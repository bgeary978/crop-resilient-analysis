import pandas as pd

# Thresholds: placeholders for your group to agree on (your Epic 3 task)
WET_MONTH_MM = 150    # a month counts as "very wet" above this rainfall
HOT_MONTH_C = 25      # a month counts as "hot" if its max temp reached this
FROST_C = 0           # a month counts as "frost" if its min temp fell below this

weather = pd.read_csv("cork_weather_monthly.csv")
weather = weather[weather["year"] >= 2008]

rows = []
for (station, year), g in weather.groupby(["station_no", "year"]):
    grow = g[g["month"].between(4, 9)]          # April to September
    full_grow = grow["rain"].count() == 6       # all 6 growing months present
    full_year = g["rain"].count() == 12

    rows.append({
        "station_no": station,
        "year": year,
        "grow_mean_temp": grow["meant"].mean() if grow["meant"].count() == 6 else None,
        "grow_rain_mm": grow["rain"].sum() if full_grow else None,
        "grow_sun_hrs": grow["sun"].sum() if grow["sun"].count() == 6 else None,
        "annual_rain_mm": g["rain"].sum() if full_year else None,
        "wet_months": (g["rain"] > WET_MONTH_MM).sum() if full_year else None,
        "hot_months": (g["maxtp"] >= HOT_MONTH_C).sum() if g["maxtp"].count() == 12 else None,
        "frost_months": (g["mintp"] < FROST_C).sum() if g["mintp"].count() == 12 else None,
        "year_max_temp": g["maxtp"].max() if g["maxtp"].count() == 12 else None,
        "year_min_temp": g["mintp"].min() if g["mintp"].count() == 12 else None,
    })

per_station = pd.DataFrame(rows)

# average across stations -> one weather row per year
yearly = per_station.drop(columns="station_no").groupby("year").mean().reset_index()
yearly["stations_used"] = per_station.groupby("year")["station_no"].nunique().values

crops = pd.read_csv("crops_clean.csv")
dataset = crops.merge(yearly, on="year", how="left")
dataset.to_csv("crop_weather_dataset.csv", index=False)

print(f"Saved {len(dataset)} rows, {len(dataset.columns)} columns to crop_weather_dataset.csv")
print("\nMissing values:")
print(dataset.isna().sum())
print("\nWeather by year:")
print(yearly.round(1).to_string(index=False))