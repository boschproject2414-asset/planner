from collections import defaultdict, deque
from datetime import date, timedelta


class CycleError(Exception):
    pass


def topo(nodes: list[int], edges: list[tuple[int, int]]) -> list[int]:
    indeg = {n: 0 for n in nodes}
    g: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        g[u].append(v)
        indeg[v] += 1
    q = deque([n for n, d in indeg.items() if d == 0])
    out: list[int] = []
    while q:
        n = q.popleft()
        out.append(n)
        for m in g[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)
    if len(out) != len(nodes):
        raise CycleError("Dependency cycle detected")
    return out


def recalc_forecast(
    activities: dict[int, dict],
    deps: list[tuple[int, int]],
    project_start: date,
) -> dict[int, tuple[date, date]]:
    order = topo(list(activities.keys()), deps)
    preds: dict[int, list[int]] = defaultdict(list)
    for u, v in deps:
        preds[v].append(u)

    result: dict[int, tuple[date, date]] = {}
    for aid in order:
        row = activities[aid]
        duration = max(int(row.get("duration_days", 1)), 1)
        start = row.get("planned_start") or project_start
        if preds[aid]:
            pred_finish = max(result[p][1] for p in preds[aid])
            start = max(start, pred_finish)
        finish = start + timedelta(days=duration)
        result[aid] = (start, finish)
    return result
