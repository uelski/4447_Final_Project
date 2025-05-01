#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

# -----------------------------------------------------------------------------
# 0. SETUP
# -----------------------------------------------------------------------------
sns.set_theme(style="whitegrid", palette="deep")

# -----------------------------------------------------------------------------
# 1. CRIME MAP VISUALIZATION
# -----------------------------------------------------------------------------
# 1a. Load neighborhood boundaries
shp_path = "data/neighborhoods/ADMN_NEIGHBORHOOD_A.shp"
denver_neighborhoods = gpd.read_file(shp_path)

# 1b. Standardize the GeoDataFrame key
denver_neighborhoods["NBHD_NAME_STD"] = (
    denver_neighborhoods["NBHD_NAME"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# 1c. Load your attribute data
neighborhood_data = pd.DataFrame({
    "name": [
        "Five Points", "Capitol Hill", "Highland", "Cherry Creek",
        "Washington Park", "Montbello", "Gateway-Green Valley Ranch", "Auraria"
    ],
    "crimeRate": [85, 78, 45, 32, 25, 68, 52, 55],
    "afterSchoolPrograms": [5, 8, 15, 22, 18, 7, 9, 5],
    "equityScore": [2.1, 3.2, 3.8, 4.5, 4.8, 2.3, 2.9, 3.1]
})

# 1d. Standardize the DataFrame key
neighborhood_data["name_std"] = (
    neighborhood_data["name"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# 1e. Merge (inner join keeps only matching neighborhoods)
denver_data = denver_neighborhoods.merge(
    neighborhood_data,
    how="inner",
    left_on="NBHD_NAME_STD",
    right_on="name_std"
)

# 1f. Plot choropleth
fig, ax = plt.subplots(figsize=(10, 8))
cmap = "RdYlGn_r"
denver_data.plot(
    column="crimeRate",
    cmap=cmap,
    linewidth=0.8,
    edgecolor="0.8",
    ax=ax,
    legend=False
)
ax.set_title("Denver Neighborhood Crime Rates", fontsize=16)
ax.set_axis_off()

# 1g. Custom colorbar
vmin, vmax = denver_data["crimeRate"].min(), denver_data["crimeRate"].max()
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label("Crime Rate per 1,000 Residents")

# 1h. Add neighborhood labels
denver_data["coords"] = denver_data.geometry.apply(
    lambda geom: geom.representative_point().coords[:][0]
)
for _, row in denver_data.iterrows():
    ax.annotate(
        row["name"],
        xy=row["coords"],
        fontsize=8,
        ha="center",
        weight="bold"
    )

plt.tight_layout()
plt.savefig("denver_crime_map_labeled.png", dpi=300)
plt.show()


# -----------------------------------------------------------------------------
# 2. CORRELATION SCATTER PLOT
# -----------------------------------------------------------------------------
plt.figure(figsize=(10, 8))
sns.regplot(
    x="afterSchoolPrograms",
    y="crimeRate",
    data=neighborhood_data,
    scatter_kws={"s": 100, "alpha": 0.7},
    line_kws={"color": "red", "linestyle": "--"}
)

# annotate each point
for i, txt in enumerate(neighborhood_data["name"]):
    x = neighborhood_data.at[i, "afterSchoolPrograms"]
    y = neighborhood_data.at[i, "crimeRate"]
    plt.annotate(txt, (x, y), fontsize=10, xytext=(5, 5), textcoords="offset points")

# correlation annotation repositioned to lower right
corr = neighborhood_data["afterSchoolPrograms"].corr(neighborhood_data["crimeRate"])
plt.annotate(
    f"Correlation: {corr:.2f}",
    xy=(0.95, 0.05),
    xycoords="axes fraction",
    fontsize=12,
    ha="right",
    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
)

plt.title("Relationship Between After-School Programs and Crime Rates", fontsize=16)
plt.xlabel("Number of After-School Programs", fontsize=12)
plt.ylabel("Crime Rate per 1,000 Residents", fontsize=12)
plt.tight_layout()
plt.savefig("program_crime_correlation.png", dpi=300)
plt.show()


# -----------------------------------------------------------------------------
# 3. EQUITY vs CRIME BAR & LINE CHART
# -----------------------------------------------------------------------------
selected = [
    "Five Points", "Capitol Hill", "Highland",
    "Cherry Creek", "Washington Park", "Montbello"
]
subset = neighborhood_data[neighborhood_data["name"].isin(selected)]

fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()

# equity scores
ax1.bar(
    subset["name"],
    subset["equityScore"],
    color="steelblue",
    alpha=0.7,
    label="Equity Score"
)
ax1.set_xlabel("Neighborhood")
ax1.set_ylabel("Equity Score (1–5)", color="steelblue")
ax1.tick_params(axis="y", labelcolor="steelblue")
ax1.set_ylim(0, 5.5)

# crime rate line
ax2.plot(
    subset["name"],
    subset["crimeRate"],
    "ro-",
    label="Crime Rate"
)
ax2.set_ylabel("Crime Rate per 1,000", color="red")
ax2.tick_params(axis="y", labelcolor="red")

plt.title("Comparison of Equity Scores and Crime Rates by Neighborhood", fontsize=16)
plt.xticks(rotation=45, ha="right")

# combined legend
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper right")

plt.tight_layout()
plt.savefig("equity_crime_comparison.png", dpi=300)
plt.show()
# -----------------------------------------------------------------------------