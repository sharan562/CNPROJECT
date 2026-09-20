"""Baseline containment strategies for comparison with the proposed method."""

from src.propagation import propagate, propagate_with_history, simulate_step


def run_no_containment(graph, seeds, beta, rng):
    """Run the outbreak without any containment."""
    _, infected, history = propagate_with_history(graph, seeds, beta, rng)
    return {"plan": [], "infected": infected, "infected_count": len(infected), "history": history}


def quarantine(graph, node):
    """Return a graph with ``node`` and its incident edges removed."""
    return {u: {v for v in neighbors if v != node} for u, neighbors in graph.items() if u != node}


def run_random_quarantine(graph, seeds, beta, K, rng, selection_rng=None):
    """Randomly quarantine susceptible nodes without affecting infection draws."""
    if selection_rng is None:
        selection_rng = rng
    return _run_realtime_baseline(
        graph, seeds, beta, K, rng,
        lambda g, susceptible, infected: selection_rng.choice(sorted(susceptible, key=str)),
    )


def run_degree_quarantine(graph, seeds, beta, K, rng):
    """Quarantine the susceptible node with the highest current degree."""
    return _run_realtime_baseline(
        graph, seeds, beta, K, rng,
        lambda g, susceptible, infected: max(susceptible, key=lambda node: (len(g[node]), str(node))),
    )


def run_earliest_infection(graph, seeds, beta, K, rng):
    """Quarantine the susceptible node nearest to the observed infection."""
    return _run_realtime_baseline(
        graph, seeds, beta, K, rng,
        lambda g, susceptible, infected: min(
            susceptible,
            key=lambda node: (_distance_to_infected(g, node, infected), str(node)),
        ),
    )


def _run_realtime_baseline(graph, seeds, beta, budget, rng, choose_node):
    """Apply one action after each observed spread step until budget is exhausted."""
    g = {u: set(v) for u, v in graph.items()}
    infected, plan = set(seeds), []

    while len(plan) < budget:
        newly = simulate_step(g, infected, beta, rng)
        if not newly:
            return {"plan": plan, "infected_count": len(infected)}
        infected |= newly
        susceptible = set(g) - infected
        if not susceptible:
            return {"plan": plan, "infected_count": len(infected)}
        node = choose_node(g, susceptible, infected)
        g = quarantine(g, node)
        plan.append(node)

    # The budget is spent, so simulate the remaining outbreak exactly once.
    _, infected = propagate(g, infected, beta, rng)
    return {"plan": plan, "infected_count": len(infected)}


def _distance_to_infected(graph, start, infected):
    """Return the shortest-path distance from ``start`` to an infected node."""
    frontier, visited, distance = {start}, {start}, 0
    while frontier:
        if frontier & infected:
            return distance
        frontier = {
            neighbor for node in frontier for neighbor in graph.get(node, ())
            if neighbor not in visited
        }
        visited |= frontier
        distance += 1
    return float("inf")
