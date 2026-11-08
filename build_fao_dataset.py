import pandas as pd
import numpy as np

# same thresholds as before: agree these as a group
WET_MONTH_MM, HOT_MONTH_C, FROST_C = 150, 25, 0

# ---- 1. yearly weather, ALL years (no 2008 cut-off) ----
weather = pd.read_csv("cork_weather_monthly.csv")
rows = []
for (station, year), g in weather.groupby(["station_no", "year"]):
    grow = g[g["month"].between(4, 9)]
    full = lambda col, n: g[col].count() == n
    rows.append({
        "station_no": station, "year": year,
        "grow_mean_temp": grow["meant"].mean() if grow["meant"].count() == 6 else None,
        "grow_rain_mm": grow["rain"].sum() if grow["rain"].count() == 6 else None,
        "grow_sun_hrs": grow["sun"].sum() if grow["sun"].count() == 6 else None,
        "annual_rain_mm": g["rain"].sum() if full("rain", 12) else None,
        "wet_months": (g["rain"] > WET_MONTH_MM).sum() if full("rain", 12) else None,
        "hot_months": (g["maxtp"] >= HOT_MONTH_C).sum() if full("maxtp", 12) else None,
        "frost_months": (g["mintp"] < FROST_C).sum() if full("mintp", 12) else None,
        "year_max_temp": g["maxtp"].max() if full("maxtp", 12) else None,
        "year_min_temp": g["mintp"].min() if full("mintp", 12) else None,
    })
per_station = pd.DataFrame(rows)
yearly = per_station.drop(columns="station_no").groupby("year").mean().reset_index()
yearly["stations_used"] = per_station.groupby("year")["station_no"].nunique().values

# ---- 2. clean the FAO file ----
fao = pd.read_csv("fao/fao_yield.csv", encoding="utf-8-sig")
fao.columns = [c.strip() for c in fao.columns]
fao = fao[["Item", "Year", "Value"]].rename(columns={"Item": "crop", "Year": "year", "Value": "yield_raw"})
fao["crop"] = fao["crop"].str.strip().str.lower()
fao["yield_t_per_ha"] = pd.to_numeric(fao["yield_raw"], errors="coerce") / 1000   # kg/ha -> t/ha
fao = fao.drop(columns="yield_raw").dropna(subset=["yield_t_per_ha"])

# ---- 3. sanity check against CSO for 2008 onwards ----
cso = pd.read_csv("crops_clean.csv")
pairs = {"wheat": "total wheat", "barley": "total barley", "oats": "total oats", "potatoes": "potatoes"}
print("FAO vs CSO yield, 2008 onwards (mean absolute difference, t/ha):")
for fao_name, cso_name in pairs.items():
    a = fao[(fao.crop == fao_name) & (fao.year >= 2008)].set_index("year")["yield_t_per_ha"]
    b = cso[cso.crop == cso_name].set_index("year")["yield_t_per_ha"]
    both = pd.concat([a, b], axis=1, keys=["fao", "cso"]).dropna()
    print(f"  {fao_name}: {len(both)} years, difference {abs(both.fao - both.cso).mean():.2f}")

# ---- 4. yield relative to each crop's trend ----
parts = []
for crop_name, g in fao.groupby("crop"):
    g = g.copy()
    slope, intercept = np.polyfit(g["year"], g["yield_t_per_ha"], 1)
    g["yield_vs_trend_pct"] = (g["yield_t_per_ha"] / (slope * g["year"] + intercept) - 1) * 100
    parts.append(g)
fao = pd.concat(parts, ignore_index=True)

# ---- 5. join and save ----
dataset = fao.merge(yearly, on="year", how="left").sort_values(["crop", "year"])
dataset.to_csv("fao_weather_dataset.csv", index=False)

print(f"\nSaved {len(dataset)} rows, {len(dataset.columns)} columns to fao_weather_dataset.csv")
print(f"Crops: {dataset.crop.nunique()}, years {int(dataset.year.min())}-{int(dataset.year.max())}")
print("\nMissing values:")
print(dataset.isna().sum())