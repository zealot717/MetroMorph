# scripts/07_build_graph_from_enriched.py

import geopandas as gpd
import networkx as nx
import os
from shapely.geometry import LineString
from tqdm import tqdm

def main():
    print("🔁 Converting enriched GPKG to weighted graph...")

    # Load enriched GeoDataFrame
    gdf = gpd.read_file("data/enriched/enriched_graph_scored.gpkg")

    # Drop rows with invalid or null geometries
    gdf = gdf[gdf.geometry.notnull()].copy()
    gdf = gdf[gdf.geometry.type == "LineString"]

    # Normalize weight direction (higher coolness = lower weight)
    G = nx.Graph()

    valid_count = 0
    for idx, row in tqdm(gdf.iterrows(), total=len(gdf)):
        geom = row.geometry
        if not isinstance(geom, LineString) or len(geom.coords) < 2:
            continue

        coords = list(geom.coords)
        start = (coords[0][1], coords[0][0])  # lat, lon
        end = (coords[-1][1], coords[-1][0])

        # Invert cool score for weight: cooler = lower cost
        weight = 1 - row["cool_score"]
        try:
            G.add_edge(start, end, weight=weight, geometry=geom.wkt)
            valid_count += 1
        except Exception as e:
            continue

    print(f"✅ Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    print(f"✅ Valid LineStrings used: {valid_count} / {len(gdf)}")

    # Save to GraphML (geometry stored as WKT string)
    output_path = "data/routing/cool_graph.graphml"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    nx.write_graphml(G, output_path)
    print(f"✅ GraphML with geometries saved to: {output_path}")

if __name__ == "__main__":
    main()
