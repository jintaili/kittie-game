"""Readout scoring used for PPO and dedicated Qwen evaluations."""
import torch
from .actions import log_probabilities

def score_actor(actor, ids, facings):
    if not ids or any(not row for row in ids) or max(map(len, ids)) > actor.settings['max_prompt_tokens']:
        raise ValueError('Invalid truncation-free batch')
    device = actor.label_ids.device
    lengths = torch.tensor([len(row) for row in ids], device=device)
    width = int(lengths.max())
    tokens = torch.full((len(ids), width), actor.tokenizer.pad_token_id, device=device, dtype=torch.long)
    for i, row in enumerate(ids):
        tokens[i, :len(row)] = torch.tensor(row, device=device)
    positions = torch.arange(width, device=device).expand(len(ids), -1)
    mask = positions < lengths[:, None]
    base = actor.model.get_base_model()
    hidden = base.model(input_ids=tokens, attention_mask=mask.long(),
                        position_ids=positions, use_cache=False).last_hidden_state
    final = hidden[torch.arange(len(ids), device=device), lengths-1]
    # The frozen output head is a plain tied Linear. Only twelve readout rows
    # are needed. Float32 avoids quantizing the final classifier logits to BF16.
    if type(base.lm_head) is not torch.nn.Linear or base.lm_head.weight.requires_grad:
        raise ValueError('Expected frozen plain output head')
    weight = base.lm_head.weight.index_select(0, actor.label_ids).float()
    bias = base.lm_head.bias
    if bias is not None:
        bias = bias.index_select(0, actor.label_ids).float()
    raw = torch.nn.functional.linear(final.float(), weight, bias)
    actor.last_features = final.detach().float()
    return log_probabilities(raw, torch.tensor(facings, device=device))
