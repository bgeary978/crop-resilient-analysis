import pandas as pd

df = pd.read_csv("fao/fao_yield.csv", encoding="utf-8-sig")
df.columns = [c.strip() for c in df.columns]

print("Columns:")
print(df.columns.tolist())

print("\nFirst 10 rows:")
print(df.head(10).to_string())

print(f"\nTotal rows: {len(df)}")

# these lines only run if the matching column names exist
if "Item" in df.columns:
    print(f"\nNumber of crops: {df['Item'].nunique()}")
    print(sorted(df["Item"].unique()))
if "Year" in df.columns:
    print(f"\nYears: {df['Year'].min()}-{df['Year'].max()}")
if "Element" in df.columns:
    print("\nElements:", df["Element"].unique())
if "Unit" in df.columns:
    print("Units:", df["Unit"].unique())