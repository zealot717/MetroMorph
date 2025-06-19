import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
from config.aoi_config import get_aoi_box

def main():
    aoi_geom = get_aoi_box()
    gdf = gpd.GeoDataFrame(geometry=[aoi_geom], crs="EPSG:4326").to_crs(epsg=3857)

    print("✅ AOI Bounds (in WGS84):", aoi_geom.bounds)

    ax = gdf.plot(edgecolor="red", facecolor="none", linewidth=2, figsize=(10, 10))
    
    # Use default basemap, no attribute-based access
    try:
        ctx.add_basemap(ax)  # automatically uses Stamen Terrain or other default
    except Exception as e:
        print("⚠️ Basemap loading failed:", e)

    ax.set_title("🗺️ AOI over Bengaluru - Verification")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
