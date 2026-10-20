"""Episode-level metrics with fixed definitions and no policy feedback."""
from __future__ import annotations
from collections import Counter
from .event_rewards import RewardTracker, RewardState, FPS
from .reward_config import RewardConfig


def state(raw: dict) -> RewardState:
    return RewardState(raw['kittie_x']/16, bool(raw['kittie_ground']), raw['kittie_health'],
        raw['kittie_inventory'], raw['kittie_gate'], raw['courtyard_defeated'], raw['boss_health'],
        bool(raw['kittie_dead'] or not raw['kittie_health']), bool(raw['kittie_won']))


class EpisodeMetrics:
    def __init__(self, raw: dict, width: int, boss: bool):
        self.width, self.boss = width, boss
        self.reward = RewardTracker(state(raw), width, boss, RewardConfig())
        self.initial = dict(raw); self.previous = dict(raw)
        self.cells = Counter(); self.route = []; self.milestones = []
        self.last_improvement_frame = 0; self.stall_frames = 0; self.damage = 0
        self.recovery_pending = None; self.recoveries = 0; self.damage_events = 0
        self.sample(raw, 0)

    def sample(self, raw: dict, frame: int):
        cell = (int(raw['kittie_x']/16//64), int(raw['kittie_y']/16//32))
        self.cells[cell] += 1
        if not self.route or tuple(self.route[-1]) != cell:
            self.route.append(list(cell))
        if frame == 0:
            return {}
        before = self.reward.best_x
        terms = self.reward.update(state(raw), 1)
        gained = self.reward.best_x > before or any(terms.get(k, 0) > 0 for k in ('bells','goons','boss_hits','completion'))
        if gained:
            self.last_improvement_frame = frame
        if frame-self.last_improvement_frame >= 5*FPS:
            self.stall_frames += 1
        progress = self.progress()
        for threshold in (.25,.5,.75,1.):
            name = 'progress_'+str(threshold)
            if not self.boss and progress >= threshold and not any(e['name']==name for e in self.milestones):
                self.milestones.append({'frame':frame,'name':name})
        for name in ('bells','goons','boss_hits','completion'):
            if terms.get(name,0)>0:
                self.milestones.append({'frame':frame,'name':name,'reward':terms[name]})
        damage = max(0, self.previous['kittie_health']-raw['kittie_health'])
        if damage:
            self.damage += damage; self.damage_events += 1
            self.recovery_pending = (frame, self.reward.best_x, raw['boss_health'])
        elif self.recovery_pending and not state(raw).dead:
            start,x,bh = self.recovery_pending
            if frame-start >= FPS and (self.reward.best_x >= x+64 or raw['boss_health'] < bh or state(raw).won):
                self.recoveries += 1; self.recovery_pending = None
        self.previous = dict(raw)
        return terms

    def progress(self):
        if self.boss:
            return (self.initial['boss_health']-self.reward.boss_health)/max(1,self.initial['boss_health'])
        return min(1.,max(0.,(self.reward.best_x-self.reward.start_x)/max(1,self.width-40-self.reward.start_x)))

    def finish(self, raw: dict, frame: int, outcome: str):
        if not self.reward.finished:
            self.reward.update(state(raw),0,timeout=outcome in ('wall_time_limit','frame_limit'))
        result = {'reward_components':self.reward.total, 'reward_total':sum(self.reward.total.values()),
            'meaningful_reward':any(self.reward.total.get(k,0)>0 for k in ('bells','goons','boss_hits','completion')),
            'progress_reward_observed':self.reward.total.get('progress',0)>0,
            'normalized_progress':self.progress(), 'milestones':self.milestones,
            'spatial_cells_visited':len(self.cells),'spatial_cell_occupancy':{f'{x},{y}':n for (x,y),n in self.cells.items()},
            'route_cells':self.route,'stall_seconds':self.stall_frames/FPS,
            'damage_taken':self.damage,'damage_events':self.damage_events,'recoveries_after_damage':self.recoveries,
            'gate_bits_opened':(self.reward.gates & ~self.initial['kittie_gate']).bit_count(),
            'unique_goons_defeated':max(0,self.reward.defeats-self.initial['courtyard_defeated']) if not self.boss else int(raw['boss_health']==0),
            'native_score':raw['native_score'],
            'metric_definitions':{'progress':'safe-landing distance normalized to width minus 40; boss health reduction / initial health',
                'spatial_cell':'64 pixels horizontal by 32 vertical; occupancy includes frame zero',
                'stall':'time after 5 seconds without safe-distance or event milestone improvement; diagnostic, no termination',
                'recovery':'survive at least one second after damage then advance 64 safe pixels, hit boss, or win',
                'meaningful_reward':'bell, unique goon, boss hit or completion; distance reported separately',
                'timeout':'censored gameplay outcome; frozen rubric timeout penalty retained separately'}}
        return result
