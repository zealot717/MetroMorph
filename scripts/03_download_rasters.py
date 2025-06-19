# scripts/03_download_rasters.py

import ee
import geemap
import os
from config.aoi_config import AOI_BBOX

# Initialize Earth Engine
try:
    ee.Initialize(project="sdg11-462407")  # Replace with your project ID
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project="sdg11-462407")  # Replace with your project ID

def get_bbox_geometry():
    return ee.Geometry.Rectangle(
        AOI_BBOX["min_lon"], AOI_BBOX["min_lat"],
        AOI_BBOX["max_lon"], AOI_BBOX["max_lat"]
    )

def download_ndvi(out_path):
    print("🌿 Downloading NDVI from Sentinel-2...")

    bbox = get_bbox_geometry()
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(bbox) \
        .filterDate("2023-01-01", "2023-12-31") \
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))

    image = collection.median().clip(bbox)
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

    geemap.ee_export_image(
        ndvi, filename=out_path, scale=30, region=bbox, file_per_band=False
    )
    print(f"✅ Saved NDVI to: {out_path}")

def download_lst(out_path):
    print("🔥 Downloading LST from Landsat 8 (thermal band)...")

    bbox = get_bbox_geometry()
    collection = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterBounds(bbox) \
        .filterDate("2023-01-01", "2023-12-31") \
        .filter(ee.Filter.lt("CLOUD_COVER", 10))

    image = collection.median().clip(bbox)

    # Apply scaling factors from Landsat documentation
    thermal = image.select("ST_B10").multiply(0.00341802).add(149.0).rename("LST_C")

    geemap.ee_export_image(
        thermal, filename=out_path, scale=100, region=bbox, file_per_band=False
    )
    print(f"✅ Saved LST to: {out_path}")



def main():
    os.makedirs("data/raw", exist_ok=True)
    download_ndvi("data/raw/NDVI.tif")
    download_lst("data/raw/LST.tif")


if __name__ == "__main__":
    main()