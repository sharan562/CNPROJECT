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
    """Quarantine the susceptible node nearest to the observed infection.

    This real-time baseline uses graph distance to the current infected set;
    it never simulates a future outbreak to select a quarantine target.
    """
    g = {u: set(v) for u, v in graph.items()}
    infected = set(seeds)
    plan = []

    while len(plan) < K:
        newly = simulate_step(g, infected, beta, rng)
        if not newly:
            break
        infected |= newly

        susceptible = set(g) - infected
        if not susceptible:
            break

        node = min(
            susceptible,
            key=lambda candidate: _distance_to_infected(g, candidate, infected),
        )
        g = quarantine(g, node)
        plan.append(node)

    _, infected = propagate(g, infected, beta, rng)

    return {
        "plan": plan,
        "infected_count": len(infected)
    }


def _distance_to_infected(graph, start, infected):
    """Return the shortest-path distance from ``start`` to any infected node."""
    frontier = {start}
    visited = {start}
    distance = 0

    while frontier:
        if frontier & infected:
            return distance
        frontier = {
            neighbor
            for node in frontier
            for neighbor in graph.get(node, ())
            if neighbor not in visited
        }
        visited |= frontier
        distance += 1

    return float("inf")
