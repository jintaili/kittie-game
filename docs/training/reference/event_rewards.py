from __future__ import annotations

from dataclasses import dataclass
from .reward_config import RewardConfig

FPS = 4194304 / 70224


@dataclass(frozen=True)
class RewardState:
    x: float
    grounded: bool
    hearts: int
    balls: int
    gates: int
    defeats: int
    boss_health: int
    dead: bool = False
    won: bool = False


class RewardTracker:
    """Bounded event rewards. Native score never enters this calculation."""

    def __init__(self, initial: RewardState, width: int, boss: bool, config: RewardConfig):
        self.config, self.width, self.boss = config, width, boss
        self.start_x = self.best_x = initial.x
        self.gates = initial.gates
        self.defeats = initial.defeats
        self.boss_health = initial.boss_health
        self.last = initial
        self.finished = False
        self.total: dict[str, float] = {}

    def update(self, state: RewardState, frames: int, *, timeout: bool = False) -> dict[str, float]:
        if self.finished:
            raise RuntimeError("Reward requested after episode ended")
        if frames < 0:
            raise ValueError("Negative frame count")
        c = self.config
        terms: dict[str, float] = {"time": c.second * frames / FPS}
        # Award distance only on an observed safe landing. Revisit/rebound cannot farm it.
        if state.grounded and not state.dead and not self.boss:
            current = min(max(state.x, self.best_x), self.width - 40)
            terms["progress"] = c.progress_budget * (current - self.best_x) / max(1, self.width - 40 - self.start_x)
            self.best_x = current
        if not self.boss:
            new_gates = state.gates & ~self.gates
            terms["bells"] = c.bell * new_gates.bit_count()
            self.gates |= state.gates
            new_defeats = max(0, min(3, state.defeats) - self.defeats)
            terms["goons"] = c.goon * new_defeats
            self.defeats = max(self.defeats, min(3, state.defeats))
        else:
            terms["boss_hits"] = c.boss_hit * max(0, self.boss_health - state.boss_health)
            if state.boss_health == 0 and self.boss_health > 0:
                terms["goons"] = c.goon
            self.boss_health = min(self.boss_health, state.boss_health)
        terms["damage"] = c.damage * max(0, self.last.hearts - state.hearts)
        if state.dead:
            terms["death"] = c.death
            self.finished = True
        elif state.won:
            terms["completion"] = c.completion
            terms["completion_hearts"] = c.completion_heart * state.hearts
            terms["completion_balls"] = c.completion_ball * state.balls
            self.finished = True
        elif timeout:
            terms["timeout"] = c.timeout
            self.finished = True
        self.last = state
        for name, value in terms.items():
            self.total[name] = self.total.get(name, 0.0) + value
        return terms

    def state_dict(self) -> dict:
        from dataclasses import asdict
        return {"start_x": self.start_x, "best_x": self.best_x, "gates": self.gates,
                "defeats": self.defeats, "boss_health": self.boss_health,
                "last": asdict(self.last), "finished": self.finished, "total": self.total}

    def load_state_dict(self, data: dict) -> None:
        for name in ("start_x", "best_x", "gates", "defeats", "boss_health", "finished", "total"):
            setattr(self, name, data[name])
        self.last = RewardState(**data["last"])
