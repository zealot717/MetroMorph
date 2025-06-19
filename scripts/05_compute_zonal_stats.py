import geopandas as gpd
from rasterstats import zonal_stats
import os
from tqdm import tqdm

# ---------- Paths ----------
graph_fp = "data/processed/clipped_graph.gpkg"
ndvi_fp = "data/processed/NDVI_crop.tif"
lst_fp = "data/processed/LST_crop.tif"
out_fp = "data/enriched/enriched_graph.gpkg"

# ---------- Load Clipped Road Network ----------
print("📂 Loading clipped road network...")
gdf = gpd.read_file(graph_fp)

# Ensure geometry is in WGS84 for compatibility
gdf = gdf.to_crs("EPSG:4326")

# ---------- Function to Extract Zonal Mean ----------
def compute_zonal_mean(gdf, raster_path, col_name, buffer_dist=0.0002):
    """
    Computes mean raster value within a small buffer around each road segment.
    
    Args:
        gdf (GeoDataFrame): Input GeoDataFrame with LineStrings.
        raster_path (str): Path to raster (.tif).
        col_name (str): Output column name.
        buffer_dist (float): Buffer distance in degrees (~0.0002 ≈ 20m).
    
    Returns:
        GeoDataFrame with new column.
    """
    print(f"🔍 Extracting mean from {os.path.basename(raster_path)}...")
    buffered = gdf.geometry.buffer(buffer_dist)
    zs = zonal_stats(buffered, raster_path, stats=["mean"], nodata=None)
    gdf[col_name] = [z["mean"] if z and z["mean"] is not None else None for z in zs]
    return gdf

# ---------- Apply to NDVI and LST ----------
os.makedirs(os.path.dirname(out_fp), exist_ok=True)

gdf = compute_zonal_mean(gdf, ndvi_fp, "mean_ndvi")
gdf = compute_zonal_mean(gdf, lst_fp, "mean_lst")

# ---------- Save Enriched Graph ----------
gdf.to_file(out_fp, driver="GPKG")
print(f"✅ Saved enriched graph to: {out_fp}")
