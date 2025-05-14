import osmnx as ox
import networkx as nx
import rasterio
import numpy as np
from shapely.geometry import box
import geopandas as gpd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# -----------------------
# 1. Download Walkable Road Network from OSM (Bangalore bounding box)
# -----------------------
# Define bounding box as polygon
bbox_polygon = box(77.4, 12.8, 77.75, 13.15)
gdf_bbox = gpd.GeoDataFrame(geometry=[bbox_polygon], crs='EPSG:4326')

# Get graph from polygon
G = ox.graph_from_polygon(gdf_bbox.loc[0, 'geometry'], network_type='walk')
G_proj = ox.project_graph(G)  # Project to UTM for accurate distance
edges = ox.graph_to_gdfs(G_proj, nodes=False, edges=True)

# -----------------------
# 2. Load LST Raster (already exported in EPSG:4326)
# -----------------------
lst_path = 'data/bangalore_lst.tif'
with rasterio.open(lst_path) as src:
    lst_data = src.read(1)
    lst_meta = src.meta
    lst_crs = src.crs
    lst_transform = src.transform
    lst_nodata = src.nodata

# -----------------------
# 3. Reproject Edges to Match Raster CRS (if needed)
# -----------------------
edges = edges.to_crs(lst_crs)

# -----------------------
# 4. Sample Mean LST Along Each Road Edge
# -----------------------
def sample_raster_along_line(line, raster, transform, nodata_val):
    coords = np.array(line.coords)
    rows, cols = rasterio.transform.rowcol(transform, coords[:, 0], coords[:, 1])
    values = []
    for r, c in zip(rows, cols):
        if 0 <= r < raster.shape[0] and 0 <= c < raster.shape[1]:
            val = raster[r, c]
            if val != nodata_val:
                values.append(val)
    return np.mean(values) if values else np.nan

edges['mean_lst'] = edges['geometry'].apply(lambda geom: sample_raster_along_line(
    geom, lst_data, lst_transform, lst_nodata
))

# Drop edges without valid LST
edges = edges.dropna(subset=['mean_lst'])

# -----------------------
# 5. Plot Mean LST per Edge
# -----------------------
edges.plot(column='mean_lst', cmap='coolwarm', legend=True)
plt.title("Mean Land Surface Temperature (LST) on Walkable Roads")
plt.axis('off')
plt.tight_layout()
plt.show()

# -----------------------
# 6. Save for Routing Use
# -----------------------
edges.to_file('data/road_edges_with_lst.geojson', driver='GeoJSON')
print("✅ Road edges with LST sampled and saved.")
