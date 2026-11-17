"""Sprint 2 tests - run with:  python -m pytest test_sprint2.py -v

Covers the test tasks in the Display Data epic:
  APPG5-30 raw data display matches the source files
  APPG5-36 tables, filters and search work
  APPG5-42 / APPG5-48 charts get the right data
  APPG5-54 comparison lines up weather and crop data for the same year
"""
import pandas as pd
import pytest

import data_loader as dl


@pytest.fixture(scope="module")
def weather():
    return dl.load_weather()


@pytest.fixture(scope="module")
def crops():
    return dl.load_crops()


# ---- APPG5-30: raw data matches the source files ----
def test_raw_weather_has_every_row_from_the_three_files():
    raw = dl.load_raw_weather()
    assert set(raw["station"]) == {"Roches Point", "Cork Airport", "Moore Park"}
    # same number of monthly rows as the merged file produced in Sprint 1
    assert len(raw) == len(pd.read_csv(dl.path("cork_weather_monthly.csv")))


def test_raw_weather_is_not_cleaned():
    raw = dl.load_raw_weather()
    # blanks in the original are kept as text, not converted to numbers
    assert pd.api.types.is_string_dtype(raw["rain"])
    assert (raw["rain"].str.strip() == "").any()


@pytest.mark.parametrize("source,file", [("CSO", "crops/aqa04.csv"), ("FAO", "fao/fao_yield.csv")])
def test_raw_crops_match_source(source, file):
    raw = dl.load_raw_crops(source)
    original = pd.read_csv(dl.path(*file.split("/")), encoding="utf-8-sig", dtype=str)
    assert raw.equals(original)


# ---- APPG5-36: filters and search ----
def test_year_filter(crops):
    out = dl.filter_table(crops, year_range=[2010, 2015])
    assert out["year"].between(2010, 2015).all()
    assert len(out) > 0


def test_category_filter(crops):
    out = dl.filter_table(crops, column="crop", values=["Barley"])
    assert set(out["crop"]) == {"Barley"}


def test_search_is_case_insensitive(weather):
    out = dl.filter_table(weather, search="moore park")
    assert len(out) > 0
    assert set(out["station_name"]) == {"Moore Park"}


def test_no_filters_returns_everything(crops):
    assert len(dl.filter_table(crops)) == len(crops)


def test_search_with_no_match_returns_empty(crops):
    assert dl.filter_table(crops, search="zzz-not-a-crop").empty


# ---- APPG5-42: weather charts ----
def test_yearly_rain_is_a_total_of_12_months(weather):
    d = dl.weather_series(weather, "rain", ["Cork Airport"], [2018, 2018])
    expected = weather[(weather.station_name == "Cork Airport") & (weather.year == 2018)]["rain"].sum()
    assert d["rain"].iloc[0] == pytest.approx(expected)


def test_yearly_temperature_is_an_average(weather):
    d = dl.weather_series(weather, "meant", ["Cork Airport"], [2018, 2018])
    expected = weather[(weather.station_name == "Cork Airport") & (weather.year == 2018)]["meant"].mean()
    assert d["meant"].iloc[0] == pytest.approx(expected)


def test_incomplete_years_are_left_out(weather):
    # the latest year is still in progress so it can't have 12 months
    latest = int(weather.year.max())
    d = dl.weather_series(weather, "rain", ["Cork Airport"], [latest, latest])
    assert d.empty


def test_monthly_view_respects_year_range(weather):
    d = dl.weather_series(weather, "meant", ["Moore Park"], [2010, 2012], "Monthly")
    assert d["x"].dt.year.between(2010, 2012).all()
    assert len(d) <= 36


# ---- APPG5-48: crop charts ----
def test_crop_series_only_returns_selected_crops(crops):
    d = dl.crop_series(crops, "yield_t_per_ha", ["Wheat", "Oats"], [2000, 2020])
    assert set(d["crop"]) == {"Wheat", "Oats"}
    assert d["year"].between(2000, 2020).all()


def test_yields_are_realistic(crops):
    d = dl.crop_series(crops, "yield_t_per_ha", ["Wheat", "Barley"], [1963, 2025])
    assert d["yield_t_per_ha"].between(1, 15).all()


# ---- APPG5-54: comparison lines up the same years ----
def test_compare_uses_same_year_weather(crops):
    d = dl.compare_series(crops, "Barley", "summer_rain_mm", [1963, 2025])
    row = crops[(crops.crop == "Barley") & (crops.year == 2018)].iloc[0]
    match = d[d.year == 2018].iloc[0]
    assert match["summer_rain_mm"] == row["summer_rain_mm"]
    assert match["yield_t_per_ha"] == row["yield_t_per_ha"]


def test_2018_drought_shows_as_a_dry_summer(crops):
    d = dl.compare_series(crops, "Barley", "summer_rain_mm", [1963, 2025])
    assert d.loc[d.year == 2018, "summer_rain_mm"].iloc[0] < d["summer_rain_mm"].median()


# ---- readable processed tables ----
def test_display_uses_readable_headings(crops):
    out = dl.for_display(crops)
    assert "Yield (t/ha)" in out.columns
    assert "yield_t_per_ha" not in out.columns


def test_display_shows_flags_as_ticks(crops):
    out = dl.for_display(crops)
    assert set(out["Dry summer"].unique()) <= {"✓", ""}
    assert (out["Dry summer"] == "✓").sum() == crops["dry_summer"].sum()


def test_every_processed_column_has_a_label(crops, weather):
    for df in (crops, weather.drop(columns="date")):
        missing = [c for c in df.columns if c not in dl.COLUMN_LABELS]
        assert missing == []
