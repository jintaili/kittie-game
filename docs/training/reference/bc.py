"""Weighted BC epoch extracted from the two supervised training stages.

The caller supplies the actor, tokenized training rows and optimizer. Model
loading, validation, checkpointing and dataset distribution are separate work.
"""
from __future__ import annotations

import random
from typing import Literal

import torch
import torch.nn.functional as F

from .bc_data import batch_order


def train_epoch(
    actor: torch.nn.Module,
    rows: list[dict],
    optimizer: torch.optim.Optimizer,
    rng: random.Random,
    *,
    effective_batch: int = 32,
    microbatch: int = 1,
    max_grad_norm: float = 1.0,
    loss_denominator: Literal["actual_batch", "effective_batch"] = "effective_batch",
) -> list[dict]:
    """Perform one pass, visiting each supplied training decision once.

    Courtyard BC divides each step's weighted loss by its actual batch length.
    Multi-level BC uses the configured effective batch, including its short last
    batch. Existing per-row weights must be retained, not recomputed by batch.
    """
    if not rows or effective_batch < 1 or not 1 <= microbatch <= effective_batch:
        raise ValueError("Expected training rows and valid batch sizes")
    if loss_denominator not in ("actual_batch", "effective_batch"):
        raise ValueError("Unknown supervised loss denominator")
    if any(r.get("split") != "train" for r in rows):
        raise ValueError("BC updates require explicitly assigned training rows")
    params = [p for p in actor.parameters() if p.requires_grad]
    if not params:
        raise ValueError("No trainable parameters")
    device = params[0].device
    actor.train()
    records = []
    for batch in batch_order(rows, rng, effective_batch):
        optimizer.zero_grad(set_to_none=True)
        denominator = len(batch) if loss_denominator == "actual_batch" else effective_batch
        total = 0.0
        for offset in range(0, len(batch), microbatch):
            part = batch[offset:offset + microbatch]
            logs = actor([r["ids"] for r in part], [r["facing"] for r in part])
            targets = torch.tensor([r["target"] for r in part], device=device)
            weights = torch.tensor([r["weight"] for r in part], device=device)
            loss = (F.nll_loss(logs, targets, reduction="none") * weights).sum() / denominator
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite BC loss")
            loss.backward()
            total += float(loss.detach())
        norm = torch.nn.utils.clip_grad_norm_(params, max_grad_norm, error_if_nonfinite=True)
        optimizer.step()
        if not all(torch.isfinite(p).all() for p in params):
            raise ValueError("Nonfinite parameter after BC update")
        records.append({"examples": len(batch), "weighted_ce": total, "gradient_norm": float(norm)})
    return records
