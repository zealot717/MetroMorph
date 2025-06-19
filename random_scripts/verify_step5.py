# random_scripts/verify_step5.py

import geopandas as gpd
import matplotlib.pyplot as plt

def main():
    print("🔍 Verifying enriched clipped graph...")

    # Load enriched graph (edges should have NDVI and LST columns)
    enriched = gpd.read_file("data/enriched/enriched_graph.gpkg")

    assert 'mean_ndvi' in enriched.columns, "❌ 'mean_ndvi' column missing!"
    assert 'mean_lst' in enriched.columns, "❌ 'mean_lst' column missing!"
    
    print(f"✅ Loaded {len(enriched)} enriched road segments.")

    # Print summary stats
    print("\n📊 Enrichment Statistics:")
    print(f"NDVI - min: {enriched['mean_ndvi'].min()}, max: {enriched['mean_ndvi'].max()}, mean: {enriched['mean_ndvi'].mean()}")
    print(f"LST  - min: {enriched['mean_lst'].min()}, max: {enriched['mean_lst'].max()}, mean: {enriched['mean_lst'].mean()}")

    # Plot to visually verify spatial variation
    fig, ax = plt.subplots(1, 2, figsize=(14, 7))
    enriched.plot(ax=ax[0], column='mean_ndvi', legend=True, cmap='RdYlGn')
    ax[0].set_title("🟢 NDVI per Edge")
    enriched.plot(ax=ax[1], column='mean_lst', legend=True, cmap='inferno')
    ax[1].set_title("🔥 LST per Edge")
    for a in ax:
        a.axis('off')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
