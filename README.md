# NASA Climate Dashboard

This repository contains a small Dash web application that visualises NASA GISTEMP annual global surface temperature anomalies using Plotly Express. The dashboard highlights key warming statistics, provides interactive visualisations, and surfaces the warmest years on record.

## Features

- 📈 Interactive line chart comparing raw annual anomalies with a five-year rolling average.
- 📊 Bar chart summarising the average anomaly per decade.
- 🧮 Summary cards for the latest anomaly, last-decade average, and the long-term warming trend.
- 🗓️ Data table listing the ten warmest years in the record.

## Getting started

1. Create and activate a Python virtual environment (optional but recommended).
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Launch the Dash development server:

   ```bash
   python app/app.py
   ```

4. Open your browser at http://127.0.0.1:8050/ to interact with the dashboard.

## Dataset

The dataset in [`data/nasa_global_temperature_anomalies.csv`](data/nasa_global_temperature_anomalies.csv) reproduces annual global mean temperature anomalies from the [NASA Goddard Institute for Space Studies (GISTEMP v4)](https://data.giss.nasa.gov/gistemp/). Values are expressed in °C relative to the 1951–1980 baseline and cover 1980–2023.

## Project structure

```
.
├── app/
│   └── app.py            # Dash application
├── assets/
│   └── style.css         # Custom styling for the dashboard
├── data/
│   └── nasa_global_temperature_anomalies.csv
├── requirements.txt      # Python dependencies
└── README.md
```

## Development notes

- The Dash app exposes a WSGI-compatible `server` object for deployment platforms.
- When adding new datasets, update `DATA_PATH` in `app/app.py` and extend the layout as needed.
