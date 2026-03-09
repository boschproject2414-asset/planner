from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class ActivityNode:
    id: int
    duration: float
    phase: str


class ScheduleError(Exception):
    pass


def topological_sort(nodes: dict[int, ActivityNode], edges: list[tuple[int, int]]) -> list[int]:
    indegree = {n: 0 for n in nodes}
    graph: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1

    q = deque([n for n, d in indegree.items() if d == 0])
    order: list[int] = []
    while q:
        n = q.popleft()
        order.append(n)
        for nxt in graph[n]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)

    if len(order) != len(nodes):
        raise ScheduleError("Cycle detected in dependency graph")
    return order


def compute_schedule(
    nodes: dict[int, ActivityNode],
    edges: list[tuple[int, int]],
    approved_gates: set[str],
) -> dict[str, dict[int, float] | list[int] | float]:
    order = topological_sort(nodes, edges)
    preds: dict[int, list[int]] = defaultdict(list)
    succs: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        preds[v].append(u)
        succs[u].append(v)

    es: dict[int, float] = {}
    ef: dict[int, float] = {}
    for n in order:
        gate_blocked = nodes[n].phase.lower() == "electrical" and "G2" not in approved_gates
        start = 999999.0 if gate_blocked else max((ef[p] for p in preds[n]), default=0)
        es[n] = start
        ef[n] = start + nodes[n].duration

    project_finish = max(ef.values(), default=0)
    ls: dict[int, float] = {}
    lf: dict[int, float] = {}
    for n in reversed(order):
        finish = min((ls[s] for s in succs[n]), default=project_finish)
        lf[n] = finish
        ls[n] = finish - nodes[n].duration

    tf = {n: ls[n] - es[n] for n in nodes}
    critical = [n for n, f in tf.items() if abs(f) < 1e-6]

    return {
        "ES": es,
        "EF": ef,
        "LS": ls,
        "LF": lf,
        "TF": tf,
        "critical_path": critical,
        "project_finish": project_finish,
    }
