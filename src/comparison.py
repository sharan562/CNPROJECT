import random

from src.topology import get_adjacency_graph

from src.baselines import (
    run_no_containment,
    run_random_quarantine,
    run_degree_quarantine,
    run_earliest_infection
)

from src.containment import contain


BETA = 0.25
K = 2
SEEDS = ["WS_1"]


def run_proposed(graph, seeds, beta, K, rng):
    """Run the proposed risk-based greedy containment."""

    plan, infected_count = contain(
        graph,
        seeds,
        beta,
        K,
        rng=rng
    )

    return {
        "plan": plan,
        "infected_count": infected_count
    }


if __name__ == "__main__":

    # Load network
    graph = get_adjacency_graph(
        "data/bank_topology.json"
    )

    print("\n=== CONTAINMENT STRATEGY COMPARISON ===")

    print("\nNetwork nodes:", len(graph))
    print("Initial infected:", SEEDS)
    print("Transmission probability:", BETA)
    print("Quarantine budget:", K)

    # -------------------------------
    # No Containment
    # -------------------------------

    rng = random.Random(42)

    no_containment = run_no_containment(
        graph,
        SEEDS,
        BETA,
        rng
    )

    # -------------------------------
    # Random Quarantine
    # -------------------------------

    rng = random.Random(42)

    random_result = run_random_quarantine(
        graph,
        SEEDS,
        BETA,
        K,
        rng
    )

    # -------------------------------
    # Degree-Based Quarantine
    # -------------------------------

    rng = random.Random(42)

    degree_result = run_degree_quarantine(
        graph,
        SEEDS,
        BETA,
        K,
        rng
    )

    # -------------------------------
    # Earliest Infection
    # -------------------------------

    rng = random.Random(42)

    earliest_result = run_earliest_infection(
        graph,
        SEEDS,
        BETA,
        K,
        rng
    )

    # -------------------------------
    # Proposed Method
    # -------------------------------

    rng = random.Random(42)

    proposed_result = run_proposed(
        graph,
        SEEDS,
        BETA,
        K,
        rng
    )

    # -------------------------------
    # Results
    # -------------------------------

    results = {
        "No Containment": no_containment["infected_count"],
        "Random": random_result["infected_count"],
        "Degree": degree_result["infected_count"],
        "Earliest Infection": earliest_result["infected_count"],
        "Proposed": proposed_result["infected_count"]
    }

    print("\n--- Final Infection Counts ---")

    for strategy, count in results.items():
        print(
            strategy,
            "->",
            count,
            "infected"
        )

    # -------------------------------
    # Quarantine Plans
    # -------------------------------

    print("\n--- Quarantine Plans ---")

    print(
        "Random:",
        random_result["plan"]
    )

    print(
        "Degree:",
        degree_result["plan"]
    )

    print(
        "Earliest:",
        earliest_result["plan"]
    )

    print(
        "Proposed:",
        proposed_result["plan"]
    )

    # -------------------------------
    # Infection Reduction
    # -------------------------------

    baseline = no_containment["infected_count"]

    print("\n--- Infections Prevented ---")

    for strategy, count in results.items():

        reduction = baseline - count

        print(
            strategy,
            "->",
            reduction,
            "infections prevented"
        )
