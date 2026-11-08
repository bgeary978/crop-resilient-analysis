import pandas as pd

FILE = "crop_weather_final.csv"      # output of finalize_dataset.py
df = pd.read_csv(FILE)
failures = 0

def check(name, bad):
    global failures
    if len(bad) == 0:
        print(f"PASS  {name}")
    else:
        failures += 1
        print(f"FAIL  {name}  ({len(bad)} records)")
        print(bad.head(5).to_string())

print(f"Validating {FILE}: {len(df)} rows\n")

# ---- standardisation ----
print("-- Standardisation --")
check("crop names lowercase and trimmed",
      df[df["crop"] != df["crop"].str.strip().str.lower()])
check("year is a whole number between 1961 and 2025",
      df[(df["year"] % 1 != 0) | ~df["year"].between(1961, 2025)])
check("source is FAO or CSO", df[~df["source"].isin(["FAO", "CSO"])])
print("Crops present:", sorted(df["crop"].unique()), "\n")

# ---- required fields ----
print("-- Required fields --")
required = ["crop", "year", "source", "yield_t_per_ha", "yield_vs_trend_pct",
            "grow_mean_temp", "grow_rain_mm", "grow_sun_hrs",
            "spring_rain_mm", "summer_rain_mm", "summer_temp", "summer_sun_hrs"]
for col in required:
    if col not in df.columns:
        failures += 1
        print(f"FAIL  column '{col}' does not exist")
    else:
        check(f"'{col}' filled in on every record", df[df[col].isna()])

# ---- duplicates ----
print("\n-- Duplicates --")
check("one record per crop per year", df[df.duplicated(["crop", "year"], keep=False)])

# ---- ranges (generous limits; adjust as a group) ----
print("\n-- Ranges --")
ranges = {"yield_t_per_ha": (0, 60),      # potatoes are about 40 t/ha
          "grow_mean_temp": (5, 20),
          "grow_rain_mm": (0, 1500),
          "grow_sun_hrs": (0, 2000),
          "summer_rain_mm": (0, 1000),
          "summer_temp": (5, 25),
          "year_min_temp": (-25, 15),
          "year_max_temp": (10, 40)}
for col, (lo, hi) in ranges.items():
    if col in df.columns:
        check(f"{col} between {lo} and {hi}", df[(df[col] < lo) | (df[col] > hi)])

print(f"\n{'ALL CHECKS PASSED' if failures == 0 else str(failures) + ' CHECK(S) FAILED'}")