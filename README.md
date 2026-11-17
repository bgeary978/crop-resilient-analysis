# Crop Resilient Analysis

Crop Resilient Analysis is a project focused on analysing Irish weather conditions and crop yields to identify relationships between weather patterns and agricultural performance.

The project uses weather data from Met Eireann and crop yield data from the Central Statistics Office (CSO). The aim is to process and visualise this information, identify patterns and explore predictive modelling to estimate crop performance.

## Project Sprints

The project is organised into three sprints:

### Sprint 1 – Data Input and Processing

Collect and import weather and crop yield datasets, clean missing or incorrect values, and validate the data for further analysis.

### Sprint 2 – Data Visualization

Display raw and processed datasets, create visualisations of weather and crop yields, and compare the data to identify potential relationships.

### Sprint 3 – Knowledge Extraction

Identify patterns within the datasets, develop a predictive model for crop performance, and present the results in a clear and understandable format.

**Team Members**
- Ben Geary
- Conor Dwyer
- Emmet Casey
- Oisin McCarthy

## Project Management

The project follows Agile and Scrum practices, using Jira for backlog and sprint management, Confluence for documentation, and GitHub for version control and collaboration.

## Sprint 2 – Data Visualisation Dashboard

An interactive [Dash](https://dash.plotly.com/) dashboard (APPG5-24 Display Data).

| Tab | Jira story | What it does |
|---|---|---|
| Data | APPG5-25 Display Raw Data, APPG5-31 Display Processed Data | Raw and processed datasets in a table with search, crop/station filter, year range, sorting and CSV export |
| Weather | APPG5-37 Visualise Weather Data | Rainfall, temperature or sunshine per station, yearly or monthly |
| Crops | APPG5-43 Visualise Crop Yield Data | Yield, yield vs normal, area or production for chosen crops |
| Compare | APPG5-49 Compare Weather and Crop Yield | A weather measure and crop yield on one chart, with a plain-English summary |

### Running it

The dashboard reads the Sprint 1 outputs, so these must be in the project folder first:
`cork_weather_monthly.csv`, `crop_weather_final.csv` and the raw `weather/`, `crops/` and `fao/` folders.

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python app.py                   # then open http://127.0.0.1:8050
python -m pytest test_sprint2.py -v
```

| File | Purpose |
|---|---|
| `app.py` | Dashboard layout, tabs and chart callbacks |
| `data_loader.py` | Loads raw and processed data; shared filter and display functions |
| `assets/style.css` | Styling (Dash loads it automatically) |
| `test_sprint2.py` | 20 tests for the Sprint 2 test tasks (APPG5-30, 36, 42, 48, 54) |
| `requirements.txt` | Exact library versions used |

Weather comes from three Cork stations, but crop yields are national figures for all of Ireland.
