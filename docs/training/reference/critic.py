"""Detached critic used by Head Goon PPO."""
import torch
from torch import nn

class Standardize(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.register_buffer('mean', torch.zeros(dim))
        self.register_buffer('std', torch.ones(dim))
    def forward(self, x):
        return (x-self.mean)/self.std
    @torch.no_grad()
    def calibrate(self, x):
        self.mean.copy_(x.mean(0)); self.std.copy_(x.std(0,unbiased=False).clamp_min(.01))


def make_critic(dim, normalization):
    norm = nn.LayerNorm(dim) if normalization=='layernorm' else Standardize(dim)
    model=nn.Sequential(norm,nn.Linear(dim,128),nn.Tanh(),nn.Linear(128,1))
    nn.init.zeros_(model[-1].weight);nn.init.zeros_(model[-1].bias)
    return model
