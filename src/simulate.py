import random

from src.topology import get_adjacency_graph
from src.propagation import propagate
from src.containment import contain


BETA = 0.25
K = 2
SEEDS = ["WS_1"]


def run_no_containment(graph, seeds, beta, rng):
    """Run the outbreak without containment."""
    arrival, infected = propagate(graph, seeds, beta, rng)

    return {
        "arrival": arrival,
        "infected": infected,
        "infected_count": len(infected)
    }


def run_proposed_containment(graph, seeds, beta, K, rng):
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

    # Load bank network
    graph = get_adjacency_graph("data/bank_topology.json")

    print("\n=== BANKING MALWARE CONTAINMENT SIMULATION ===")

    print("\nNetwork:")
    print("Nodes:", len(graph))
    print("Initial infected:", SEEDS)
    print("Transmission probability:", BETA)
    print("Quarantine budget:", K)

    # -------------------------------
    # Baseline: No Containment
    # -------------------------------

    rng = random.Random(42)

    baseline = run_no_containment(
        graph,
        SEEDS,
        BETA,
        rng
    )

    print("\n--- No Containment ---")
    print("Total infected:", baseline["infected_count"])

    print("\nInfection Arrival Times:")

    for node, time in sorted(
        baseline["arrival"].items(),
        key=lambda x: x[1]
    ):
        print(node, "-> step", time)

    # -------------------------------
    # Proposed Method
    # -------------------------------

    rng = random.Random(42)

    proposed = run_proposed_containment(
        graph,
        SEEDS,
        BETA,
        K,
        rng
    )

    print("\n--- Proposed Greedy Containment ---")
    print("Quarantine plan:", proposed["plan"])
    print("Total infected:", proposed["infected_count"])

    # -------------------------------
    # Comparison
    # -------------------------------

    reduction = (
        baseline["infected_count"]
        - proposed["infected_count"]
    )

    print("\n--- Comparison ---")
    print("Baseline infected:", baseline["infected_count"])
    print("Contained infected:", proposed["infected_count"])
    print("Infections prevented:", reduction)