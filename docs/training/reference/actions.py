"""Factorized readout to 18 joint action probabilities."""
import torch
import torch.nn.functional as F

def log_probabilities(logits: torch.Tensor, facings: torch.Tensor) -> torch.Tensor:
    if logits.ndim != 2 or logits.shape[1] != 12:
        raise ValueError('Expected [batch, 12] readout logits')
    if facings.shape != (len(logits),) or not torch.all((facings == 0) | (facings == 1)):
        raise ValueError('Expected one left/right facing per row')
    motion = F.log_softmax(logits[:, :6].float(), dim=-1)
    throws = F.log_softmax(logits[:, 6:].float().reshape(-1, 2, 3), dim=-1)
    directions = torch.stack((facings, facings, torch.zeros_like(facings), torch.zeros_like(facings),
                              torch.ones_like(facings), torch.ones_like(facings)), dim=1)
    conditional = throws[torch.arange(len(logits), device=logits.device)[:, None], directions]
    return (motion[:, :, None] + conditional).reshape(-1, 18)
