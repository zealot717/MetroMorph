import networkx as nx
import matplotlib.pyplot as plt
import random
import geopandas as gpd
from shapely import wkt
from matplotlib.lines import Line2D

def load_graph(graphml_path):
    print("📂 Loading GraphML...")
    G = nx.read_graphml(graphml_path)

    # Fix node labels from strings to tuples
    G = nx.relabel_nodes(G, lambda x: eval(x) if isinstance(x, str) else x)

    # Convert WKT geometry strings to shapely objects and weights to float
    for u, v, data in G.edges(data=True):
        if 'geometry' in data:
            data['geometry'] = wkt.loads(data['geometry'])
        data['weight'] = float(data['weight'])

    print(f"✅ Loaded graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # 🔌 Extract the largest connected component
    largest_cc = max(nx.connected_components(G), key=len)
    G_sub = G.subgraph(largest_cc).copy()

    print(f"✅ Largest connected component: {G_sub.number_of_nodes()} nodes, {G_sub.number_of_edges()} edges")
    return G_sub


def get_random_node_pair(G):
    nodes = list(G.nodes)
    for _ in range(20):
        src = random.choice(nodes)
        dst = random.choice(nodes)
        if nx.has_path(G, src, dst):
            return src, dst
    raise ValueError("❌ No valid path found after multiple tries.")

def visualize_path(G, path, title="Cool Path"):
    print("🧭 Visualizing path...")

    edge_geoms = [G.edges[u, v]['geometry'] for u, v in zip(path[:-1], path[1:])]
    edge_gdf = gpd.GeoDataFrame(geometry=edge_geoms, crs="EPSG:4326")

    # Plot base network
    all_edges = [data['geometry'] for u, v, data in G.edges(data=True)]
    full_gdf = gpd.GeoDataFrame(geometry=all_edges, crs="EPSG:4326")

    ax = full_gdf.plot(color="lightgrey", linewidth=0.5, figsize=(10, 10))
    edge_gdf.plot(ax=ax, color="blue", linewidth=2, label="Cool Path")
    
    # Plot start and end
    start, end = path[0], path[-1]
    plt.scatter([start[1]], [start[0]], color="green", label="Start", zorder=5)
    plt.scatter([end[1]], [end[0]], color="red", label="End", zorder=5)

    plt.legend()
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def main():
    graph_path = "data/routing/cool_graph.graphml"
    G = load_graph(graph_path)

    print(f"✅ Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    src, dst = get_random_node_pair(G)
    print(f"📍 Source: {src}, Target: {dst}")

    path = nx.shortest_path(G, source=src, target=dst, weight='weight')
    print(f"🛣️ Path found with {len(path)} nodes.")

    visualize_path(G, path, title="Coolest Path Found")

if __name__ == "__main__":
    main()
