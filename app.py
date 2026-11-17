"""Sprint 2 - Cork crop & weather dashboard (Display Data epic, APPG5-24).

Run:   pip install -r requirements.txt
       python app.py
Open:  http://127.0.0.1:8050

Tabs map to the Sprint 2 stories:
  Data      -> APPG5-25 Display Raw Data, APPG5-31 Display Processed Data
  Weather   -> APPG5-37 Visualise Weather Data
  Crops     -> APPG5-43 Visualise Crop Yield Data
  Compare   -> APPG5-49 Compare Weather and Crop Yield
"""
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, Input, Output, dash_table, dcc, html
from plotly.subplots import make_subplots

import data_loader as dl

# ---------------------------------------------------------------- data
RAW_WEATHER = dl.load_raw_weather()
WEATHER = dl.load_weather()
CROPS = dl.load_crops()

STATIONS = sorted(WEATHER["station_name"].unique())
CROP_NAMES = sorted(CROPS["crop"].unique())
W_MIN, W_MAX = int(WEATHER["year"].min()), int(WEATHER["year"].max())
C_MIN, C_MAX = int(CROPS["year"].min()), int(CROPS["year"].max())

GREEN, BLUE, ORANGE = "#2e7d32", "#1565c0", "#ef6c00"
COLOURS = ["#2e7d32", "#1565c0", "#ef6c00", "#6a1b9a", "#c62828", "#00838f"]

DATASETS = {
    "raw_weather": "Raw – Met Éireann weather (3 station files)",
    "raw_cso": "Raw – CSO crop statistics (AQA04)",
    "raw_fao": "Raw – FAOSTAT crop yields",
    "weather": "Processed – monthly weather, all stations",
    "crops": "Processed – crop yields with seasonal weather",
}


# ------------------------------------------------------ reusable pieces
def year_slider(id_, lo, hi, start=None):
    """One year-range control, reused on every tab."""
    marks = {y: str(y) for y in range(lo, hi + 1) if y % 10 == 0 or y in (lo, hi)}
    return dcc.RangeSlider(id=id_, min=lo, max=hi, step=1, value=[start or lo, hi],
                           marks=marks, tooltip={"placement": "bottom"}, allowCross=False)


def control(label, component):
    return html.Div([html.Label(label, className="label"), component], className="control")


def styled_fig(fig, y_title):
    fig.update_layout(template="plotly_white", margin=dict(l=40, r=20, t=30, b=40),
                      legend=dict(orientation="h", y=1.08, x=0), hovermode="x unified",
                      yaxis_title=y_title, xaxis_title=None, height=450)
    return fig


def empty_fig(message):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=16, color="#666"))
    fig.update_layout(template="plotly_white", xaxis_visible=False, yaxis_visible=False, height=450)
    return fig


# --------------------------------------------------------------- tabs
data_tab = html.Div([
    html.Div([
        control("Dataset", dcc.Dropdown(id="data-set", options=DATASETS, value="crops", clearable=False)),
        control("Search", dcc.Input(id="data-search", type="text", debounce=True,
                                    placeholder="e.g. barley, Cork Airport, 2018")),
    ], className="row"),
    html.Div([
        control("Station / crop", dcc.Dropdown(id="data-category", multi=True,
                                               placeholder="All")),
        control("Years", year_slider("data-years", C_MIN, C_MAX)),
    ], className="row"),
    html.P(id="data-count", className="note"),
    dash_table.DataTable(
        id="data-table", page_size=15, sort_action="native", filter_action="native",
        export_format="csv", export_headers="display",
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": GREEN, "color": "white", "fontWeight": "bold"},
        style_cell={"fontFamily": "inherit", "fontSize": 13, "padding": "6px",
                    "minWidth": 70, "maxWidth": 220, "whiteSpace": "normal"},
        style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#f5f8f5"}],
    ),
])

weather_tab = html.Div([
    html.Div([
        control("Measure", dcc.Dropdown(id="w-metric", options=dl.WEATHER_METRICS,
                                        value="rain", clearable=False)),
        control("Stations", dcc.Dropdown(id="w-stations", options=STATIONS,
                                         value=STATIONS, multi=True)),
        control("View", dcc.RadioItems(id="w-period", options=["Yearly", "Monthly"],
                                       value="Yearly", inline=True)),
    ], className="row"),
    control("Years", year_slider("w-years", W_MIN, W_MAX, start=1990)),
    dcc.Graph(id="w-chart"),
    html.P(id="w-note", className="note"),
])

crops_tab = html.Div([
    html.Div([
        control("Crops", dcc.Dropdown(id="c-crops", options=CROP_NAMES,
                                      value=["Barley", "Wheat", "Oats"], multi=True)),
        control("Measure", dcc.Dropdown(id="c-metric", options=dl.CROP_METRICS,
                                        value="yield_t_per_ha", clearable=False)),
    ], className="row"),
    control("Years", year_slider("c-years", C_MIN, C_MAX)),
    dcc.Graph(id="c-chart"),
    html.P("Area and production figures come from the CSO and are only available from 2008. "
           "'Yield vs normal' compares each year with the crop's long-term trend.",
           className="note"),
])

compare_tab = html.Div([
    html.Div([
        control("Crop", dcc.Dropdown(id="x-crop", options=CROP_NAMES, value="Barley",
                                     clearable=False)),
        control("Weather measure", dcc.Dropdown(id="x-weather", options=dl.COMPARE_WEATHER,
                                                value="summer_rain_mm", clearable=False)),
    ], className="row"),
    control("Years", year_slider("x-years", C_MIN, C_MAX)),
    dcc.Graph(id="x-chart"),
    html.P(id="x-summary", className="summary"),
    html.P("Note: weather is from three Cork stations, but crop yields are national figures "
           "for all of Ireland (CSO and FAO). Cork weather is used as a guide to Irish growing "
           "conditions, so links between the two will look weaker than they would for a single farm.",
           className="note"),
])

app = Dash(__name__, title="Cork Crop & Weather")
app.layout = html.Div([
    html.Header([
        html.H1("Cork Crop & Weather"),
        html.P("Met Éireann weather for Cork alongside CSO and FAO crop yields for Ireland"),
    ]),
    dcc.Tabs(className="tabs", children=[
        dcc.Tab(label="Data", children=data_tab),
        dcc.Tab(label="Weather", children=weather_tab),
        dcc.Tab(label="Crops", children=crops_tab),
        dcc.Tab(label="Compare", children=compare_tab),
    ]),
], className="page")


# ----------------------------------------------------------- callbacks
def get_dataset(name):
    if name == "raw_weather":
        return RAW_WEATHER, "station"
    if name == "raw_cso":
        return dl.load_raw_crops("CSO").rename(columns={"Year": "year"}), "Type of Crop"
    if name == "raw_fao":
        return dl.load_raw_crops("FAO").rename(columns={"Year": "year"}), "Item"
    if name == "weather":
        return WEATHER.drop(columns="date"), "station_name"
    return CROPS, "crop"


@app.callback(Output("data-category", "options"), Output("data-category", "value"),
              Output("data-years", "min"), Output("data-years", "max"),
              Output("data-years", "value"), Output("data-years", "marks"),
              Input("data-set", "value"))
def update_data_controls(name):
    """When the dataset changes, reset the category list and year range to fit it."""
    df, col = get_dataset(name)
    years = df["year"].astype(float)
    lo, hi = int(years.min()), int(years.max())
    marks = {y: str(y) for y in range(lo, hi + 1) if y % 10 == 0 or y in (lo, hi)}
    return sorted(df[col].dropna().unique()), [], lo, hi, [lo, hi], marks


@app.callback(Output("data-table", "data"), Output("data-table", "columns"),
              Output("data-count", "children"),
              Input("data-set", "value"), Input("data-category", "value"),
              Input("data-years", "value"), Input("data-search", "value"))
def update_table(name, categories, years, search):
    df, col = get_dataset(name)
    out = dl.filter_table(df, years, col, categories, search)
    if name in ("weather", "crops"):
        out = dl.for_display(out)
    columns = [{"name": c, "id": c} for c in out.columns]
    return out.to_dict("records"), columns, f"Showing {len(out):,} of {len(df):,} rows"


@app.callback(Output("w-chart", "figure"), Output("w-note", "children"),
              Input("w-metric", "value"), Input("w-stations", "value"),
              Input("w-years", "value"), Input("w-period", "value"))
def update_weather(metric, stations, years, period):
    if not stations:
        return empty_fig("Pick at least one station"), ""
    d = dl.weather_series(WEATHER, metric, stations, years, period)
    if d.empty:
        return empty_fig("No data for this selection"), ""
    label = dl.WEATHER_METRICS[metric]
    if period == "Yearly" and metric in ("rain", "sun"):
        label = label.replace("(", "per year (")
    fig = px.line(d, x="x", y=metric, color="station_name", markers=period == "Yearly",
                  color_discrete_sequence=COLOURS, labels={"station_name": "Station", metric: label})
    note = ("Yearly view only includes years where all 12 months were recorded. "
            "Moore Park and Roches Point records start in 2004.")
    return styled_fig(fig, label), note


@app.callback(Output("c-chart", "figure"),
              Input("c-crops", "value"), Input("c-metric", "value"), Input("c-years", "value"))
def update_crops(crops, metric, years):
    if not crops:
        return empty_fig("Pick at least one crop")
    d = dl.crop_series(CROPS, metric, crops, years)
    if d.empty:
        return empty_fig("No data for this crop and measure – try 2008 onwards for area/production")
    label = dl.CROP_METRICS[metric]
    fig = px.line(d, x="year", y=metric, color="crop", markers=True,
                  color_discrete_sequence=COLOURS, labels={"crop": "Crop", metric: label})
    if metric == "yield_vs_trend_pct":
        fig.add_hline(y=0, line_dash="dot", line_color="#999")
    return styled_fig(fig, label)


@app.callback(Output("x-chart", "figure"), Output("x-summary", "children"),
              Input("x-crop", "value"), Input("x-weather", "value"), Input("x-years", "value"))
def update_compare(crop, weather, years):
    d = dl.compare_series(CROPS, crop, weather, years)
    if d.empty:
        return empty_fig("No data for this selection"), ""
    w_label = dl.COMPARE_WEATHER[weather]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=d["year"], y=d[weather], name=w_label, marker_color="#90caf9", opacity=0.8)
    fig.add_scatter(x=d["year"], y=d["yield_t_per_ha"], name=f"{crop} yield (t/ha)",
                    mode="lines+markers", line=dict(color=GREEN, width=3), secondary_y=True)
    styled_fig(fig, w_label)
    fig.update_yaxes(title_text="Yield (t/ha)", secondary_y=True, showgrid=False)

    # Plain-English summary: wettest/driest (or hottest/coldest) years vs normal yield
    high = d.nlargest(3, weather)
    low = d.nsmallest(3, weather)
    word_hi, word_lo = ("highest", "lowest")
    summary = (f"In the 3 years with the {word_hi} {w_label.split(',')[0].split('(')[0].strip().lower()}, "
               f"{crop.lower()} yield averaged {high['yield_vs_trend_pct'].mean():+.0f}% vs normal. "
               f"In the 3 {word_lo} years it averaged {low['yield_vs_trend_pct'].mean():+.0f}%. "
               f"Correlation across {len(d)} years: {d[weather].corr(d['yield_vs_trend_pct']):+.2f} "
               f"(closer to ±1 means a stronger link).")
    return fig, summary


if __name__ == "__main__":
    # debug=False hides Dash's developer panel; set it to True while coding
    app.run(debug=False)
