# scripts/07_build_graph_from_enriched.py

import geopandas as gpd
import networkx as nx
import os
from shapely.geometry import LineString, MultiLineString
from tqdm import tqdm

def main():
    print("🔁 Converting enriched GPKG to weighted graph...")

    # Load enriched GeoDataFrame
    gdf = gpd.read_file("data/enriched/enriched_graph_scored.gpkg")
    print(f"📦 Loaded {len(gdf)} edges")

    # Filter valid geometries: LineString or MultiLineString
    gdf = gdf[gdf.geometry.notnull()]
    gdf = gdf[gdf.geometry.type.isin(["LineString", "MultiLineString"])]
    print(f"✅ After filtering: {len(gdf)} valid LineStrings or MultiLineStrings")

    G = nx.Graph()
    valid_count = 0
    skipped_short = 0
    skipped_other = 0

    for _, row in tqdm(gdf.iterrows(), total=len(gdf)):
        geom = row.geometry
        cool_score = row.get("cool_score", None)

        if cool_score is None or not geom:
            skipped_other += 1
            continue

        # Convert MultiLineString to individual LineStrings
        lines = [geom] if isinstance(geom, LineString) else list(geom.geoms)

        for line in lines:
            coords = list(line.coords)
            if len(coords) < 2:
                skipped_short += 1
                continue

            start = (coords[0][1], coords[0][0])  # (lat, lon)
            end = (coords[-1][1], coords[-1][0])
            weight = 1 - cool_score

            try:
                G.add_edge(start, end, weight=weight, geometry=line.wkt)
                valid_count += 1
            except Exception:
                skipped_other += 1
                continue

    print(f"✅ Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    print(f"📊 Valid edges used: {valid_count}")
    print(f"⚠️ Skipped (short lines): {skipped_short}, (other issues): {skipped_other}")

    # Save graph
    output_path = "data/routing/cool_graph.graphml"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    nx.write_graphml(G, output_path)
    print(f"✅ GraphML with geometries saved to: {output_path}")

if __name__ == "__main__":
    main()
