"""Composite propagation-risk score for worm containment.

score(v) = alpha * urgency(v) + beta * centrality(v) + gamma * reach(v)
where alpha + beta + gamma = 1 and each component lies in [0, 1].

urgency(v)   = exp(-dist(v) / tau)   (distance to nearest infected node)
centrality(v)= degree(v) / max degree
reach(v)     = susceptible nodes within 2 hops (excluding v) / total susceptible
"""

import math
from collections import deque


def urgency(distance, tau):
    """Proximity urgency; a node closer to the infection is more urgent."""
    return math.exp(-distance / tau)


def distances_to_infected(graph, infected):
    """Shortest-path distance from every node to the nearest infected node."""
    distances = {node: 0 for node in infected if node in graph}
    queue = deque(distances)
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, ()):
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
    return distances


def centrality(graph, v):
    """Degree of v normalized by the maximum degree in the graph."""
    if not graph:
        return 0.0
    max_deg = max(len(graph.get(u, ())) for u in graph)
    if max_deg == 0:
        return 0.0
    return len(graph.get(v, ())) / max_deg


def reach(graph, v, infected):
    """Fraction of susceptible nodes within 2 hops of v (v excluded)."""
    susceptible = set(graph) - set(infected)
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


def _score(graph, v, infected, distances, tau, alpha, beta, gamma):
    """Combine urgency, centrality, and reach into a single risk score."""
    return (
        alpha * urgency(distances.get(v, float("inf")), tau)
        + beta * centrality(graph, v)
        + gamma * reach(graph, v, infected)
    )


def risk_score(graph, v, infected, tau=1.0, alpha=0.4, beta=0.35, gamma=0.25):
    """Composite risk score for node v given the current infected set."""
    return _score(
        graph, v, infected, distances_to_infected(graph, infected),
        tau, alpha, beta, gamma,
    )


def score_all(graph, infected, tau=1.0, alpha=0.4, beta=0.35, gamma=0.25):
    """Score every node in the graph, computing infection distances once."""
    distances = distances_to_infected(graph, infected)
    return {
        v: _score(graph, v, infected, distances, tau, alpha, beta, gamma)
        for v in graph
    }
