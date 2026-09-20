import random

from src.propagation import simulate_step
from src.propagation import propagate


def run_no_containment(graph, seeds, beta, rng):
    """Run the outbreak without any containment."""

    arrival, infected = propagate(
        graph,
        seeds,
        beta,
        rng
    )

    return {
        "plan": [],
        "infected_count": len(infected)
    }


def quarantine(graph, node):
    """Remove a node and its connections from the graph."""

    return {
        u: {v for v in neighbors if v != node}
        for u, neighbors in graph.items()
        if u != node
    }


def run_random_quarantine(graph, seeds, beta, K, rng):
    """Randomly quarantine susceptible nodes."""

    g = {u: set(v) for u, v in graph.items()}
    infected = set(seeds)
    plan = []

    while len(plan) < K:

        newly = simulate_step(
            g,
            infected,
            beta,
            rng
        )

        if not newly:
            break

        infected |= newly

        susceptible = set(g) - infected

        if not susceptible:
            break

        node = rng.choice(list(susceptible))

        g = quarantine(g, node)
        plan.append(node)

    return {
        "plan": plan,
        "infected_count": len(infected)
    }


def run_degree_quarantine(graph, seeds, beta, K, rng):
    """Quarantine the susceptible node with the highest degree."""

    g = {u: set(v) for u, v in graph.items()}
    infected = set(seeds)
    plan = []

    while len(plan) < K:

        newly = simulate_step(
            g,
            infected,
            beta,
            rng
        )

        if not newly:
            break

        infected |= newly

        susceptible = set(g) - infected

        if not susceptible:
            break

        node = max(
            susceptible,
            key=lambda v: len(g[v])
        )

        g = quarantine(g, node)
        plan.append(node)

    return {
        "plan": plan,
        "infected_count": len(infected)
    }


def run_earliest_infection(graph, seeds, beta, K, rng):
    """Quarantine nodes based on their infection arrival order."""

    arrival, _ = propagate(
        graph,
        seeds,
        beta,
        rng
    )

    candidates = [
        node for node in graph
        if node not in seeds
    ]

    candidates.sort(
        key=lambda node: arrival.get(node, float("inf"))
    )

    plan = candidates[:K]

    g = {u: set(v) for u, v in graph.items()}

    for node in plan:
        g = quarantine(g, node)

    _, infected = propagate(
        g,
        seeds,
        beta,
        rng
    )

    return {
        "plan": plan,
        "infected_count": len(infected)
    }