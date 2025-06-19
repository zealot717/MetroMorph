# random_scripts/verify_step6.py

import geopandas as gpd
import matplotlib.pyplot as plt

def main():
    print("🔎 Verifying Coolness Score Computation...")

    fp = "data/enriched/enriched_graph_scored.gpkg"
    gdf = gpd.read_file(fp)

    assert "cool_score" in gdf.columns, "❌ Missing 'cool_score' column!"
    assert gdf["cool_score"].notnull().all(), "❌ Some cool scores are NaN!"

    print(f"✅ Loaded {len(gdf)} road segments with coolness scores.")
    print(f"📊 Cool Score Stats:\n  - Min: {gdf['cool_score'].min()}\n  - Max: {gdf['cool_score'].max()}\n  - Mean: {gdf['cool_score'].mean()}")

    # Optional histogram
    plt.figure(figsize=(8, 5))
    gdf["cool_score"].hist(bins=30, color="skyblue", edgecolor="black")
    plt.title("Distribution of Coolness Scores")
    plt.xlabel("Coolness Score (0 = Hot, 1 = Cool)")
    plt.ylabel("Number of Segments")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
