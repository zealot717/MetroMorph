1. python3 -m scripts.01_define_aoi
2. 

run as a module ,

so any firstly be in Main directory  -- Urban Cooling

then run like this python3 -m scripts.01_define_aoi

follow the order as to how the scripts are numberered and each step has a verification test.

As of now works till step 07, data preprocessing is done

1. routing 
2. cool corridors 
3. UI


Urban_Cooling/
├── config/
│   └── aoi_config.py                 # Bounding box / AOI polygon definition
│
├── data/
│   ├── raw/                          # Unprocessed input data
│   │   ├── osm_graph.gpkg            # OSM road network (walkable)
│   │   ├── NDVI.tif                  # Raw NDVI raster (Sentinel-2)
│   │   └── LST.tif                   # Raw LST raster (Landsat 8)
│
│   ├── processed/                    # Clipped to AOI
│   │   ├── clipped_graph.gpkg        # Clipped road network (AOI only)
│   │   ├── NDVI_crop.tif             # AOI-clipped NDVI raster
│   │   └── LST_crop.tif              # AOI-clipped LST raster
│
│   ├── enriched/                     # Raster values sampled onto roads
│   │   ├── enriched_graph.gpkg       # Road segments enriched with NDVI & LST
│   │   └── enriched_graph_scored.gpkg  # Above + coolness score computed
│
│   └── routing/                      # Final graph used for routing
│       └── cool_graph.graphml        # NetworkX graph with edge weights
│
├── scripts/                          # Core pipeline scripts
│   ├── 01_define_aoi.py              # (if exists) Sets bounding box
│   ├── 02_download_graphs.py         # Downloads walkable OSM graph
│   ├── 03_download_rasters.py        # Fetches NDVI and LST from Earth Engine
│   ├── 04_clip_graph_and_rasters.py  # Clips road/rasters to AOI
│   ├── 05_enrich_graph.py            # Samples rasters onto roads
│   ├── 06_verify_enrichment.py       # (if present) optional debug
│   ├── 07c_compute_coolness_score.py # Computes normalized cool score
│   ├── 07_build_graph_from_enriched.py  # Converts GPKG → GraphML
│   └── 08_routing_demo.py            # Finds and plots coolest route
│
├── random_scripts/                   # All verification and QA scripts
│   ├── verify_step2.py               # Verifies raw OSM graph
│   ├── verify_step3.py               # Verifies raw raster stats/plots
│   ├── verify_step4.py               # Checks clipped files
│   ├── verify_step5.py               # Histogram and stats for enrichment
│   ├── verify_step6.py               # Histogram of cool scores
│   ├── verify_step7.py               # Graph structure and weights
│   └── verify_step8.py               # (optional) route path plotting
│
├── utils/                            # (Optional) Utility scripts (if made later)
│
├── README.md                         # (Optional) Project description
└── requirements.txt                  # (Optional) Environment setup
