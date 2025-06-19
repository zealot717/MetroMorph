"""
Fixed AOI for Central Bengaluru (Optimized):
Covers a core zone around Domlur – Intermediate Ring Road – Indiranagar
Suitable for fast OSM downloads, raster cropping, and intervention testing
"""

AOI_BBOX = {
    "min_lon": 77.615,
    "min_lat": 12.955,
    "max_lon": 77.640,
    "max_lat": 12.985
}

def get_aoi_box():
    """Returns a shapely box polygon for AOI clipping."""
    from shapely.geometry import box
    return box(
        AOI_BBOX["min_lon"],
        AOI_BBOX["min_lat"],
        AOI_BBOX["max_lon"],
        AOI_BBOX["max_lat"]
    )

def get_bbox_list():
    """Returns bounding box as list: [min_lon, min_lat, max_lon, max_lat]"""
    return [
        AOI_BBOX["min_lon"],
        AOI_BBOX["min_lat"],
        AOI_BBOX["max_lon"],
        AOI_BBOX["max_lat"]
    ]
