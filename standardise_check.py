import pandas as pd

raw = pd.read_csv("fao/fao_yield.csv", encoding="utf-8-sig")
raw.columns = [c.strip() for c in raw.columns]
cso = pd.read_csv("crops_clean.csv")
final = pd.read_csv("crop_weather_final.csv")

print("CROP NAMES")
print("  FAO raw:   ", sorted(raw["Item"].unique()))
print("  CSO clean: ", sorted(cso["crop"].unique()))
print("  Final:     ", sorted(final["crop"].unique()))

print("\nUNITS")
print("  FAO raw unit:", raw["Unit"].unique().tolist(), "-> converted to t/ha")
w = raw[(raw["Item"] == "Wheat") & (raw["Year"] == 2020)]["Value"].iloc[0]
f = final[(final["crop"] == "wheat") & (final["year"] == 2020)]["yield_t_per_ha"].iloc[0]
print(f"  Example, wheat 2020: raw {w} kg/ha -> final {f:.2f} t/ha")

print("\nYEARS")
print("  FAO raw:   ", raw["Year"].dtype, raw["Year"].min(), "-", raw["Year"].max())
print("  CSO clean: ", cso["year"].dtype, cso["year"].min(), "-", cso["year"].max())
print("  Final:     ", final["year"].dtype, final["year"].min(), "-", final["year"].max())