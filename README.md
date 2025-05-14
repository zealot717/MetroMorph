Run it in this order:
1. data_prep.py
2. lst_model.py
3. rasterinit.py
4. roadnet.py

Before running data_prep.py you'll have to authenticate a google earth engine account client. It'll send files to GDrive, download and store it in a folder locally, change names in code accordingly.

What’s Been Done (Steps 1–4a)
Step 1: GEE Data Extraction
Exported NDVI, NDBI, and LST from Sentinel-2 and Landsat 8 using Google Earth Engine (GEE).

Switched to single-band exports for each variable (bangalore_ndvi.tif, bangalore_ndbi.tif, bangalore_lst.tif) to simplify local analysis and avoid issues with band stacking.

Resolution: 30m, AOI: Bengaluru bbox.

Step 2: Local Preprocessing & Correlation
Loaded individual .tif files and cleaned them (masked nodata).

Computed basic stats and visualized distributions (NDVI, NDBI, LST).

Correlation analysis:

NDVI vs LST (expected: negative)

NDBI vs LST (expected: positive)

This step confirmed that vegetated areas are cooler and built-up areas are hotter, validating the use of LST for cool corridor design.

Step 3: LST Export Confirmation
Ensured LST (bangalore_lst.tif) was correctly exported and georeferenced.

Step 4a: Road Network + LST Sampling
Downloaded walkable road network from OpenStreetMap using osmnx.

Projected it to match the LST raster CRS.

Sampled mean LST values along each road segment using raster lookup.

Stored the result in edges['mean_lst'] and saved it to a GeoJSON (road_edges_with_lst.geojson).

Visualized roads with a cool-warm color scale based on their LST.

⏭️ What’s Next (Step 4b onward)
Step 4b: Coolest Route Finder
Goal: Find the thermally most comfortable (coolest) path between any two points in the city, using the road network weighted by mean_lst.

Tasks:
Add mean_lst as edge weight.

Prompt user for source and destination (coordinates or interactively).

Use Dijkstra or A algorithm* to compute:

shortest_path by distance (baseline)

coolest_path by mean LST

Plot both paths on the map for comparison.

Export as GeoJSON or static map