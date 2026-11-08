import pandas as pd
import numpy as np

fao = pd.read_csv("fao_weather_dataset.csv").drop(columns="yield_vs_trend_pct")
cso = pd.read_csv("crop_weather_dataset.csv")

fao["source"] = "FAO"
cso["source"] = "CSO"

# 1. CSO rows for the 4 long-history crops, only for years FAO doesn't cover (2025)
long_map = {"total wheat": "wheat", "total barley": "barley",
            "total oats": "oats", "potatoes": "potatoes"}
extend = cso[cso["crop"].isin(long_map) & (cso["year"] > fao["year"].max())].copy()
extend["crop"] = extend["crop"].map(long_map)

# 2. CSO-only crops (no FAO equivalent)
only_cso = ["beans and peas", "oilseed rape",
            "winter wheat", "spring wheat",
            "winter barley", "spring barley",
            "winter oats", "spring oats"]
extra = cso[cso["crop"].isin(only_cso)].copy()

combined = pd.concat([fao, extend, extra], ignore_index=True)

# 3. recompute yield vs trend per crop on the combined series
parts = []
for crop, g in combined.groupby("crop"):
    g = g.copy()
    slope, intercept = np.polyfit(g["year"], g["yield_t_per_ha"], 1)
    g["yield_vs_trend_pct"] = (g["yield_t_per_ha"] / (slope * g["year"] + intercept) - 1) * 100
    parts.append(g)
combined = pd.concat(parts, ignore_index=True).sort_values(["crop", "year"])

combined.to_csv("combined_dataset.csv", index=False)

print(f"Saved {len(combined)} rows, {len(combined.columns)} columns to combined_dataset.csv")
print("\nRows per crop:")
print(combined.groupby("crop").agg(rows=("year", "size"),
                                   first=("year", "min"),
                                   last=("year", "max"),
                                   source=("source", lambda s: "/".join(sorted(set(s))))).to_string())