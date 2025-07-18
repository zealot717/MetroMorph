# scripts/07c_compute_coolness_score.py

import geopandas as gpd
import os
from sklearn.preprocessing import MinMaxScaler

# Load enriched graph
fp = "data/enriched/enriched_graph.gpkg"
gdf = gpd.read_file(fp)

# Drop null values (no raster coverage)
gdf = gdf.dropna(subset=["mean_ndvi", "mean_lst"]).copy()

# Normalize both columns
scaler_ndvi = MinMaxScaler()
scaler_lst = MinMaxScaler()

gdf["ndvi_norm"] = scaler_ndvi.fit_transform(gdf[["mean_ndvi"]])
gdf["lst_norm"] = scaler_lst.fit_transform(gdf[["mean_lst"]])

# Compute Coolness Score
gdf["cool_score"] = 0.5 * gdf["ndvi_norm"] + 0.5 * (1 - gdf["lst_norm"])

# Save result
out_fp = "data/enriched/enriched_graph_scored.gpkg"
gdf.to_file(out_fp, driver="GPKG")

print(f"✅ Coolness scores saved to: {out_fp}")
