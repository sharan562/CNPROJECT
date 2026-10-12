"""Streamlit dashboard for the banking-malware containment prototype."""

import json
import random

import streamlit as st

from src.comparison import run_comparison, run_trials, summarize_trials
from src.topology import get_adjacency_graph
from src.visualize import plot_comparison, plot_infection_curves, plot_network

TOPOLOGIES = {
    "Default (8 nodes)": "data/bank_topology.json",
    "Multi-branch (19 nodes)": "data/bank_topology_multibranch.json",
}
RANDOM_TOPOLOGY_SEED = 7


def adjacency_from_data(data):
    """Build {node: set(neighbors)} from a topology dict {nodes, edges}."""
    graph = {node["id"]: set() for node in data["nodes"]}
    for u, v in data["edges"]:
        graph[u].add(v)
        graph[v].add(u)
    return graph


def make_random_graph(n_nodes, edge_probability):
    """Deterministic connected random graph with zero-padded labels N00..N{n-1}."""
    rng = random.Random(RANDOM_TOPOLOGY_SEED)
    labels = [f"N{i:02d}" for i in range(n_nodes)]
    graph = {label: set() for label in labels}
    for i in range(1, n_nodes):
        parent = rng.randrange(i)
        graph[labels[i]].add(labels[parent])
        graph[labels[parent]].add(labels[i])
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            if rng.random() < edge_probability:
                graph[labels[i]].add(labels[j])
                graph[labels[j]].add(labels[i])
    return graph

st.set_page_config(page_title="Banking Malware Containment", layout="wide")

st.title("Cost-Constrained Containment of Emotet-Class Banking Malware")
st.caption("Prototype simulation — does not scan, contact, or modify production networks.")

with st.sidebar:
    st.header("Experiment controls")

    source = st.selectbox("Topology source", ["Preset", "Upload JSON", "Random"])

    if source == "Preset":
        topology_name = st.selectbox("Topology", list(TOPOLOGIES))
        graph = get_adjacency_graph(TOPOLOGIES[topology_name])
    elif source == "Upload JSON":
        uploaded = st.file_uploader(
            "Topology JSON",
            type=["json"],
            help='Expected shape: {"nodes": [{"id": "..."}], "edges": [["a", "b"]]}',
        )
        if uploaded is None:
            st.info("Upload a topology JSON file, or switch to Preset or Random.")
            st.stop()
        try:
            graph = adjacency_from_data(json.loads(uploaded.getvalue()))
        except Exception as exc:
            st.error(f"Could not read topology: {exc}")
            st.stop()
    else:
        n_nodes = st.slider("Number of nodes", 5, 60, 20, 1)
        edge_probability = st.slider("Edge probability", 0.0, 1.0, 0.12, 0.01)
        graph = make_random_graph(n_nodes, edge_probability)

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

mean_results = {s: m["mean_final_infected"] for s, m in trial_summary.items()}
ci_errors = {s: m["ci95_half_width"] for s, m in trial_summary.items()}

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Mean final infections across trials")
    st.pyplot(
        plot_comparison(
            mean_results,
            errors=ci_errors,
            title=f"Mean Final Infections Across {int(trials)} Trials (95% CI)",
        ),
        use_container_width=True,
    )
with col_right:
    st.subheader("Infection curves")
    st.pyplot(plot_infection_curves(histories), use_container_width=True)

st.subheader("Network topology")
st.pyplot(
    plot_network(graph, infected=baseline_infected, quarantined=plans["Proposed"]),
    use_container_width=True,
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
