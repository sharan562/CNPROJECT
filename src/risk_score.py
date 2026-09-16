"""Composite propagation-risk score for worm containment.

score(v) = alpha * urgency(v) + beta * centrality(v) + gamma * reach(v)
where alpha + beta + gamma = 1 and each component lies in [0, 1].

urgency(v)   = exp(-t[v] / tau)     (0 for never-infected nodes)
centrality(v)= degree(v) / max degree
reach(v)     = susceptible nodes within 2 hops (excluding v) / total susceptible
"""

import math


def urgency(t, tau):
    """Time-decayed urgency; earlier infection (smaller t) is more urgent."""
    return math.exp(-t / tau)


def centrality(graph, v):
    """Degree of v normalized by the maximum degree in the graph."""
    if not graph:
        return 0.0
    max_deg = max(len(graph.get(u, ())) for u in graph)
    if max_deg == 0:
        return 0.0
    return len(graph.get(v, ())) / max_deg


def reach(graph, v, arrival):
    """Fraction of susceptible nodes within 2 hops of v (v excluded)."""
    susceptible = set(graph) - set(arrival)
    if not susceptible:
        return 0.0

    seen = {v}
    frontier = {v}
    for _ in range(2):
        nxt = set()
        for node in frontier:
            for nb in graph.get(node, ()):
                if nb not in seen:
                    seen.add(nb)
                    nxt.add(nb)
        frontier = nxt

    reachable = seen & susceptible
    reachable.discard(v)
    return len(reachable) / len(susceptible)


def risk_score(graph, v, arrival, tau=5.0, alpha=0.4, beta=0.35, gamma=0.25):
    """Composite risk score for node v given current infection state."""
    t = arrival.get(v, float("inf"))
    return (
        alpha * urgency(t, tau)
        + beta * centrality(graph, v)
        + gamma * reach(graph, v, arrival)
    )


def score_all(graph, arrival, tau=5.0, alpha=0.4, beta=0.35, gamma=0.25):
    """Score every node in the graph."""
    return {
        v: risk_score(graph, v, arrival, tau, alpha, beta, gamma) for v in graph
    }
