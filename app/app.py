from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from dash import Dash, dash_table, dcc, html, Input, Output
import plotly.express as px

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "nasa_global_temperature_anomalies.csv"

def load_dataset() -> pd.DataFrame:
    """Load and preprocess the temperature dataset."""
    df = pd.read_csv(DATA_PATH)
    df = df.sort_values("Year")
    df["RollingMean"] = df["GlobalMeanAnomalyC"].rolling(window=5, min_periods=1).mean()
    df["Decade"] = (df["Year"] // 10) * 10
    return df

def compute_summary_stats(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate summary statistics used in the layout."""
    latest_year = int(df["Year"].max())
    latest_anomaly = float(df.loc[df["Year"] == latest_year, "GlobalMeanAnomalyC"].iloc[0])

    last_decade_years = df[df["Year"] >= latest_year - 9]
    last_decade_avg = float(last_decade_years["GlobalMeanAnomalyC"].mean())

    earliest_decade = df["Decade"].min()
    latest_decade = df["Decade"].max()
    decadal_means = df.groupby("Decade")["GlobalMeanAnomalyC"].mean().reset_index()
    earliest_decade_avg = float(decadal_means.loc[decadal_means["Decade"] == earliest_decade, "GlobalMeanAnomalyC"].iloc[0])
    latest_decade_avg = float(decadal_means.loc[decadal_means["Decade"] == latest_decade, "GlobalMeanAnomalyC"].iloc[0])

    slope_per_year = float(np.polyfit(df["Year"], df["GlobalMeanAnomalyC"], 1)[0])
    slope_per_decade = slope_per_year * 10

    return {
        "latest_year": latest_year,
        "latest_anomaly": latest_anomaly,
        "last_decade_avg": last_decade_avg,
        "earliest_decade": int(earliest_decade),
        "earliest_decade_avg": earliest_decade_avg,
        "latest_decade": int(latest_decade),
        "latest_decade_avg": latest_decade_avg,
        "trend_per_decade": slope_per_decade,
    }

def create_app() -> Dash:
    df = load_dataset()
    summary = compute_summary_stats(df)

    app = Dash(__name__)
    app.title = "NASA Climate Trends"

    dropdown_options = [
        {"label": "Global mean temperature anomaly", "value": "GlobalMeanAnomalyC"},
        {"label": "Five-year rolling average", "value": "RollingMean"},
    ]

    app.layout = html.Div(
        className="container",
        children=[
            html.Header(
                children=[
                    html.H1("NASA Global Temperature Dashboard"),
                    html.P(
                        "Annual global surface temperature anomalies from NASA GISTEMP "
                        "(baseline 1951-1980)."
                    ),
                ]
            ),
            html.Section(
                className="stats",
                children=[
                    html.Div(
                        className="stat-card",
                        children=[
                            html.H3(f"{summary['latest_year']}", className="stat-title"),
                            html.P("Latest reported anomaly (°C)"),
                            html.Strong(f"{summary['latest_anomaly']:.2f}")
                        ],
                    ),
                    html.Div(
                        className="stat-card",
                        children=[
                            html.H3("Last 10 years", className="stat-title"),
                            html.P("Average anomaly (°C)"),
                            html.Strong(f"{summary['last_decade_avg']:.2f}")
                        ],
                    ),
                    html.Div(
                        className="stat-card",
                        children=[
                            html.H3("Trend", className="stat-title"),
                            html.P("Warming per decade (°C)"),
                            html.Strong(f"{summary['trend_per_decade']:.2f}")
                        ],
                    ),
                ],
            ),
            html.Section(
                className="controls",
                children=[
                    html.Label("Select data series"),
                    dcc.Dropdown(
                        id="series-dropdown",
                        options=dropdown_options,
                        value="GlobalMeanAnomalyC",
                        clearable=False,
                    ),
                    html.P(
                        "Use the dropdown to compare the raw annual anomalies to the smoother "
                        "five-year rolling average."
                    ),
                ],
            ),
            html.Section(
                className="charts",
                children=[
                    dcc.Graph(id="temperature-trend"),
                    dcc.Graph(id="decadal-means", figure=create_decadal_chart(df)),
                ],
            ),
            html.Section(
                className="table-section",
                children=[
                    html.H2("Warmest years on record"),
                    dash_table.DataTable(
                        id="warmest-years",
                        columns=[
                            {"name": "Year", "id": "Year"},
                            {"name": "Anomaly (°C)", "id": "GlobalMeanAnomalyC"},
                        ],
                        data=(
                            df.nlargest(10, "GlobalMeanAnomalyC")[
                                ["Year", "GlobalMeanAnomalyC"]
                            ].to_dict("records")
                        ),
                        style_header={"fontWeight": "bold"},
                        style_cell={"padding": "0.5rem", "textAlign": "center"},
                    ),
                ],
            ),
            html.Footer(
                children=[
                    html.P(
                        "Source: NASA Goddard Institute for Space Studies (GISTEMP v4). "
                        "Data reproduced for educational purposes."
                    ),
                ]
            ),
        ],
    )

    @app.callback(
        Output("temperature-trend", "figure"),
        Input("series-dropdown", "value"),
    )
    def update_trend(selected_series: str):
        title = (
            "Annual anomalies" if selected_series == "GlobalMeanAnomalyC" else "Five-year rolling mean"
        )
        fig = px.line(
            df,
            x="Year",
            y=selected_series,
            title=f"Global surface temperature anomalies — {title}",
            labels={"Year": "Year", selected_series: "Anomaly (°C)"},
        )
        fig.update_layout(margin=dict(l=40, r=20, t=60, b=40))
        fig.update_traces(mode="lines+markers")
        return fig

    return app

def create_decadal_chart(df: pd.DataFrame):
    decadal = df.groupby("Decade", as_index=False)["GlobalMeanAnomalyC"].mean()
    fig = px.bar(
        decadal,
        x="Decade",
        y="GlobalMeanAnomalyC",
        title="Average anomaly by decade",
        labels={"Decade": "Decade", "GlobalMeanAnomalyC": "Average anomaly (°C)"},
        text=decadal["GlobalMeanAnomalyC"].round(2),
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(margin=dict(l=40, r=20, t=60, b=40))
    return fig


app = create_app()
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
