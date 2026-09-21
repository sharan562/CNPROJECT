"""Budget-constrained greedy containment optimizer.

Interleaves one spread step with one quarantine action, so the operator is
modeled as responding to the outbreak in near-real-time. Quarantining removes a
node and its incident edges, so it can neither be infected nor spread further.
"""

import random

from src.propagation import simulate_step
from src.risk_score import score_all


def quarantine(graph, v):
    """Return a copy of ``graph`` with node ``v`` and its incident edges removed."""
    return {
        u: {n for n in nbs if n != v}
        for u, nbs in graph.items()
        if u != v
    }


def contain(graph, seeds, beta, K, tau=1.0, alpha=0.4, beta_centrality=0.35, gamma=0.25, eps=0.0, rng=None, return_history=False):
    """Run the outbreak to completion, quarantining the highest-risk susceptible
    node after each spread step while the budget ``K`` lasts and the per-step
    growth exceeds ``eps``.

    Returns ``(plan, infected_count)``: ``plan`` is the ordered list of
    quarantined nodes; ``infected_count`` is the final number of infected nodes.
    """
    if rng is None:
        rng = random.Random()
    g = {u: set(nbs) for u, nbs in graph.items()}
    infected = set(seeds)
    plan = []
    history = [len(infected)]

    while True:
        newly = simulate_step(g, infected, beta, rng)
        if not newly:
            break
        infected |= newly
        history.append(len(infected))

        if len(plan) < K and len(newly) > eps:
            susceptible = set(g) - infected
            if susceptible:
                scores = score_all(g, infected, tau, alpha, beta_centrality, gamma)
                v = max(susceptible, key=lambda node: (scores[node], str(node)))
                g = quarantine(g, v)
                plan.append(v)

    if return_history:
        return plan, len(infected), history
    return plan, len(infected)
