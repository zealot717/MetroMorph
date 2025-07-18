# random_scripts/verify_step3_overlay.py

import geopandas as gpd
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
from config.aoi_config import get_aoi_box

def plot_raster_with_aoi(raster_path, title):
    with rasterio.open(raster_path) as src:
        fig, ax = plt.subplots(figsize=(10, 10))
        show(src, ax=ax, cmap='RdYlGn' if "NDVI" in raster_path else 'inferno', title=title)
        
        # Draw AOI bbox
        aoi_poly = gpd.GeoSeries([get_aoi_box()], crs="EPSG:4326")
        aoi_poly.boundary.plot(ax=ax, edgecolor="cyan", linewidth=2, linestyle="--", label="AOI")

        plt.legend()
        plt.axis("off")
        plt.tight_layout()
        plt.show()

def main():
    print("🖼️ Visualizing NDVI + LST with AOI overlay")
    plot_raster_with_aoi("data/raw/NDVI.tif", "🌿 NDVI (Sentinel-2)")
    plot_raster_with_aoi("data/raw/LST.tif", "🔥 LST in °C (Landsat 8 Thermal)")

if __name__ == "__main__":
    main()
