from dataclasses import dataclass

@dataclass(frozen=True)
class RewardConfig:
    completion: float = 100.0
    progress_budget: float = 10.0
    bell: float = 5.0
    goon: float = 2.0
    boss_hit: float = 5.0
    damage: float = -4.0
    death: float = -30.0
    timeout: float = -5.0
    second: float = -0.1
    completion_heart: float = 2.0
    completion_ball: float = 2.0
