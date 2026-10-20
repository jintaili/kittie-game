"""Boss-specific hit reward; all other historical terms remain unchanged."""
from .metrics import EpisodeMetrics as BaseMetrics


class EpisodeMetrics(BaseMetrics):
    def __init__(self,raw,width,boss):
        self.ball_history=[]
        super().__init__(raw,width,boss)

    def sample(self,raw,frame,events=()):
        terms=super().sample(raw,frame)
        if not frame: return terms
        hits=[e for e in events if e['kind']=='boss_hit']
        if len(hits)*5 != terms.get('boss_hits',0): raise ValueError('Boss hit events and native health disagree')
        if hits:
            replacement=sum(e['reward'] for e in hits)
            self.reward.total['boss_hits']+=replacement-terms['boss_hits']
            terms['boss_hits']=replacement
            for milestone in self.milestones:
                if milestone['frame']==frame and milestone['name']=='boss_hits': milestone['reward']=replacement
        self.ball_history.extend(dict(e,frame=frame) for e in events)
        return terms

    def finish(self,raw,frame,outcome):
        result=super().finish(raw,frame,outcome)
        hits=[e for e in self.ball_history if e['kind']=='boss_hit']
        result.update(ball_events=self.ball_history,throws=sum(e['kind']=='throw' for e in self.ball_history),
                      direct_hits=sum(e['bounces']==0 for e in hits),hit_bounce_counts=[e['bounces'] for e in hits],
                      reward_rubric='head-goon-bounce-v1: boss_hit=20*0.5**prior_surface_rebounds; other terms unchanged')
        return result
