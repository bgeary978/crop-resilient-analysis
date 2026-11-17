"""Sprint 2 - loading and filtering data for the dashboard.

Keeps all the pandas work in one place so app.py only deals with layout,
and so the functions can be tested on their own (see test_sprint2.py).
"""
import glob
import os

import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))

# Friendly labels so farmers never see raw column names
WEATHER_METRICS = {
    "meant": "Mean temperature (°C)",
    "maxtp": "Highest temperature (°C)",
    "mintp": "Lowest temperature (°C)",
    "rain": "Rainfall (mm)",
    "sun": "Sunshine (hours)",
}

CROP_METRICS = {
    "yield_t_per_ha": "Yield (tonnes per hectare)",
    "yield_vs_trend_pct": "Yield vs normal (%)",
    "area_000ha": "Area grown ('000 hectares)",
    "production_000t": "Production ('000 tonnes)",
}

COMPARE_WEATHER = {
    "summer_rain_mm": "Summer rainfall, Jun-Aug (mm)",
    "spring_rain_mm": "Spring rainfall, Mar-May (mm)",
    "harvest_rain_mm": "Harvest rainfall, Aug-Sep (mm)",
    "grow_rain_mm": "Growing season rainfall, Apr-Sep (mm)",
    "summer_temp": "Summer mean temperature (°C)",
    "spring_temp": "Spring mean temperature (°C)",
    "grow_mean_temp": "Growing season mean temperature (°C)",
    "summer_sun_hrs": "Summer sunshine (hours)",
}


# Readable headings for the processed tables (raw tables keep their original names)
COLUMN_LABELS = {
    "crop": "Crop", "year": "Year", "source": "Source",
    "yield_t_per_ha": "Yield (t/ha)", "yield_vs_trend_pct": "Yield vs normal (%)",
    "area_000ha": "Area ('000 ha)", "production_000t": "Production ('000 t)",
    "grow_mean_temp": "Growing season temp (°C)", "grow_rain_mm": "Growing season rain (mm)",
    "grow_sun_hrs": "Growing season sunshine (hrs)", "annual_rain_mm": "Annual rain (mm)",
    "wet_months": "Very wet months", "hot_months": "Hot months", "frost_months": "Frost months",
    "year_max_temp": "Year's highest temp (°C)", "year_min_temp": "Year's lowest temp (°C)",
    "stations_used": "Stations used",
    "spring_rain_mm": "Spring rain (mm)", "summer_rain_mm": "Summer rain (mm)",
    "harvest_rain_mm": "Harvest rain (mm)", "spring_temp": "Spring temp (°C)",
    "summer_temp": "Summer temp (°C)", "summer_sun_hrs": "Summer sunshine (hrs)",
    "dry_summer": "Dry summer", "wet_summer": "Wet summer", "wet_harvest": "Wet harvest",
    "hot_summer": "Hot summer", "cold_spring": "Cold spring", "dull_summer": "Dull summer",
    "low_yield": "Low yield",
    "station_no": "Station no.", "station_name": "Station", "month": "Month",
    "meant": "Mean temp (°C)", "maxtp": "Max temp (°C)", "mintp": "Min temp (°C)",
    "mnmax": "Mean daily max (°C)", "mnmin": "Mean daily min (°C)", "rain": "Rainfall (mm)",
    "gmin": "Grass min temp (°C)", "wdsp": "Mean wind speed (knots)",
    "maxgt": "Highest gust (knots)", "sun": "Sunshine (hrs)",
}


def for_display(df):
    """Round numbers, show True/False flags as a tick, and use readable headings."""
    out = df.copy()
    for col in out.columns:
        if out[col].dtype == bool:
            out[col] = out[col].map({True: "✓", False: ""})
    out = out.round(1)
    return out.rename(columns=COLUMN_LABELS)


def path(*parts):
    return os.path.join(BASE, *parts)


# ---------------------------------------------------------------- raw data
def load_raw_weather():
    """Read the three Met Éireann files as downloaded (no cleaning).

    Only the description lines at the top are skipped so the table has
    proper column headers. Blank values stay blank.
    """
    frames = []
    for file in sorted(glob.glob(path("weather", "*.csv"))):
        with open(file, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
        header = next(i for i, l in enumerate(lines)
                      if l.strip().lower().startswith("year") and "month" in l.lower())
        station = next((l.split(":", 1)[1].strip(" ,\t") for l in lines
                        if l.lower().startswith("station name")), "UNKNOWN")
        df = pd.read_csv(file, skiprows=header, dtype=str, keep_default_na=False)
        df.columns = [c.strip() for c in df.columns]
        df.insert(0, "station", station.title())
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def load_raw_crops(source):
    """Return the crop file exactly as downloaded: 'CSO' or 'FAO'."""
    if source == "CSO":
        return pd.read_csv(path("crops", "aqa04.csv"), encoding="utf-8-sig", dtype=str)
    return pd.read_csv(path("fao", "fao_yield.csv"), encoding="utf-8-sig", dtype=str)


# ---------------------------------------------------------- processed data
def load_weather():
    """Cleaned monthly weather (output of merge_weather.py)."""
    df = pd.read_csv(path("cork_weather_monthly.csv"))
    df["station_name"] = df["station_name"].str.title()
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    return df


def load_crops():
    """Cleaned crop + weather dataset (output of finalize_dataset.py)."""
    df = pd.read_csv(path("crop_weather_final.csv"))
    df["crop"] = df["crop"].str.title()
    return df


# ----------------------------------------------------------------- filters
def filter_table(df, year_range=None, column=None, values=None, search=None):
    """Shared filter used by every table: year range, a category, free text."""
    out = df
    if year_range and "year" in out.columns:
        years = pd.to_numeric(out["year"], errors="coerce")
        out = out[years.between(year_range[0], year_range[1])]
    if column and values:
        out = out[out[column].isin(values)]
    if search:
        text = out.apply(lambda row: " ".join(map(str, row)), axis=1)
        out = out[text.str.contains(search, case=False, regex=False)]
    return out


def weather_series(df, metric, stations, year_range, period="Yearly"):
    """Weather over time, monthly or one value per year per station.

    Rain and sunshine are totalled for the year, temperatures averaged.
    Years with missing months are dropped so totals aren't misleadingly low.
    """
    d = df[df["station_name"].isin(stations) & df["year"].between(*year_range)]
    if period == "Monthly":
        return d[["date", "station_name", metric]].dropna().rename(columns={"date": "x"})

    how = "sum" if metric in ("rain", "sun") else "mean"
    g = d.groupby(["station_name", "year"])[metric]
    yearly = g.agg(how)[g.count() == 12].reset_index()
    return yearly.rename(columns={"year": "x"})


def crop_series(df, metric, crops, year_range):
    d = df[df["crop"].isin(crops) & df["year"].between(*year_range)]
    return d[["crop", "year", metric]].dropna()


def compare_series(df, crop, weather_metric, year_range):
    d = df[(df["crop"] == crop) & df["year"].between(*year_range)]
    return d[["year", "yield_t_per_ha", "yield_vs_trend_pct", weather_metric]].dropna()
