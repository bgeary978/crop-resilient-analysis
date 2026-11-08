import pandas as pd

df = pd.read_csv("combined_dataset.csv")
weather = pd.read_csv("cork_weather_monthly.csv")

# ---- seasonal features (averaged across stations, monthly first) ----
monthly = weather.groupby(["year", "month"])[["meant", "rain", "sun", "maxtp", "mintp"]].mean().reset_index()

def season(months, col, how):
    g = monthly[monthly["month"].isin(months)].groupby("year")[col]
    out = g.agg(how)
    return out[g.count() == len(months)]      # only years with every month present

seasons = {
    "spring_rain_mm":  ([3, 4, 5], "rain", "sum"),
    "summer_rain_mm":  ([6, 7, 8], "rain", "sum"),
    "harvest_rain_mm": ([8, 9],    "rain", "sum"),
    "spring_temp":     ([3, 4, 5], "meant", "mean"),
    "summer_temp":     ([6, 7, 8], "meant", "mean"),
    "summer_sun_hrs":  ([6, 7, 8], "sun", "sum"),
}
feat = pd.DataFrame({name: season(*args) for name, args in seasons.items()}).reset_index()
df = df.merge(feat, on="year", how="left")

# ---- drop years without usable weather ----
before = len(df)
df = df[df["year"] >= 1963].dropna(subset=list(seasons)).copy()
print(f"Dropped {before - len(df)} rows (1961-62 and any incomplete seasons). {len(df)} remain.\n")

# ---- extreme weather flags: bottom/top 10% of years (agree thresholds as a group) ----
years = df.drop_duplicates("year")
q = lambda col, p: years[col].quantile(p)
df["dry_summer"]   = df["summer_rain_mm"]  <= q("summer_rain_mm", 0.10)
df["wet_summer"]   = df["summer_rain_mm"]  >= q("summer_rain_mm", 0.90)
df["wet_harvest"]  = df["harvest_rain_mm"] >= q("harvest_rain_mm", 0.90)
df["hot_summer"]   = df["summer_temp"]     >= q("summer_temp", 0.90)
df["cold_spring"]  = df["spring_temp"]     <= q("spring_temp", 0.10)
df["dull_summer"]  = df["summer_sun_hrs"]  <= q("summer_sun_hrs", 0.10)
flags = ["dry_summer", "wet_summer", "wet_harvest", "hot_summer", "cold_spring", "dull_summer"]

# ---- yield flag: 10%+ below the crop's trend ----
df["low_yield"] = df["yield_vs_trend_pct"] <= -10

# ---- how often does an extreme coincide with a low-yield year? ----
print("Share of years with low yield (10%+ below trend):")
print((df.groupby("crop")["low_yield"].mean() * 100).round(0).astype(int).astype(str).add("%").to_string())

rows = []
for crop, g in df.groupby("crop"):
    for f in flags:
        hit = g[g[f]]
        rows.append({"crop": crop, "extreme": f, "years_flagged": len(hit),
                     "low_yield_when_flagged_%": round(hit["low_yield"].mean() * 100) if len(hit) else None,
                     "mean_yield_vs_trend_%": round(hit["yield_vs_trend_pct"].mean(), 1) if len(hit) else None})
print("\nExtreme weather vs yield:")
print(pd.DataFrame(rows).to_string(index=False))

df = df.sort_values(["crop", "year"])
df.to_csv("crop_weather_final.csv", index=False)
print(f"\nSaved {len(df)} python finalize_dataset.pypython finalize_dataset.pyrows, {len(df.columns)} columns to crop_weather_final.csv")