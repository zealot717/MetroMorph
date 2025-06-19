import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show, plotting_extent
import numpy as np
from config.aoi_config import get_aoi_box
from shapely.geometry import box

def show_clipped_graph():
    print("📍 Loading and plotting clipped OSM graph...")
    clipped = gpd.read_file("data/processed/clipped_graph.gpkg", layer="clipped_graph")

    fig, ax = plt.subplots(figsize=(10, 10))
    clipped.plot(ax=ax, color="black", linewidth=0.5)
    ax.set_title("🛣️ Clipped Walkable Graph within AOI")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def show_raster(path, title):
    print(f"🗺️ Visualizing: {title}")
    with rasterio.open(path) as src:
        raster = src.read(1, masked=True)

        if src.height is None or src.width is None:
            raise ValueError("Height or width is None for raster: " + path)

        fig, ax = plt.subplots(figsize=(10, 6))
        raster_show = ax.imshow(
            raster,
            cmap='RdYlGn' if 'NDVI' in path else 'inferno',
            extent=plotting_extent(src),
            vmin=np.nanmin(raster),
            vmax=np.nanmax(raster),
        )
        plt.colorbar(raster_show, ax=ax, orientation='vertical', label=title)
        ax.set_title(f"{title} (clipped)")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        plt.tight_layout()
        plt.show()


def main():
    print("✅ Step 4 Verification Started")

    # Show clipped graph
    show_clipped_graph()

    # Show clipped rasters
    show_raster("data/processed/NDVI_crop.tif", "🌿 NDVI")
    show_raster("data/processed/LST_crop.tif", "🔥 LST (°C)")


if __name__ == "__main__":
    main()
