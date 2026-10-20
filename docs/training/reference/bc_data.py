"""Multi-level trajectory weighting and no-replacement epoch ordering."""
import collections
import math

def weighted_rows(rows: list[dict]) -> tuple[list[dict], dict[str, float]]:
    selected = [dict(r) for r in rows if r['split'] == 'train']
    sizes = collections.Counter(r['run'] for r in selected)
    runs = collections.defaultdict(set)
    for row in selected:
        runs[row['stage']].add(row['run'])
    total = sum(math.sqrt(len(group)) for group in runs.values())
    mass = {stage: math.sqrt(len(group))/total for stage, group in runs.items()}
    for row in selected:
        row['weight'] = len(selected)*mass[row['stage']]/(len(runs[row['stage']])*sizes[row['run']])
    return selected, mass


def batch_order(rows: list[dict], rng, batch_size: int) -> list[list[dict]]:
    # Every decision once. Length buckets reduce padding; no replacement sampling.
    ordered = sorted(rows, key=lambda r: len(r['ids']))
    batches = [ordered[i:i+batch_size] for i in range(0, len(ordered), batch_size)]
    for batch in batches:
        rng.shuffle(batch)
    rng.shuffle(batches)
    return batches
