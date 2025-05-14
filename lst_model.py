import rasterio
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# --- Paths ---
data_dir = 'data'  # Adjust if needed
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

ndvi_path = os.path.join(data_dir, 'bangalore_ndvi.tif')
ndbi_path = os.path.join(data_dir, 'bangalore_ndbi.tif')
lst_path = os.path.join(data_dir, 'bangalore_lst.tif')

# --- Load GeoTIFFs ---
def load_band(path):
    with rasterio.open(path) as src:
        return src.read(1), src.profile

ndvi, profile = load_band(ndvi_path)
ndbi, _ = load_band(ndbi_path)
lst, _ = load_band(lst_path)

# --- Flatten & Stack Data ---
mask = ~np.isnan(ndvi) & ~np.isnan(ndbi) & ~np.isnan(lst)
X = np.stack([ndvi[mask], ndbi[mask]], axis=1)
y = lst[mask]

# --- Train Regression Model ---
model = LinearRegression()
model.fit(X, y)

print("Model coefficients:", model.coef_)
print("Model intercept:", model.intercept_)
print("Training RMSE:", np.sqrt(mean_squared_error(y, model.predict(X))))

# --- Simulate Greening (increase NDVI by 0.1 where possible) ---
ndvi_simulated = ndvi.copy()
greening_mask = (ndvi > 0) & (ndvi < 0.6)  # Adjust based on context
ndvi_simulated[greening_mask] += 0.1
ndvi_simulated = np.clip(ndvi_simulated, 0, 1)

# --- Predict New LST ---
X_simulated = np.stack([ndvi_simulated[mask], ndbi[mask]], axis=1)
lst_predicted_flat = model.predict(X_simulated)

lst_predicted = np.full_like(lst, np.nan)
lst_predicted[mask] = lst_predicted_flat

# --- Compute Delta LST (Cooling) ---
delta_lst = lst - lst_predicted

# --- Save Outputs ---
def save_band(array, ref_profile, path):
    profile = ref_profile.copy()
    profile.update(dtype=rasterio.float32, count=1, compress='lzw')
    with rasterio.open(path, 'w', **profile) as dst:
        dst.write(array.astype(rasterio.float32), 1)

save_band(ndvi_simulated, profile, os.path.join(output_dir, 'simulated_NDVI.tif'))
save_band(lst_predicted, profile, os.path.join(output_dir, 'predicted_LST.tif'))
save_band(delta_lst, profile, os.path.join(output_dir, 'delta_LST.tif'))

# --- Quick Visualization (Optional) ---
plt.figure(figsize=(10, 5))
plt.subplot(1, 3, 1)
plt.title("Original LST")
plt.imshow(lst, cmap='inferno')
plt.colorbar()

plt.subplot(1, 3, 2)
plt.title("Predicted LST")
plt.imshow(lst_predicted, cmap='inferno')
plt.colorbar()

plt.subplot(1, 3, 3)
plt.title("Δ LST (Cooling Effect)")
plt.imshow(delta_lst, cmap='RdYlBu_r')
plt.colorbar()

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'lst_simulation_summary.png'))
plt.show()
