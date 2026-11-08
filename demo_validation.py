import pandas as pd

df = pd.read_csv("crop_weather_final.csv")

required = ["crop", "year", "source", "yield_t_per_ha", "yield_vs_trend_pct",
            "grow_mean_temp", "grow_rain_mm", "grow_sun_hrs",
            "spring_rain_mm", "summer_rain_mm", "summer_temp", "summer_sun_hrs"]
ranges = {"yield_t_per_ha": (0, 60), "grow_mean_temp": (5, 20),
          "grow_rain_mm": (0, 1500), "grow_sun_hrs": (0, 2000),
          "summer_rain_mm": (0, 1000), "summer_temp": (5, 25)}

def validate(row):
    problems = []
    for col in required:
        if pd.isna(row[col]):
            problems.append(f"missing required field: {col}")
    for col, (lo, hi) in ranges.items():
        v = row[col]
        if pd.notna(v) and not (lo <= v <= hi):
            problems.append(f"{col} = {v} is outside the valid range {lo} to {hi}")
    return problems

def show(title, row):
    print(f"\n=== {title} ===")
    print(row[["crop", "year", "source", "yield_t_per_ha",
               "summer_rain_mm", "summer_temp"]].to_string())
    problems = validate(row)
    if problems:
        print("RESULT: INVALID")
        for p in problems:
            print("  -", p)
    else:
        print("RESULT: VALID")

valid = df[(df["crop"] == "wheat") & (df["year"] == 2020)].iloc[0]
show("Valid record", valid)

invalid = valid.copy()
invalid["yield_t_per_ha"] = None      # missing required field
invalid["summer_rain_mm"] = -50       # impossible rainfall
show("Invalid record (test copy, real data not changed)", invalid)