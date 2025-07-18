import geopandas as gpd
import numpy as np
import folium

# --- Constants ---
TREES_PER_METER = 0.2               # 2 trees per 10m
COOL_SCORE_PER_TREE = 0.003
TREE_COST = 100                    # INR per tree

COOL_ROOF_SCORE_PER_METER = 0.002
COOL_ROOF_COST_PER_METER = 150     # INR per meter

MAX_COOL_SCORE = 1.0


def apply_intervention(gdf_edges, intervention_type, intensity):
    """
    Apply cooling intervention (trees or cool roofs) on top-N% hottest edges.

    Parameters:
    - gdf_edges: GeoDataFrame with 'cool_score' and geometry.
    - intervention_type: "Add Trees" or "Cool Roofs"
    - intensity: float from 0.0 to 1.0 (fraction of edges to target)

    Returns:
    - Modified GeoDataFrame
    - Total objects added (trees or meters treated)
    - Total cost (INR)
    - Avg delta score
    """
    gdf = gdf_edges.copy()
    n_edges = len(gdf)
    n_target = int(n_edges * intensity)

    hottest_edges = gdf.nsmallest(n_target, "cool_score")

    total_objects = 0
    total_cost = 0
    deltas = []

    for idx, row in hottest_edges.iterrows():
        length_m = row.geometry.length * 111_000  # Approx conversion from degrees to meters

        if intervention_type == "Add Trees":
            n_trees = int(length_m * TREES_PER_METER)
            delta_score = n_trees * COOL_SCORE_PER_TREE
            cost = n_trees * TREE_COST
            count = n_trees

        elif intervention_type == "Cool Roofs":
            delta_score = length_m * COOL_ROOF_SCORE_PER_METER
            cost = length_m * COOL_ROOF_COST_PER_METER
            count = length_m  # meters treated

        else:
            continue

        new_score = min(row.cool_score + delta_score, MAX_COOL_SCORE)
        gdf.at[idx, "cool_score"] = new_score

        total_objects += count
        total_cost += cost
        deltas.append(delta_score)

    avg_delta_score = np.mean(deltas) if deltas else 0
    return gdf, int(total_objects), int(total_cost), avg_delta_score


def export_intervention_geojson(gdf_before, gdf_after, output_path):
    """
    Export GeoJSON showing only edges with Δscore after intervention.

    Parameters:
    - gdf_before: Original GeoDataFrame
    - gdf_after: Modified GeoDataFrame after intervention
    - output_path: Path to save the GeoJSON file

    Returns:
    - File path of saved GeoJSON
    """
    gdf = gdf_before.copy()
    gdf["new_score"] = gdf_after["cool_score"]
    gdf["delta_score"] = gdf["new_score"] - gdf["cool_score"]
    delta_gdf = gdf[gdf["delta_score"] > 0]
    delta_gdf.to_file(output_path, driver="GeoJSON")
    return output_path


def render_intervention_map(gdf_original, gdf_modified, base_map, intervention_type=None):
    """
    Overlay Δcool_score segments on a folium map.

    Parameters:
    - gdf_original: GeoDataFrame before intervention
    - gdf_modified: GeoDataFrame after intervention
    - base_map: folium.Map object to modify
    - intervention_type: str, either "Add Trees" or "Cool Roofs"

    Returns:
    - folium.Map with highlighted ΔScore segments
    """
    gdf = gdf_original.copy()
    gdf["new_score"] = gdf_modified["cool_score"]
    gdf["delta_score"] = gdf["new_score"] - gdf["cool_score"]
    delta_gdf = gdf[gdf["delta_score"] > 0]

    for _, row in delta_gdf.iterrows():
        delta = row["delta_score"]
        geom = row.geometry

        if intervention_type == "Cool Roofs":
            color = (
                "#cce6ff" if delta < 0.01 else
                "#66b3ff" if delta < 0.03 else
                "#0066cc"
            )
        else:  # Default or "Add Trees"
            color = (
                "#00ff00" if delta < 0.01 else
                "#00cc00" if delta < 0.03 else
                "#009900"
            )

        if geom.geom_type == "LineString":
            lines = [geom]
        elif geom.geom_type == "MultiLineString":
            lines = list(geom.geoms)
        else:
            continue

        for line in lines:
            folium.PolyLine(
                locations=[(lat, lon) for lon, lat in line.coords],
                color=color,
                weight=4,
                tooltip=f"ΔScore: {delta:.4f}"
            ).add_to(base_map)

    return base_map
