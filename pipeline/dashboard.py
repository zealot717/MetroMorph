# import streamlit as st
# import geopandas as gpd
# import networkx as nx
# import numpy as np
# import folium
# from shapely.geometry import LineString, Point
# from streamlit_folium import st_folium
# from cooling_intervention import apply_intervention, render_intervention_map, export_intervention_geojson
# import rasterio
# import matplotlib.pyplot as plt
# from matplotlib.colors import Normalize
# from PIL import Image
# import io
# import base64
# import os

# # -------- Configuration --------
# GRAPH_PATH = r"C:\Projects\urban_heat\data\enriched\enriched_graph_scored.gpkg"

# # -------- Utility Functions --------
# @st.cache_data
# def load_graph_and_gdf(path):
#     gdf = gpd.read_file(path).to_crs(epsg=4326)
#     gdf["cool_score"] = gdf["cool_score"].fillna(gdf["cool_score"].median())

#     G = nx.Graph()
#     node_coords = {}
#     for _, row in gdf.iterrows():
#         u, v = row.u, row.v
#         geom = row.geometry
#         if geom.geom_type == "MultiLineString":
#             geom = max(geom.geoms, key=lambda g: g.length)
#         if geom.geom_type != "LineString":
#             continue

#         lon0, lat0 = geom.coords[0]
#         lon1, lat1 = geom.coords[-1]
#         node_coords[u] = (lon0, lat0)
#         node_coords[v] = (lon1, lat1)

#         G.add_node(u, coord=(lon0, lat0))
#         G.add_node(v, coord=(lon1, lat1))
#         G.add_edge(u, v,
#                    geometry=geom,
#                    length=geom.length,
#                    cool_score=row.cool_score)

#     return gdf, G, node_coords

# def snap_to_nearest_edge(G, click_lat, click_lon):
#     pt = Point(click_lon, click_lat)
#     best_dist = float("inf")
#     best_edge = None
#     for u, v, data in G.edges(data=True):
#         d = data["geometry"].distance(pt)
#         if d < best_dist:
#             best_dist = d
#             best_edge = (u, v)
#     if best_edge is None:
#         return None
#     u, v = best_edge
#     u_pt = Point(*G.nodes[u]["coord"][::-1])
#     v_pt = Point(*G.nodes[v]["coord"][::-1])
#     return u if pt.distance(u_pt) < pt.distance(v_pt) else v

# def stitch_path(G, path_nodes, raw_start=None, raw_end=None):
#     pts = []
#     if raw_start:
#         pts.append(raw_start)
#     seen = set()
#     for u, v in zip(path_nodes[:-1], path_nodes[1:]):
#         key = tuple(sorted((u, v)))
#         if key in seen:
#             continue
#         seen.add(key)
#         line = G.edges[u, v]["geometry"]
#         seg = [(lat, lon) for lon, lat in line.coords]
#         if pts and pts[-1] == seg[0]:
#             seg = seg[1:]
#         pts.extend(seg)
#     if raw_end:
#         pts.append(raw_end)
#     return pts

# def render_raster_on_map(tif_path, colormap='Greens', layer_name="Environmental Layer"):
#     with rasterio.open(tif_path) as src:
#         data = src.read(1, masked=True)
#         bounds = src.bounds

#     norm = Normalize(vmin=float(data.min()), vmax=float(data.max()))
#     cmap = plt.get_cmap(colormap)
#     rgba_img = cmap(norm(data.filled(0)))
#     img = Image.fromarray((rgba_img[:, :, :3] * 255).astype('uint8'))

#     buf = io.BytesIO()
#     img.save(buf, format='PNG')
#     base64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
#     img_url = f"data:image/png;base64,{base64_img}"

#     center_lat = (bounds.top + bounds.bottom) / 2
#     center_lon = (bounds.left + bounds.right) / 2
#     m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
#     folium.raster_layers.ImageOverlay(
#         image=img_url,
#         bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
#         opacity=0.6,
#         name=layer_name,
#         interactive=True,
#         cross_origin=False
#     ).add_to(m)
#     folium.LayerControl().add_to(m)
#     return m

# # -------- Streamlit App --------
# st.set_page_config(page_title="Urban Cool Corridor Optimizer", layout="wide")

# PAGES = ["Corridor Optimizer", "Environmental Layers", "UHI Segmentation"]
# page = st.sidebar.selectbox("Navigate", PAGES)

# # -------- Page 1: Optimizer --------
# if page == "Corridor Optimizer":
#     with st.sidebar:
#         st.markdown("### 🔧 Route Configuration")
#         poi_list = ["Ulsoor Lake", "Domlur Flyover", "MG Road", "Cubbon Park"]
#         start_loc = st.selectbox("Start Location", poi_list)
#         end_loc   = st.selectbox("End Location", poi_list, index=1)
#         routing_mode = st.radio("Routing Mode", ("Shortest Path", "Coolest Path"))
#         enable_cooling = st.checkbox("🌳 Enable Cooling Intervention", value=True)
#         intervention = st.selectbox("Type of Intervention", ("Add Trees", "Cool Roofs"))
#         intensity = st.slider("Intensity", 0.0, 1.0, 0.2, 0.01)
#         st.markdown("---")
#         st.button("📥 Export Route GeoJSON")

#     st.title("Urban Cool Corridor Optimizer")
#     gdf_edges, G, node_coords = load_graph_and_gdf(GRAPH_PATH)

#     if enable_cooling:
#         gdf_modified, total_trees, total_cost, avg_delta_score = apply_intervention(
#             gdf_edges, intervention, intensity
#         )
#     else:
#         gdf_modified = gdf_edges
#         total_trees = total_cost = avg_delta_score = None

#     if enable_cooling and st.sidebar.button("📥 Download ΔScore Map"):
#         os.makedirs("outputs", exist_ok=True)
#         out_path = "outputs/intervention_delta.geojson"
#         try:
#             geojson_file = export_intervention_geojson(gdf_edges, gdf_modified, out_path)
#             with open(geojson_file, "rb") as f:
#                 st.sidebar.download_button(
#                     "⬇️ Save ΔScore GeoJSON",
#                     f,
#                     file_name="cooling_intervention.geojson",
#                     mime="application/geo+json"
#                 )
#         except Exception as e:
#             st.sidebar.error(f"Failed to export GeoJSON: {e}")

#     # Initialize session state
#     for key in ("raw_start", "raw_end", "start_node", "end_node",
#                 "start_pt", "end_pt", "route", "distance_km", "avg_cool"):
#         st.session_state.setdefault(key, None)

#     # Build base map
#     m = folium.Map(location=[12.9716, 77.5946], zoom_start=13)
#     folium.GeoJson(
#         gdf_edges,
#         style_function=lambda f: {"color": "#ccc", "weight": 1, "opacity": 0.6}
#     ).add_to(m)
#     for lon, lat in node_coords.values():
#         folium.CircleMarker(
#             [lat, lon],
#             radius=2,
#             stroke=False,
#             fill=True,
#             fill_color="#888",
#             fill_opacity=0.3
#         ).add_to(m)

#     # Overlay green corridor if enabled
#     if enable_cooling:
#         m = render_intervention_map(gdf_edges, gdf_modified, m)

#     m.add_child(folium.LatLngPopup())

#     # Draw markers & route
#     if st.session_state.raw_start:
#         folium.Marker(st.session_state.raw_start, icon=folium.Icon(color="green")).add_to(m)
#     if st.session_state.raw_end:
#         folium.Marker(st.session_state.raw_end, icon=folium.Icon(color="red")).add_to(m)
#     if st.session_state.route:
#         folium.PolyLine(st.session_state.route, color="blue", weight=4).add_to(m)

#     # Capture clicks
#     click = st_folium(m, width=700, height=500)
#     if click and click.get("last_clicked"):
#         lat = round(click["last_clicked"]["lat"], 6)
#         lon = round(click["last_clicked"]["lng"], 6)
#         node = snap_to_nearest_edge(G, lat, lon)
#         n_lon, n_lat = G.nodes[node]["coord"]

#         if st.session_state.raw_start is None:
#             st.session_state.raw_start = (lat, lon)
#             st.session_state.start_node = node
#             st.session_state.start_pt = (n_lat, n_lon)
#             st.success(f"✅ Start set at ({lat}, {lon})")
#         elif st.session_state.raw_end is None:
#             st.session_state.raw_end = (lat, lon)
#             st.session_state.end_node = node
#             st.session_state.end_pt = (n_lat, n_lon)
#             st.success(f"✅ End set at ({lat}, {lon})")
#         else:
#             for k in ("raw_start", "raw_end", "start_node", "end_node",
#                       "start_pt", "end_pt", "route", "distance_km", "avg_cool"):
#                 st.session_state[k] = None
#             st.info("🔄 Resetting points")

#     # Compute & draw route
#     if st.session_state.raw_start and st.session_state.raw_end:
#         weight = "cool_score" if routing_mode == "Coolest Path" else "length"
#         try:
#             path_nodes = nx.shortest_path(
#                 G,
#                 st.session_state.start_node,
#                 st.session_state.end_node,
#                 weight=weight
#             )
#             route = stitch_path(
#                 G,
#                 path_nodes,
#                 raw_start=st.session_state.raw_start,
#                 raw_end=st.session_state.raw_end
#             )
#             st.session_state.route = route

#             line = LineString([(lon, lat) for lat, lon in route])
#             st.session_state.distance_km = round(line.length * 111, 2)
#             cool_vals = [
#                 G.edges[u, v]["cool_score"]
#                 for u, v in zip(path_nodes[:-1], path_nodes[1:])
#             ]
#             st.session_state.avg_cool = round(float(np.mean(cool_vals)), 3)
#         except Exception as e:
#             st.error(f"Routing failed: {e}")

#     # Display metrics
#     if st.session_state.distance_km is not None:
#         st.metric("🚶 Distance (km)", st.session_state.distance_km)
#     if st.session_state.avg_cool is not None:
#         st.metric("🌡️ Avg Cool Score", st.session_state.avg_cool)
#     if enable_cooling:
#         st.metric("🌳 Total Trees Added", total_trees)
#         st.metric("💰 Total Cost (INR)", total_cost)
#         st.metric("📈 Avg Δ Cool Score", round(avg_delta_score, 4))

#     if st.button("Reset Points"):
#         for k in ("raw_start", "raw_end", "start_node", "end_node",
#                   "start_pt", "end_pt", "route", "distance_km", "avg_cool"):
#             st.session_state[k] = None

# # -------- Page 2: Environmental Layers --------

# elif page == "Environmental Layers":
#     st.title("🗺️ Environmental Layer Viewer")
#     layer = st.selectbox("Select Layer to View", ["NDVI", "LST", "Wind", "NDBI"])

#     layer_files = {
#         "NDVI": r"C:\Projects\urban_heat\data\sectionII\NDVI_II.tif",
#         "LST": r"C:\Projects\urban_heat\data\sectionII\LST_II.tif",
#         "Wind": r"C:\Projects\urban_heat\data\sectionII\Wind_II.tif",
#         "NDBI": r"C:\Projects\urban_heat\data\sectionII\NDBI_II.tif"
#     }

#     colormaps = {
#         "NDVI": "Greens",
#         "LST": "hot",
#         "Wind": "Blues",
#         "NDBI": "Greys"
#     }

#     tif_path = layer_files.get(layer)
#     cmap = colormaps.get(layer, "viridis")

#     try:
#         folium_map = render_raster_on_map(tif_path, colormap=cmap, layer_name=layer)
#         st_data = st_folium(folium_map, width=700, height=550)
#     except Exception as e:
#         st.error(f"Failed to render {layer} layer: {e}")

# # -------- Page 3: UHI Segmentation --------

# elif page == "UHI Segmentation":
#     st.title("🔥 Urban Heat Island Segmentation")
#     st.markdown("Upload NDVI and LST raster files.")

#     ndvi_file = st.file_uploader("📥 Upload NDVI .tif", type=["tif"], key="ndvi_upload_simple")
#     lst_file = st.file_uploader("📥 Upload LST .tif", type=["tif"], key="lst_upload_simple")

#     show_overlay = st.button("🧊 Show UHI Overlay")

#     if ndvi_file and lst_file:
#         ndvi_path = "data/clipped/ndvi_clipped.tif"
#         lst_path = "data/clipped/lst_clipped.tif"
#         os.makedirs("data/clipped", exist_ok=True)

#         with open(ndvi_path, "wb") as f:
#             f.write(ndvi_file.read())
#         with open(lst_path, "wb") as f:
#             f.write(lst_file.read())

#         st.success("✅ Files uploaded and saved to data/clipped/")

#         if show_overlay:
#             image_path = "data/clipped/uhi_ndvi_overlay.png"
#             if os.path.exists(image_path):
#                 from PIL import Image
#                 st.image(Image.open(image_path), caption="UHI NDVI Overlay", use_container_width=True)
#                 with open(image_path, "rb") as img_file:
#                     st.download_button(
#                         label="⬇️ Download Overlay Image",
#                         data=img_file,
#                         file_name="uhi_ndvi_overlay.png",
#                         mime="image/png"
#                     )
#             else:
#                 st.warning("⚠️ Overlay image not found at data/clipped/uhi_ndvi_overlay.png.")
#     elif show_overlay:
#         st.error("❗ Please upload both NDVI and LST files before displaying the overlay.")


import streamlit as st
import geopandas as gpd
import networkx as nx
import numpy as np
import folium
from shapely.geometry import LineString, Point
from streamlit_folium import st_folium
from cooling_intervention import apply_intervention, render_intervention_map, export_intervention_geojson
import rasterio
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from PIL import Image
import io
import base64
import os
from folium import raster_layers
from folium.raster_layers import ImageOverlay
from shapely.geometry import mapping
import json

# -------- Configuration --------
# GRAPH_PATH = r"/Users/tarunb/Documents/SDG_EL/from_scratch/Urban_cooling/data/enriched/enriched_graph_scored.gpkg"
GRAPH_PATH = r"C:\Projects\urban_heat\data\enriched\enriched_graph_scored.gpkg"
# -------- Utility Functions --------
@st.cache_data
def load_graph_and_gdf(path):
    gdf = gpd.read_file(path).to_crs(epsg=4326)
    gdf["cool_score"] = gdf["cool_score"].fillna(gdf["cool_score"].median())

    G = nx.Graph()
    node_coords = {}
    for _, row in gdf.iterrows():
        u, v = row.u, row.v
        geom = row.geometry
        if geom.geom_type == "MultiLineString":
            geom = max(geom.geoms, key=lambda g: g.length)
        if geom.geom_type != "LineString":
            continue

        lon0, lat0 = geom.coords[0]
        lon1, lat1 = geom.coords[-1]
        node_coords[u] = (lon0, lat0)
        node_coords[v] = (lon1, lat1)

        G.add_node(u, coord=(lon0, lat0))
        G.add_node(v, coord=(lon1, lat1))
        G.add_edge(u, v,
                   geometry=geom,
                   length=geom.length,
                   cool_score=row.cool_score)

    return gdf, G, node_coords

def snap_to_nearest_edge(G, click_lat, click_lon):
    pt = Point(click_lon, click_lat)
    best_dist = float("inf")
    best_edge = None
    for u, v, data in G.edges(data=True):
        d = data["geometry"].distance(pt)
        if d < best_dist:
            best_dist = d
            best_edge = (u, v)
    if best_edge is None:
        return None
    u, v = best_edge
    u_pt = Point(*G.nodes[u]["coord"][::-1])
    v_pt = Point(*G.nodes[v]["coord"][::-1])
    return u if pt.distance(u_pt) < pt.distance(v_pt) else v

def stitch_path(G, path_nodes, raw_start=None, raw_end=None):
    pts = []
    if raw_start:
        pts.append(raw_start)
    seen = set()
    for u, v in zip(path_nodes[:-1], path_nodes[1:]):
        key = tuple(sorted((u, v)))
        if key in seen:
            continue
        seen.add(key)
        line = G.edges[u, v]["geometry"]
        seg = [(lat, lon) for lon, lat in line.coords]
        if pts and pts[-1] == seg[0]:
            seg = seg[1:]
        pts.extend(seg)
    if raw_end:
        pts.append(raw_end)
    return pts

def render_raster_on_map(tif_path, colormap='Greens', layer_name="Environmental Layer"):
    with rasterio.open(tif_path) as src:
        data = src.read(1, masked=True)
        bounds = src.bounds

    norm = Normalize(vmin=float(data.min()), vmax=float(data.max()))
    cmap = plt.get_cmap(colormap)
    rgba_img = cmap(norm(data.filled(0)))
    img = Image.fromarray((rgba_img[:, :, :3] * 255).astype('uint8'))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    base64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
    img_url = f"data:image/png;base64,{base64_img}"

    center_lat = (bounds.top + bounds.bottom) / 2
    center_lon = (bounds.left + bounds.right) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
    ImageOverlay(
        image=img_url,
        bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
        opacity=0.6,
        name=layer_name,
        interactive=True,
        cross_origin=False
    ).add_to(m)
    folium.LayerControl().add_to(m)
    return m

def export_route_geojson(route_coords, filename="outputs/route.geojson"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    line = LineString([(lon, lat) for lat, lon in route_coords])
    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": mapping(line),
            "properties": {
                "name": "Optimized Route"
            }
        }]
    }
    with open(filename, "w") as f:
        json.dump(geojson, f)
    return filename

# -------- Streamlit App --------
st.set_page_config(page_title="Urban Microclimate Simulator", layout="wide")

PAGES = ["Corridor Optimizer", "Environmental Layers", "UHI Segmentation"]
page = st.sidebar.selectbox("Navigate", PAGES)

# -------- Page 1: Optimizer --------
if page == "Corridor Optimizer":
    with st.sidebar:
        st.markdown("### 🔧 Route Configuration")
        poi_list = ["Ulsoor Lake", "Domlur Flyover", "MG Road", "Cubbon Park"]
        start_loc = st.selectbox("Start Location", poi_list)
        end_loc   = st.selectbox("End Location", poi_list, index=1)
        routing_mode = st.radio("Routing Mode", ("Shortest Path", "Coolest Path"))
        enable_cooling = st.checkbox("🌳 Enable Cooling Intervention", value=True)
        intervention = st.selectbox("Type of Intervention", ("Add Trees", "Cool Roofs"))
        intensity = st.slider("Intensity", 0.0, 1.0, 0.2, 0.01)
        st.markdown("---")
        if st.button("📥 Export Route GeoJSON"):
            if st.session_state.route:
                out_path = "outputs/route.geojson"
                export_route_geojson(st.session_state.route, out_path)
                with open(out_path, "rb") as f:
                    st.download_button(
                    "⬇️ Download Route GeoJSON",
                    f,
                    file_name="optimized_route.geojson",
                    mime="application/geo+json"
                )
            else:
                st.warning("⚠️ No route available to export. Please select start and end points first.")

    st.title("Urban Cool Corridor Optimizer")
    gdf_edges, G, node_coords = load_graph_and_gdf(GRAPH_PATH)

    if enable_cooling:
        gdf_modified, total_trees, total_cost, avg_delta_score = apply_intervention(
            gdf_edges, intervention, intensity
        )
    else:
        gdf_modified = gdf_edges
        total_trees = total_cost = avg_delta_score = None

    if enable_cooling and st.sidebar.button("📥 Download ΔScore Map"):
        os.makedirs("outputs", exist_ok=True)
        out_path = "outputs/intervention_delta.geojson"
        try:
            geojson_file = export_intervention_geojson(gdf_edges, gdf_modified, out_path)
            with open(geojson_file, "rb") as f:
                st.sidebar.download_button(
                    "⬇️ Save ΔScore GeoJSON",
                    f,
                    file_name="cooling_intervention.geojson",
                    mime="application/geo+json"
                )
        except Exception as e:
            st.sidebar.error(f"Failed to export GeoJSON: {e}")

    # Initialize session state
    for key in ("raw_start", "raw_end", "start_node", "end_node",
                "start_pt", "end_pt", "route", "distance_km", "avg_cool"):
        st.session_state.setdefault(key, None)

    # Build base map
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=13)
    folium.GeoJson(
        gdf_edges,
        style_function=lambda f: {"color": "#ccc", "weight": 1, "opacity": 0.6}
    ).add_to(m)
    for lon, lat in node_coords.values():
        folium.CircleMarker(
            [lat, lon],
            radius=2,
            stroke=False,
            fill=True,
            fill_color="#888",
            fill_opacity=0.3
        ).add_to(m)

    # Overlay green corridor if enabled
    if enable_cooling:
        m = render_intervention_map(gdf_edges, gdf_modified, m, intervention_type=intervention)


    m.add_child(folium.LatLngPopup())

    # Draw markers & route
    if st.session_state.raw_start:
        folium.Marker(st.session_state.raw_start, icon=folium.Icon(color="green")).add_to(m)
    if st.session_state.raw_end:
        folium.Marker(st.session_state.raw_end, icon=folium.Icon(color="red")).add_to(m)
    if st.session_state.route:
        folium.PolyLine(st.session_state.route, color="blue", weight=4).add_to(m)

    # Capture clicks
    click = st_folium(m, width=700, height=500)
    if click and click.get("last_clicked"):
        lat = round(click["last_clicked"]["lat"], 6)
        lon = round(click["last_clicked"]["lng"], 6)
        node = snap_to_nearest_edge(G, lat, lon)
        n_lon, n_lat = G.nodes[node]["coord"]

        if st.session_state.raw_start is None:
            st.session_state.raw_start = (lat, lon)
            st.session_state.start_node = node
            st.session_state.start_pt = (n_lat, n_lon)
            st.success(f"✅ Start set at ({lat}, {lon})")
        elif st.session_state.raw_end is None:
            st.session_state.raw_end = (lat, lon)
            st.session_state.end_node = node
            st.session_state.end_pt = (n_lat, n_lon)
            st.success(f"✅ End set at ({lat}, {lon})")
        else:
            for k in ("raw_start", "raw_end", "start_node", "end_node",
                      "start_pt", "end_pt", "route", "distance_km", "avg_cool"):
                st.session_state[k] = None
            st.info("🔄 Resetting points")

    # Compute & draw route
    if st.session_state.raw_start and st.session_state.raw_end:
        weight = "cool_score" if routing_mode == "Coolest Path" else "length"
        try:
            path_nodes = nx.shortest_path(
                G,
                st.session_state.start_node,
                st.session_state.end_node,
                weight=weight
            )
            route = stitch_path(
                G,
                path_nodes,
                raw_start=st.session_state.raw_start,
                raw_end=st.session_state.raw_end
            )
            st.session_state.route = route

            line = LineString([(lon, lat) for lat, lon in route])
            st.session_state.distance_km = round(line.length * 111, 2)
            cool_vals = [
                G.edges[u, v]["cool_score"]
                for u, v in zip(path_nodes[:-1], path_nodes[1:])
            ]
            st.session_state.avg_cool = round(float(np.mean(cool_vals)), 3)
        except Exception as e:
            st.error(f"Routing failed: {e}")

    # Display metrics
    if st.session_state.distance_km is not None:
        st.metric("🚶 Distance (km)", st.session_state.distance_km)
    if st.session_state.avg_cool is not None:
        st.metric("🌡️ Avg Cool Score", st.session_state.avg_cool)
    if enable_cooling:
        st.metric("🌳 Total Trees Added", total_trees)
        st.metric("💰 Total Cost (INR)", total_cost)
        if avg_delta_score is not None:
            st.metric("📈 Avg Δ Cool Score", round(avg_delta_score, 4))
        else:
            st.metric("📈 Avg Δ Cool Score", "N/A")

    if st.button("Reset Points"):
        for k in ("raw_start", "raw_end", "start_node", "end_node",
                  "start_pt", "end_pt", "route", "distance_km", "avg_cool"):
            st.session_state[k] = None

# -------- Page 2: Environmental Layers --------
elif page == "Environmental Layers":
    st.title("🗺️ Environmental Layer Viewer")
    layer = st.selectbox("Select Layer to View", ["NDVI", "LST", "Wind", "NDBI"])
    layer_files = {
        "NDVI": r"C:\Projects\urban_heat\data\sectionII\NDVI_II.tif",
        "LST": r"C:\Projects\urban_heat\data\sectionII\LST_II.tif",
        "Wind": r"C:\Projects\urban_heat\data\sectionII\Wind_II.tif",
        "NDBI": r"C:\Projects\urban_heat\data\sectionII\NDBI_II.tif"
    }
    colormaps = {
        "NDVI": "Greens",
        "LST": "hot",
        "Wind": "Blues",
        "NDBI": "Greys"
    }
    tif_path = layer_files.get(layer)
    cmap = colormaps.get(layer, "viridis")
    try:
        fol_map = render_raster_on_map(tif_path, colormap=cmap, layer_name=layer)
        st_folium(fol_map, width=700, height=550)
    except Exception as e:
        st.error(f"Failed to render {layer} layer: {e}")

# -------- Page 3: UHI Segmentation --------
elif page == "UHI Segmentation":
    st.title("🔥 Urban Heat Island Segmentation")
    st.markdown("Upload NDVI and LST raster files.")

    ndvi_file = st.file_uploader("📥 Upload NDVI .tif", type=["tif"], key="ndvi_upload_simple")
    lst_file = st.file_uploader("📥 Upload LST .tif", type=["tif"], key="lst_upload_simple")

    show_overlay = st.button("🧊 Show UHI Overlay")

    if ndvi_file and lst_file:
        ndvi_path = "data/clipped/ndvi_clipped.tif"
        lst_path = "data/clipped/lst_clipped.tif"
        os.makedirs("data/clipped", exist_ok=True)

        with open(ndvi_path, "wb") as f:
            f.write(ndvi_file.read())
        with open(lst_path, "wb") as f:
            f.write(lst_file.read())

        st.success("✅ Files uploaded and saved to data/clipped/")

        if show_overlay:
            image_path = "data/clipped/uhi_ndvi_overlay.png"
            if os.path.exists(image_path):
                from PIL import Image
                st.image(Image.open(image_path), caption="UHI NDVI Overlay", use_container_width=True)
                with open(image_path, "rb") as img_file:
                    st.download_button(
                        label="⬇️ Download Overlay Image",
                        data=img_file,
                        file_name="uhi_ndvi_overlay.png",
                        mime="image/png"
                    )
            else:
                st.warning("⚠️ Overlay image not found at data/clipped/uhi_ndvi_overlay.png.")
    elif show_overlay:
        st.error("❗ Please upload both NDVI and LST files before displaying the overlay.")

