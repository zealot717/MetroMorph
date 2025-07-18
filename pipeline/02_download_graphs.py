# scripts/02_download_graphs.py

"""
Download walkable road network (OSM) for the fixed AOI
"""

import osmnx as ox
from config.aoi_config import get_aoi_box

def main():
    print("📦 Downloading walkable OSM graph within AOI...")

    aoi_polygon = get_aoi_box()

    # Download graph directly using API call options
    graph = ox.graph_from_polygon(
        aoi_polygon,
        network_type="walk",     # walkable network
        simplify=True,
        retain_all=False,
        truncate_by_edge=True,
        custom_filter=None
    )

    # Save to GeoPackage
    output_path = "data/raw/osm_graph.gpkg"
    ox.save_graph_geopackage(graph, filepath=output_path)

    print(f"✅ Saved graph to: {output_path}")


if __name__ == "__main__":
    main()
