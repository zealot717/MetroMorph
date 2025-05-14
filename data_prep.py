import ee
import geemap
import datetime

# Initialize the Earth Engine API
# ee.Authenticate()
ee.Initialize(project='halogen-welder-459104-v5') 

# Define AOI – Bengaluru bounding box
aoi = ee.Geometry.Rectangle([77.4, 12.8, 77.75, 13.15])

# Define time range
start_date = '2023-01-01'
end_date = '2023-12-31'

# Sentinel-2 NDVI
sentinel = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
    .filterDate(start_date, end_date) \
    .filterBounds(aoi) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
    .median()

ndvi = sentinel.normalizedDifference(['B8', 'B4']).rename('NDVI').toFloat()

# Landsat 8 LST approximation
landsat = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
    .filterDate(start_date, end_date) \
    .filterBounds(aoi) \
    .filter(ee.Filter.lt('CLOUD_COVER', 10)) \
    .median()

lst = landsat.select('ST_B10').multiply(0.00341802).add(149.0).rename('LST').toFloat()

# NDBI = (SWIR - NIR) / (SWIR + NIR)
ndbi = landsat.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI').toFloat()

# Visualize on map (optional)
Map = geemap.Map(center=[12.97, 77.59], zoom=10)
Map.addLayer(ndvi, {'min': 0, 'max': 1, 'palette': ['white', 'green']}, 'NDVI')
Map.addLayer(ndbi, {'min': -1, 'max': 1, 'palette': ['white', 'gray']}, 'NDBI')
Map.addLayer(lst, {'min': 290, 'max': 320, 'palette': ['blue', 'red']}, 'LST (K)')
Map.addLayer(aoi, {}, 'AOI')
Map

# Export all three bands separately
export_region = aoi.bounds().getInfo()['coordinates']

export_tasks = {
    'NDVI': ndvi,
    'NDBI': ndbi,
    'LST': lst
}

for name, image in export_tasks.items():
    task = ee.batch.Export.image.toDrive(
        image=image.clip(aoi),
        description=f'Export_{name}',
        folder='GEE_Exports',
        fileNamePrefix=f'bangalore_{name.lower()}',
        region=export_region,
        scale=30,
        maxPixels=1e13
    )
    task.start()
    print(f"✅ Export started for {name} — check your Google Drive shortly.")
