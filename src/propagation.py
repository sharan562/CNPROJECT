"""Discrete-time worm propagation over an adjacency-dict graph.

Graph representation: {node: set(neighbors)}.
"""


def simulate_step(graph, infected, beta, rng):
    """Advance one discrete time step.

    Each infected node attempts to infect each susceptible neighbour with
    probability ``beta``. Returns the set of newly infected nodes.
    """
    newly = set()
    for v in sorted(infected, key=str):
        for u in sorted(graph.get(v, ()), key=str):
            if u not in infected and u not in newly and rng.random() < beta:
                newly.add(u)
    return newly


def propagate(graph, seeds, beta, rng):
    """Run the outbreak to completion.

    Returns (arrival_times, infected): arrival_times maps each infected node to
    the step at which it was first infected (seeds are step 0); infected is the
    set of all nodes that ever became infected.
    """
    infected = set(seeds)
    arrival = {s: 0 for s in seeds}
    step = 0
    while True:
        newly = simulate_step(graph, infected, beta, rng)
        if not newly:
            break
        step += 1
        for n in newly:
            arrival[n] = step
        infected |= newly
    return arrival, infected
