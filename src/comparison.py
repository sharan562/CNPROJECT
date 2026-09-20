import random
import json
from pathlib import Path

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
RNG_SEED = 42
RESULTS_DIR = Path("results")


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


def run_comparison(graph, seeds=SEEDS, beta=BETA, budget=K, rng_seed=RNG_SEED):
    """Run every containment strategy under the same reproducible conditions."""
    rng = random.Random(rng_seed)
    no_containment = run_no_containment(graph, seeds, beta, rng)

    rng = random.Random(rng_seed)
    random_result = run_random_quarantine(graph, seeds, beta, budget, rng)

    rng = random.Random(rng_seed)
    degree_result = run_degree_quarantine(graph, seeds, beta, budget, rng)

    rng = random.Random(rng_seed)
    earliest_result = run_earliest_infection(graph, seeds, beta, budget, rng)

    rng = random.Random(rng_seed)
    proposed_result = run_proposed(graph, seeds, beta, budget, rng)

    results = {
        "No Containment": no_containment["infected_count"],
        "Random": random_result["infected_count"],
        "Degree": degree_result["infected_count"],
        "Earliest Infection": earliest_result["infected_count"],
        "Proposed": proposed_result["infected_count"],
    }
    plans = {
        "Random": random_result["plan"],
        "Degree": degree_result["plan"],
        "Earliest Infection": earliest_result["plan"],
        "Proposed": proposed_result["plan"],
    }
    return results, plans, no_containment["infected"]


def save_artifacts(graph, results, plans, baseline_infected):
    """Write figures and a JSON summary for the demonstration and report."""
    from src.visualize import plot_comparison, plot_network

    RESULTS_DIR.mkdir(exist_ok=True)
    plot_comparison(results, RESULTS_DIR / "strategy_comparison.png")
    plot_network(
        graph,
        infected=baseline_infected,
        quarantined=plans["Proposed"],
        output_path=RESULTS_DIR / "network_topology.png",
    )
    summary = {
        "configuration": {
            "seeds": SEEDS,
            "transmission_probability": BETA,
            "quarantine_budget": K,
            "random_seed": RNG_SEED,
        },
        "final_infected_counts": results,
        "quarantine_plans": plans,
    }
    with (RESULTS_DIR / "comparison_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)


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

    results, plans, baseline_infected = run_comparison(graph)
    save_artifacts(graph, results, plans, baseline_infected)

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

    for strategy, plan in plans.items():
        print(strategy + ":", plan)

    # -------------------------------
    # Infection Reduction
    # -------------------------------

    baseline = results["No Containment"]

    print("\n--- Infections Prevented ---")

    for strategy, count in results.items():

        reduction = baseline - count

        print(
            strategy,
            "->",
            reduction,
            "infections prevented"
        )

    print("\nSaved results to:", RESULTS_DIR)
