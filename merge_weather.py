import os, glob, re
import pandas as pd

IN_DIR = "weather"
OUT_FILE = "cork_weather_monthly.csv"

frames = []
for path in sorted(glob.glob(os.path.join(IN_DIR, "*.csv"))):
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()

    # find the real header row (the line with year, month, meant...)
    header_idx = next(
        i for i, l in enumerate(lines)
        if l.strip().lower().startswith("year") and "month" in l.lower() and "meant" in l.lower()
    )

    # station name from the description lines at the top
    name = next(
        (l.split(":", 1)[1].strip(" ,\t") for l in lines if l.lower().startswith("station name")),
        "UNKNOWN",
    )
    m = re.search(r"(\d+)", os.path.basename(path))
    number = m.group(1) if m else "UNKNOWN"

    df = pd.read_csv(path, skiprows=header_idx, sep=None, engine="python", skipinitialspace=True)
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.loc[:, ~df.columns.str.startswith("unnamed")]
    df = df.apply(pd.to_numeric, errors="coerce")   # blanks become NaN
    df = df.dropna(subset=["year", "month"])
    df.insert(0, "station_name", name)
    df.insert(0, "station_no", number)
    frames.append(df)
    print(f"{name} ({number}): {len(df)} rows, {int(df.year.min())}-{int(df.year.max())}")

all_data = pd.concat(frames, ignore_index=True)
all_data = all_data.sort_values(["station_no", "year", "month"])
all_data.to_csv(OUT_FILE, index=False)
print(f"\nSaved {len(all_data)} rows to {OUT_FILE}")
print(all_data.isna().sum())