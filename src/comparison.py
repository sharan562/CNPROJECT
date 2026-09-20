import random
import json
import math
import statistics
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
TRIAL_COUNT = 30
RESULTS_DIR = Path("results")


def run_proposed(graph, seeds, beta, K, rng):
    """Run the proposed risk-based greedy containment."""

    plan, infected_count, history = contain(
        graph,
        seeds,
        beta,
        K,
        rng=rng,
        return_history=True,
    )

    return {
        "plan": plan,
        "infected_count": infected_count,
        "history": history,
    }


def run_comparison(graph, seeds=SEEDS, beta=BETA, budget=K, rng_seed=RNG_SEED):
    """Run every containment strategy under the same reproducible conditions."""
    rng = random.Random(rng_seed)
    no_containment = run_no_containment(graph, seeds, beta, rng)

    rng = random.Random(rng_seed)
    random_result = run_random_quarantine(
        graph,
        seeds,
        beta,
        budget,
        rng,
        selection_rng=random.Random(rng_seed + 10_000),
    )

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
    histories = {
        "No Containment": no_containment["history"],
        "Proposed": proposed_result["history"],
    }
    return results, plans, histories, no_containment["infected"]


def run_trials(graph, trial_count=TRIAL_COUNT, start_seed=RNG_SEED):
    """Collect final infection counts over independent, reproducible trials."""
    if trial_count < 1:
        raise ValueError("trial_count must be at least 1")

    trial_results = None
    for seed in range(start_seed, start_seed + trial_count):
        results, _, _, _ = run_comparison(graph, rng_seed=seed)
        if trial_results is None:
            trial_results = {strategy: [] for strategy in results}
        for strategy, count in results.items():
            trial_results[strategy].append(count)
    return trial_results


def summarize_trials(trial_results):
    """Return mean final infections and 95% confidence intervals by strategy."""
    summary = {}
    for strategy, counts in trial_results.items():
        mean = statistics.mean(counts)
        standard_deviation = statistics.stdev(counts) if len(counts) > 1 else 0.0
        confidence_interval = 1.96 * standard_deviation / math.sqrt(len(counts))
        summary[strategy] = {
            "trials": len(counts),
            "mean_final_infected": mean,
            "standard_deviation": standard_deviation,
            "ci95_half_width": confidence_interval,
        }
    return summary


def save_artifacts(graph, results, plans, histories, baseline_infected, trial_results, trial_summary):
    """Write figures and a JSON summary for the demonstration and report."""
    from src.visualize import plot_comparison, plot_infection_curves, plot_network

    RESULTS_DIR.mkdir(exist_ok=True)
    mean_results = {
        strategy: metrics["mean_final_infected"]
        for strategy, metrics in trial_summary.items()
    }
    ci95_errors = {
        strategy: metrics["ci95_half_width"]
        for strategy, metrics in trial_summary.items()
    }
    plot_comparison(
        mean_results,
        RESULTS_DIR / "strategy_comparison.png",
        errors=ci95_errors,
        title="Mean Final Infections Across 30 Trials (95% CI)",
    )
    plot_infection_curves(histories, RESULTS_DIR / "infection_curves.png")
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
        "infection_histories": histories,
        "multi_trial_results": trial_results,
        "multi_trial_summary": trial_summary,
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

    results, plans, histories, baseline_infected = run_comparison(graph)
    trial_results = run_trials(graph)
    trial_summary = summarize_trials(trial_results)
    save_artifacts(
        graph, results, plans, histories, baseline_infected, trial_results, trial_summary
    )

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

    print("\n--- Mean Final Infections (30 Trials, 95% CI) ---")
    for strategy, metrics in trial_summary.items():
        print(
            f"{strategy} -> {metrics['mean_final_infected']:.2f} "
            f"± {metrics['ci95_half_width']:.2f}"
        )

    print("\nSaved results to:", RESULTS_DIR)
