"""Reference scheduling semantics, independent of model/provider/emulator.

Frame indices use the emulator clock. Call the controller while the emulator
continues stepping with its currently held buttons. This reference is not a
replacement for the study's retained native control loop.
"""
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class Timing:
    post_action_frames: int = 6
    delay_mode: Literal['measured', 'floor'] = 'measured'
    # Supplied per-request input, not estimated from the current game's future.
    delay_frames: tuple[int, ...] = ()

    def __post_init__(self):
        if self.post_action_frames < 0:raise ValueError('Negative interval')
        if self.delay_mode not in ('measured','floor'):raise ValueError('Unknown delay mode')
        if any(x < 0 for x in self.delay_frames):raise ValueError('Negative delay')
        if self.delay_mode=='floor' and not self.delay_frames:raise ValueError('Supply delay frames')

class SingleRequest:
    def __init__(self, timing: Timing):
        self.timing=timing;self.next_observation=0;self.request_frame=None
        self.reply_frame=None;self.target_frame=None;self.requests=0;self.ended=False

    def observe(self, frame: int)->None:
        if self.ended or self.request_frame is not None:raise ValueError('Request cannot overlap or follow termination')
        if frame < self.next_observation:raise ValueError('Post-action interval incomplete')
        target=frame
        if self.timing.delay_mode=='floor':
            if self.requests>=len(self.timing.delay_frames):raise ValueError('Delay input exhausted')
            target+=self.timing.delay_frames[self.requests]
        self.request_frame=frame;self.target_frame=target;self.requests+=1

    def reply(self, frame: int)->None:
        if self.request_frame is None or self.reply_frame is not None:raise ValueError('No outstanding request')
        if frame<self.request_frame:raise ValueError('Reply predates observation')
        self.reply_frame=frame

    def ready(self, frame: int)->bool:
        return (not self.ended and self.reply_frame is not None
                and frame>=max(self.reply_frame,self.target_frame))

    def apply(self, frame: int)->dict:
        if not self.ready(frame):raise ValueError('Reply not ready or game ended')
        # Native integrations call at each frame boundary. They record any polling lag.
        row={'request_frame':self.request_frame,'reply_frame':self.reply_frame,
             'target_frame':self.target_frame,'apply_frame':frame,
             'actual_delay_frames':frame-self.request_frame}
        self.request_frame=None;self.reply_frame=None;self.target_frame=None
        self.next_observation=frame+self.timing.post_action_frames
        return row

    def finish(self)->None:
        # Outstanding responses remain loggable through reply(), but cannot apply.
        self.ended=True
