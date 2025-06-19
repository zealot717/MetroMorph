# test_plot_aoi.py

from config.aoi_config import get_aoi_box
import geopandas as gpd
import matplotlib.pyplot as plt

gdf = gpd.GeoDataFrame(geometry=[get_aoi_box()], crs="EPSG:4326")
gdf.plot(edgecolor="red", facecolor="none")
plt.title("AOI: Central Bengaluru")
plt.grid(True)
plt.show()
