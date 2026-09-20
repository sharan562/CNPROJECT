import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch
from pathlib import Path


def plot_network(graph, infected=None, quarantined=None, output_path="network_topology.png"):
    """Save the bank topology, highlighting infected and quarantined nodes."""

    infected = set(infected or [])
    quarantined = set(quarantined or [])

    G = nx.Graph()

    # Add nodes and edges
    for node, neighbors in graph.items():
        G.add_node(node)

        for neighbor in neighbors:
            G.add_edge(node, neighbor)

    # Create network layout
    pos = nx.spring_layout(G, seed=42)

    normal_nodes = [
        node for node in G.nodes
        if node not in infected and node not in quarantined
    ]

    # Draw edges
    nx.draw_networkx_edges(G, pos)

    # Draw normal nodes
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=normal_nodes,
        node_size=900,
        node_color="#9ecae1",
    )

    # Draw infected nodes
    if infected:
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=list(infected),
            node_size=900,
            node_color="#e74c3c",
        )

    # Draw quarantined nodes
    if quarantined:
        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=list(quarantined),
            node_size=900,
            node_color="#f39c12",
        )

    # Draw labels
    nx.draw_networkx_labels(G, pos)

    plt.legend(handles=[
        Patch(color="#9ecae1", label="Susceptible"),
        Patch(color="#e74c3c", label="Infected"),
        Patch(color="#f39c12", label="Quarantined"),
    ], loc="best")
    plt.title("Bank Network: Baseline Infection and Proposed Quarantine Plan")
    plt.axis("off")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close()


def plot_infection_curve(infected_history):
    """Plot the number of infected nodes over time."""

    time = list(range(len(infected_history)))

    plt.figure()

    plt.plot(
        time,
        infected_history,
        marker="o"
    )

    plt.xlabel("Time Step")
    plt.ylabel("Number of Infected Nodes")
    plt.title("Malware Infection Spread")

    plt.grid(True)

    plt.savefig("infection_curve.png")
    plt.close()


def plot_comparison(results, output_path="strategy_comparison.png"):
    """Save a comparison of final infection counts by strategy."""

    strategies = list(results.keys())
    infected_counts = list(results.values())

    plt.figure()

    colors = ["#7f8c8d", "#95a5a6", "#5dade2", "#58d68d", "#e67e22"]
    plt.bar(
        strategies,
        infected_counts,
        color=colors[:len(strategies)],
    )

    plt.xlabel("Containment Strategy")
    plt.ylabel("Final Infected Nodes")
    plt.title("Containment Strategy Comparison")

    plt.xticks(rotation=20)
    plt.tight_layout()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=160)
    plt.close()


if __name__ == "__main__":

    from topology import get_adjacency_graph

    # Load bank network
    graph = get_adjacency_graph(
        "data/bank_topology.json"
    )

    # Example nodes for testing
    infected = {
        "WS_1",
        "BRANCH_1"
    }

    quarantined = {
        "ATM_1"
    }

    # Generate network visualization
    plot_network(
        graph,
        infected=infected,
        quarantined=quarantined
    )

    print("Network visualization saved as network_topology.png")
