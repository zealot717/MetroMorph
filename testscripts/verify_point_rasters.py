import geopandas as gpd
import rasterio
from rasterio.sample import sample_gen
from shapely.geometry import Point
import numpy as np
import matplotlib.pyplot as plt
from rasterio.plot import show

def sample_raster_at_points(raster_path, points_gdf):
    with rasterio.open(raster_path) as src:
        values = []
        for pt in points_gdf.geometry:
            val = list(src.sample([(pt.x, pt.y)]))[0]
            values.append(val[0] if val[0] is not None else np.nan)
    return values

def main():
    print("🎯 Verifying raster point sampling...")

    # Load clipped raster
    raster_path = "data/processed/NDVI_crop.tif"  # or LST_crop.tif
    points = [
        Point(77.6235, 12.9642),
        Point(77.6267, 12.9613),
        Point(77.6351, 12.9723)
    ]

    gdf = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")

    # Sample values
    values = sample_raster_at_points(raster_path, gdf)
    gdf["raster_val"] = values

    print("\n🧪 Sampled values:")
    for i, (idx, row) in enumerate(gdf.iterrows(), 1):
        print(f"Point {i}: ({row.geometry.x:.6f}, {row.geometry.y:.6f}) -> Value: {row.raster_val:.4f}")

    # Visualize
    with rasterio.open(raster_path) as src:
        fig, ax = plt.subplots(figsize=(8, 8))
        show(src, ax=ax, cmap="RdYlGn" if "NDVI" in raster_path else "inferno")
        gdf.plot(ax=ax, color='blue', marker='o', markersize=80, label="Sample Points")
        ax.set_title("📍 Sampled Points on Raster")
        plt.legend()
        plt.axis("off")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()
