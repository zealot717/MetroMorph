# scripts/verify_step2_osm_graph.py

import geopandas as gpd
import matplotlib.pyplot as plt
from config.aoi_config import get_aoi_box
import contextily as ctx

def main():
    print("🗺️ Verifying downloaded OSM graph from GPKG...")

    # Load the graph edges from GeoPackage
    gdf = gpd.read_file("data/raw/osm_graph.gpkg", layer='edges')

    print(f"✅ Loaded {len(gdf)} edges from GPKG")

    # Load AOI bounding box
    aoi = get_aoi_box()
    aoi_gdf = gpd.GeoDataFrame(geometry=[aoi], crs="EPSG:4326")

    # Project both to Web Mercator for basemap compatibility
    gdf = gdf.to_crs(epsg=3857)
    aoi_gdf = aoi_gdf.to_crs(epsg=3857)

    # Plot the graph and AOI
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, linewidth=0.5, color='blue', label="OSM Road Segments")
    aoi_gdf.boundary.plot(ax=ax, color='red', linewidth=1.5, linestyle="--", label="AOI")

    # Add basemap
    ctx.add_basemap(ax)
    ax.set_title("✅ OSM Walkable Network over AOI")
    ax.legend()
    ax.axis('off')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
