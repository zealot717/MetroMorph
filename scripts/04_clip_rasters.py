import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import box
from config.aoi_config import get_aoi_box

# === 0. Setup
aoi = get_aoi_box()
aoi_gdf = gpd.GeoDataFrame([1], geometry=[aoi], crs="EPSG:4326")

os.makedirs("data/processed", exist_ok=True)

# === 1. Load only the 'edges' layer from osm_graph.gpkg
print("📦 Loading edges from osm_graph.gpkg...")
edges = gpd.read_file("data/raw/osm_graph.gpkg", layer="edges")

# === 2. Clip edges
print("✂️ Clipping edges to AOI...")
edges_clipped = gpd.clip(edges, aoi_gdf)
edges_clipped.to_file("data/processed/clipped_graph.gpkg", layer="clipped_graph", driver="GPKG")
print("✅ Saved clipped graph with LineStrings.")

# === 3. Clip NDVI
print("🌿 Clipping NDVI raster...")
with rasterio.open("data/raw/NDVI.tif") as src:
    out_image, out_transform = mask(src, [aoi], crop=True)
    out_meta = src.meta.copy()
    out_meta.update({
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })
    with rasterio.open("data/processed/NDVI_crop.tif", "w", **out_meta) as dest:
        dest.write(out_image)
print("✅ NDVI raster clipped.")

# === 4. Clip LST
print("🔥 Clipping LST raster...")
with rasterio.open("data/raw/LST.tif") as src:
    out_image, out_transform = mask(src, [aoi], crop=True)
    out_meta = src.meta.copy()
    out_meta.update({
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })
    with rasterio.open("data/processed/LST_crop.tif", "w", **out_meta) as dest:
        dest.write(out_image)
print("✅ LST raster clipped.")
