# random_scripts/verify_step7_build_graph.py

import networkx as nx
import matplotlib.pyplot as plt
import os

def verify_graph(graph_path="data/routing/cool_graph.graphml"):
    print("📂 Loading GraphML...")
    G = nx.read_graphml(graph_path)
    print(f"✅ Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    # Extract geometries and weights
    edge_geometries = []
    weights = []
    for u, v, data in G.edges(data=True):
        if "geometry" in data and "weight" in data:
            try:
                from shapely import wkt
                line = wkt.loads(data["geometry"])
                edge_geometries.append(line)
                weights.append(float(data["weight"]))
            except Exception:
                continue

    print(f"✅ Valid geometries: {len(edge_geometries)} / {len(G.edges())}")

    # Weight statistics
    if weights:
        import numpy as np
        print("📊 Edge Weight Stats (lower = cooler):")
        print(f"  - Min: {np.min(weights):.3f}")
        print(f"  - Max: {np.max(weights):.3f}")
        print(f"  - Mean: {np.mean(weights):.3f}")

        plt.hist(weights, bins=30, color="skyblue", edgecolor="black")
        plt.title("Edge Weights (1 - Coolness Score)")
        plt.xlabel("Weight")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    verify_graph()
