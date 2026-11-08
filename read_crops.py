import pandas as pd

df = pd.read_csv("crops/aqa04.csv", sep=None, engine="python", encoding="utf-8-sig")
df.columns = [c.strip().replace("\ufeff", "") for c in df.columns]

# the statistic column has a different name depending on the CSV layout
stat_col = "STATISTIC" if "STATISTIC" in df.columns else "Statistic Label"

# clean values and names
df["VALUE"] = pd.to_numeric(df["VALUE"], errors="coerce")   # blanks become NaN
df["Type of Crop"] = df["Type of Crop"].str.strip().str.lower()

# readable names for the three statistics (works with codes or with text labels)
def to_measure(s):
    low = str(s).strip().lower()
    if low in ("aqa04c1", "aqa04c2", "aqa04c3"):
        return {"aqa04c1": "area_000ha", "aqa04c2": "yield_t_per_ha", "aqa04c3": "production_000t"}[low]
    if "area" in low:
        return "area_000ha"
    if "yield" in low:
        return "yield_t_per_ha"
    if "production" in low:
        return "production_000t"
    return None

df["measure"] = df[stat_col].map(to_measure)
print("Statistics not recognised:", df[df["measure"].isna()][stat_col].unique())

# long format -> one row per crop per year
index_cols = ["Year", "Type of Crop"]
if "C02039V02469" in df.columns:
    index_cols.insert(1, "C02039V02469")
wide = df.pivot_table(index=index_cols, columns="measure", values="VALUE").reset_index()
wide.columns.name = None
wide = wide.rename(columns={"Year": "year", "C02039V02469": "crop_code", "Type of Crop": "crop"})
wide = wide.sort_values(["crop_code" if "crop_code" in wide.columns else "crop", "year"])

wide.to_csv("crops_clean.csv", index=False)

print("Units in the file:")
print(df.groupby(stat_col)["UNIT"].unique())
print(f"\nSaved {len(wide)} rows to crops_clean.csv")
print(f"Years: {int(wide.year.min())}-{int(wide.year.max())}")
print(f"Crops: {wide.crop.nunique()}")
print("\nMissing values:")
print(wide.isna().sum())