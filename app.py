"""Streamlit dashboard for the banking-malware containment prototype."""

import streamlit as st

from src.comparison import run_comparison, run_trials, summarize_trials
from src.topology import get_adjacency_graph
from src.visualize import plot_comparison, plot_infection_curves, plot_network

TOPOLOGIES = {
    "Default (8 nodes)": "data/bank_topology.json",
    "Multi-branch (19 nodes)": "data/bank_topology_multibranch.json",
}

st.set_page_config(page_title="Banking Malware Containment", layout="wide")

st.title("Cost-Constrained Containment of Emotet-Class Banking Malware")
st.caption("Prototype simulation — does not scan, contact, or modify production networks.")

with st.sidebar:
    st.header("Experiment controls")

    topology_name = st.selectbox("Topology", list(TOPOLOGIES))
    topology_path = TOPOLOGIES[topology_name]

    graph = get_adjacency_graph(topology_path)
    nodes = sorted(graph.keys())

    seed_node = st.selectbox("Seed node", nodes)
    beta = st.slider("Transmission probability (β)", 0.0, 1.0, 0.25, 0.05)
    budget = st.number_input("Quarantine budget (K)", min_value=0, value=2, step=1)
    trials = st.number_input("Trial count", min_value=1, value=30, step=1)
    rng_seed = st.number_input("Random seed", min_value=0, value=42, step=1)

seeds = [seed_node]

results, plans, histories, baseline_infected = run_comparison(
    graph, seeds=seeds, beta=beta, budget=budget, rng_seed=rng_seed
)
trial_results = run_trials(
    graph, seeds=seeds, beta=beta, budget=budget,
    trial_count=int(trials), start_seed=rng_seed,
)
trial_summary = summarize_trials(trial_results)

st.subheader("Final infection counts (single run)")
st.dataframe(
    [{"Strategy": strategy, "Final infected": count} for strategy, count in results.items()],
    hide_index=True,
)

st.subheader("Mean final infections across trials")
mean_results = {s: m["mean_final_infected"] for s, m in trial_summary.items()}
ci_errors = {s: m["ci95_half_width"] for s, m in trial_summary.items()}
st.pyplot(
    plot_comparison(
        mean_results,
        errors=ci_errors,
        title=f"Mean Final Infections Across {int(trials)} Trials (95% CI)",
    )
)

st.subheader("Infection curves")
st.pyplot(plot_infection_curves(histories))

st.subheader("Network topology")
st.pyplot(
    plot_network(graph, infected=baseline_infected, quarantined=plans["Proposed"])
)

st.subheader("Quarantine plans")
st.dataframe(
    [
        {"Strategy": strategy, "Plan": ", ".join(plan)}
        for strategy, plan in plans.items()
    ],
    hide_index=True,
)

st.subheader("Multi-trial summary")
st.dataframe(
    [
        {
            "Strategy": strategy,
            "Trials": metrics["trials"],
            "Mean final infected": round(metrics["mean_final_infected"], 3),
            "Std dev": round(metrics["standard_deviation"], 3),
            "95% CI ±": round(metrics["ci95_half_width"], 3),
        }
        for strategy, metrics in trial_summary.items()
    ],
    hide_index=True,
)
