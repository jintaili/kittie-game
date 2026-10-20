"""Frame-discounted GAE with complete-episode accounting."""
from collections import Counter
import numpy as np

def gae(rows, values, config):
    groups = {}
    for i, row in enumerate(rows):
        groups.setdefault(row['episode_id'], []).append(i)
    adv = np.zeros(len(rows), dtype=np.float32)
    for indices in groups.values():
        indices.sort(key=lambda i: rows[i]['decision'])
        if not rows[indices[-1]]['done']:
            raise ValueError('Actor updates require finished episodes')
        running = 0.
        for pos in reversed(range(len(indices))):
            i = indices[pos]; row = rows[i]
            if pos < len(indices)-1:
                nxt = indices[pos+1]
                if row['done'] or rows[nxt]['request_frame'] != row['end_frame']:
                    raise ValueError('Trajectory discontinuity')
                nv = float(values[nxt])
            else:
                nv = 0.
            g = config['gamma_per_frame'] ** row['frames']
            lam = config['lambda_per_20_frames'] ** (row['frames']/20)
            delta = row['reward_discounted'] + g*nv - float(values[i])
            running = delta + g*lam*running*(not row['done'])
            adv[i] = running
    return adv, adv + np.asarray(values, dtype=np.float32)


def weights(rows, stages):
    counts = Counter(r['stage'] for r in rows if r['executed'])
    if set(counts) != set(stages):
        raise ValueError('Every level needs executed actions')
    # Mean weight is 1 across all rows; nonexecuted decisions have zero actor loss.
    return np.array([len(rows)/(len(stages)*counts[r['stage']]) if r['executed'] else 0.
                     for r in rows], dtype=np.float32)


def normalize_advantages(adv, w):
    mean = np.average(adv, weights=w)
    std = np.sqrt(np.average((adv-mean)**2, weights=w))
    return (adv-mean)/max(float(std), 1e-8)
