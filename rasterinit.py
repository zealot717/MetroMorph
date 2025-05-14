import rasterio
import numpy as np
import matplotlib.pyplot as plt

# File paths
ndvi_path = 'data/bangalore_ndvi.tif'
ndbi_path = 'data/bangalore_ndbi.tif'
lst_path  = 'data/bangalore_lst.tif'

# Read NDVI
with rasterio.open(ndvi_path) as ndvi_src:
    ndvi = ndvi_src.read(1)
    ndvi_nodata = ndvi_src.nodata

# Read NDBI
with rasterio.open(ndbi_path) as ndbi_src:
    ndbi = ndbi_src.read(1)
    ndbi_nodata = ndbi_src.nodata

# Read LST
with rasterio.open(lst_path) as lst_src:
    lst = lst_src.read(1)
    lst_nodata = lst_src.nodata

# Mask out invalid values from all three rasters
valid_mask = (
    (ndvi != ndvi_nodata) & ~np.isnan(ndvi) &
    (ndbi != ndbi_nodata) & ~np.isnan(ndbi) &
    (lst != lst_nodata)   & ~np.isnan(lst)
)

ndvi_clean = ndvi[valid_mask]
ndbi_clean = ndbi[valid_mask]
lst_clean  = lst[valid_mask]

# Summary statistics
print("NDVI:", np.nanmin(ndvi_clean), "to", np.nanmax(ndvi_clean))
print("NDBI:", np.nanmin(ndbi_clean), "to", np.nanmax(ndbi_clean))
print("LST (K):", np.nanmin(lst_clean), "to", np.nanmax(lst_clean))

# Correlation analysis
ndvi_lst_corr = np.corrcoef(ndvi_clean, lst_clean)[0, 1]
ndbi_lst_corr = np.corrcoef(ndbi_clean, lst_clean)[0, 1]

print(f"\nCorrelation (NDVI vs LST): {ndvi_lst_corr:.3f}")
print(f"Correlation (NDBI vs LST): {ndbi_lst_corr:.3f}")

# Optional: Plot histograms
plt.figure(figsize=(15, 4))
plt.subplot(1, 3, 1)
plt.hist(ndvi_clean, bins=50, color='green')
plt.title('NDVI Distribution')

plt.subplot(1, 3, 2)
plt.hist(ndbi_clean, bins=50, color='gray')
plt.title('NDBI Distribution')

plt.subplot(1, 3, 3)
plt.hist(lst_clean, bins=50, color='red')
plt.title('LST Distribution (K)')
plt.tight_layout()
plt.show()
