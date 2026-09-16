import json
import networkx as nx


def load_topology(filename):
    with open(filename, "r") as file:
        data = json.load(file)

    G = nx.Graph()

    # Add nodes
    for node in data["nodes"]:
        G.add_node(
            node["id"],
            type=node["type"],
            security=node["security"]
        )

    # Add edges
    for edge in data["edges"]:
        G.add_edge(edge[0], edge[1])

    return G


def get_topology_info(G):
    print("\n--- Network Topology ---")
    print("Number of nodes:", G.number_of_nodes())
    print("Number of edges:", G.number_of_edges())

    print("\nNodes:")

    for node, data in G.nodes(data=True):
        print(
            node,
            "| Type:", data["type"],
            "| Security:", data["security"],
            "| Degree:", G.degree[node]
        )


def calculate_centrality(G):
    degree = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)

    return degree, betweenness


if __name__ == "__main__":

    G = load_topology("data/bank_topology.json")

    get_topology_info(G)

    degree, betweenness = calculate_centrality(G)

    print("\nDegree Centrality:")

    for node, value in degree.items():
        print(node, round(value, 3))

    print("\nBetweenness Centrality:")

    for node, value in betweenness.items():
        print(node, round(value, 3))