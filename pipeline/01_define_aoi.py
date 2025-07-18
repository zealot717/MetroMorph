# scripts/01_define_aoi.py

from config.aoi_config import AOI_BBOX, get_aoi_box
import geopandas as gpd

def save_aoi_as_file():
    aoi = get_aoi_box()
    gdf = gpd.GeoDataFrame({'geometry': [aoi]}, crs="EPSG:4326")
    gdf.to_file("data/processed/aoi_bbox.geojson", driver="GeoJSON")
    print("✅ AOI saved to data/processed/aoi_bbox.geojson")

if __name__ == "__main__":
    save_aoi_as_file()
