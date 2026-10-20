"""One causal input builder for archived teacher requests and live serving."""
from __future__ import annotations

import copy
import json
import re
from typing import Any

VERSION = 'qwen-all-levels-bc-request-v1'
STAGES = ('courtyard', 'grove', 'villa', 'banquet', 'head_goon')
MOTIONS = tuple(f'{direction}_{control}' for direction in ('neutral', 'left', 'right')
                for control in ('release_a', 'hold_a'))
THROWS = ('none', 'flat', 'lob')
NAMES = tuple(f'{motion}_{throw}' for motion in MOTIONS for throw in THROWS)
OPTIONS = {name: ([] if name.startswith('neutral_') else [name.split('_')[0]])
           + (['a'] if '_hold_a_' in name else [])
           + ([] if name.endswith('_none') else ['b'] + (['up'] if name.endswith('_lob') else []))
           for name in NAMES}
READOUT_LABELS = 'ABCDEFGHIJKL'
SYSTEM = '''The observation describes the instant the request is made. Old held buttons continue during the estimated response delay. Derived forecasts are predictions, not future observations. Use the recorded stage mechanics, geometry, questions, history and shot feedback.
Choose movement and A control together, then choose throwing for the resulting facing. Neutral movement keeps the observed facing. release_a releases A; hold_a holds A. Holding A does not guarantee a new jump. Only fresh A/B presses trigger jumps/throws. None releases B and Up; flat holds B; lob holds B and Up. Each applied action holds for at least six frames.
The classifier uses three separate choice groups, all evaluated from this same observation:
Movement: A=neutral_release_a; B=neutral_hold_a; C=left_release_a; D=left_hold_a; E=right_release_a; F=right_hold_a.
Throw if facing left: G=none; H=flat; I=lob.
Throw if facing right: J=none; K=flat; L=lob.
Only the throw group for the selected movement's resulting facing is applied.'''
ALIASES = {f'{d}_{old}': f'{d}_{new}' for d in ('neutral', 'left', 'right')
           for old, new in (('ground', 'release_a'), ('jump', 'hold_a'))}
KEYS = {'wool_held': 'balls_held', 'world_wool': 'world_balls',
        'possible_wool_pickups': 'possible_ball_pickups', 'wool': 'balls'}


def canonical_action(action: str) -> str:
    value = normalize(action)
    if value not in OPTIONS:
        raise ValueError(f'Unknown physical action: {action}')
    return value


def normalize(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            new = normalize(key)
            if new in result:
                raise ValueError('Alias collision in input')
            result[new] = normalize(item)
        return result
    if isinstance(value, list):
        return [normalize(item) for item in value]
    if not isinstance(value, str):
        return value
    if value in KEYS:
        return KEYS[value]
    for old, new in KEYS.items():
        value = value.replace(old, new)
    value = re.sub(r'\bwool\b', 'ball', value, flags=re.I)
    for old, new in ALIASES.items():
        value = value.replace(old, new)
    # The first all-level version corrupted singular/plural wording only.
    for old, new in {'physical balls ball': 'physical ball', 'three balls hits': 'three ball hits',
                     'balls rings': 'balls ring', 'No balls is carried.': 'No ball is carried.',
                     'Moving-balls pickup': 'Moving-ball pickup'}.items():
        value = value.replace(old, new)
    return value


def pack(value: Any) -> Any:
    """Lossless column representation, matching the parent's compact input style."""
    if isinstance(value, dict):
        return {k: pack(v) for k, v in value.items()}
    if isinstance(value, list):
        if len(value) > 1 and all(isinstance(v, dict) and list(v) == list(value[0]) for v in value):
            keys = list(value[0])
            return {'columns': keys, 'rows': [[pack(v[k]) for k in keys] for v in value]}
        return [pack(v) for v in value]
    return value


def unpack(value: Any) -> Any:
    if isinstance(value, dict):
        if set(value) == {'columns', 'rows'}:
            return [{k: unpack(v) for k, v in zip(value['columns'], row)} for row in value['rows']]
        return {k: unpack(v) for k, v in value.items()}
    if isinstance(value, list):
        return [unpack(v) for v in value]
    return value


def build_input(wire: dict, stage: str) -> str:
    """No labels, outcomes, measured future latency or metadata enter this function."""
    if stage not in STAGES:
        raise ValueError(stage)
    state = wire['state']
    state = json.loads(state) if isinstance(state, str) else copy.deepcopy(state)
    if state.get('stage', stage) != stage:
        raise ValueError('Recorded stage differs')
    state.pop('contract_version', None)
    state['stage'] = stage
    state['input_version'] = VERSION
    questions = copy.deepcopy(wire['questions'])
    feedback = []
    for direction in ('left', 'right'):
        instructions = questions['throw_' + direction]['instructions']
        if isinstance(instructions, dict):
            feedback.append(instructions['shot_feedback'])
            questions['throw_' + direction]['instructions'] = instructions['question']
    if len(feedback) != 2 or feedback[0] != feedback[1]:
        raise ValueError('Expected matching causal shot feedback for both facings')
    state['shot_feedback'] = feedback[0]
    state['questions'] = questions
    result = normalize(state)
    if tuple(result['questions']['motion']['criteria']) != MOTIONS:
        raise ValueError('Movement classifier order changed')
    if tuple(result['derived']['motion_forecasts']) != MOTIONS:
        raise ValueError('Forecast action meanings changed')
    for direction in ('left', 'right'):
        if tuple(result['questions']['throw_' + direction]['criteria']) != THROWS:
            raise ValueError('Throw order changed')
    if stage == 'head_goon' and not all(k in result['observed']['boss'] for k in ('health', 'phase')):
        raise ValueError('Missing Head Goon observation')
    return json.dumps(pack(result), separators=(',', ':'), ensure_ascii=True)


def messages(prompt: str) -> list[dict[str, str]]:
    value = json.loads(prompt)
    if value.get('input_version') != VERSION or value.get('stage') not in STAGES:
        raise ValueError('Wrong serving input version')
    if re.search(r'\bwool\b|wool_|_wool|_(?:ground|jump)(?:_|\b)', prompt, re.I):
        raise ValueError('Unnormalized model input')
    return [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': prompt}]


def facing(prompt: str) -> int:
    value = json.loads(prompt)['observed']['player']['facing']
    if value not in ('left', 'right'):
        raise ValueError('Invalid facing')
    return int(value == 'right')
