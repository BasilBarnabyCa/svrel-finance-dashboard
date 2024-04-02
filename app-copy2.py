from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# Load the CSV data into a DataFrame
df = pd.read_csv("data/csvs/sales.csv")
df_targets = pd.read_csv("data/csvs/targets.csv")

# Convert 'date' column to datetime to extract year and month
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month_name"] = df["date"].dt.strftime("%B")

# Define the calendar order for months
month_order = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
df["month"] = pd.Categorical(df["month_name"], categories=month_order, ordered=True)


# Prepare Data Functions
def get_monthly_sales(selected_year):
    year_data = (
        df[df["year"] == selected_year]
        .groupby("month", as_index=False)
        .agg({"live_races_sales": "sum", "simulcast_sales": "sum"})
    )
    return year_data


def get_monthly_sales_extended(selected_year):
    year_data = (
        df[df["year"] == selected_year]
        .groupby("month", as_index=False)
        .agg(
            {
                "live_races_sales": "sum",
                "simulcast_sales": "sum",
                "live_races_total": "mean",
                "simulcast_days_total": "mean",
            }
        )
    )
    return year_data


def get_sales_target(month_name):
    target_row = df_targets[df_targets["Month"] == month_name]
    if not target_row.empty:
        return target_row["Target"].values[0]
    return 0


def format_percentage_change(value):
    if value is None or np.isnan(value):
        return "No Change"
    elif value > 0:
        return f"Up {value:.2f}%"
    elif value < 0:
        return f"Down {abs(value):.2f}%"
    else:
        return "No Change"


def format_currency(value):
    if value is None or np.isnan(value):
        return ""
    return f"${value:,.2f}"


def get_live_races_data(selected_month):
    current_year = df["year"].max()
    previous_year = current_year - 1

    metrics = {
        "Sales": "live_races_sales",
        "Purse": "live_races_purse",
        "No. of Races": "live_races_total",
    }

    data_frames = []

    for metric_name, column_name in metrics.items():
        current_data = df[
            (df["month_name"] == selected_month) & (df["year"] == current_year)
        ][column_name].sum()
        previous_data = df[
            (df["month_name"] == selected_month) & (df["year"] == previous_year)
        ][column_name].sum()

        variance = current_data - previous_data
        percentage_change = (
            (variance / previous_data * 100) if previous_data else np.nan
        )
        formatted_percentage_change = format_percentage_change(percentage_change)

        # Apply currency formatting to financial metrics
        if "Sales" in metric_name or "Purse" in metric_name:
            current_data = format_currency(current_data)
            previous_data = format_currency(previous_data)
            variance = format_currency(variance)

        data_frames.append(
            pd.DataFrame(
                {
                    "Metric": [metric_name],
                    str(previous_year): [previous_data],
                    str(current_year): [current_data],
                    "Variance": [variance],
                    "Percentage Change": [formatted_percentage_change],
                }
            )
        )

    combined_data = pd.concat(data_frames, ignore_index=True)
    return combined_data


def get_simulcast_data(selected_month):
    current_year = df["year"].max()
    previous_year = current_year - 1

    metrics = {
        "Sales": "simulcast_sales",
        "Average": "simulcast_average",  # New metric added
        "No. of Days": "simulcast_days_total",
    }

    data_frames = []

    for metric_name, column_name in metrics.items():
        current_data = df[
            (df["month_name"] == selected_month) & (df["year"] == current_year)
        ][column_name].mean()
        previous_data = df[
            (df["month_name"] == selected_month) & (df["year"] == previous_year)
        ][column_name].mean()

        variance = current_data - previous_data
        percentage_change = (
            ((variance / previous_data) * 100) if previous_data else np.nan
        )
        formatted_percentage_change = format_percentage_change(percentage_change)

        current_data_formatted = (
            format_currency(current_data)
            if "Sales" in metric_name
            else f"{current_data:,.2f}"
        )
        previous_data_formatted = (
            format_currency(previous_data)
            if "Sales" in metric_name
            else f"{previous_data:,.2f}"
        )
        variance_formatted = (
            format_currency(variance) if "Sales" in metric_name else f"{variance:,.2f}"
        )

        data_frames.append(
            pd.DataFrame(
                {
                    "Metric": [metric_name],
                    str(previous_year): [previous_data_formatted],
                    str(current_year): [current_data_formatted],
                    "Variance": [variance_formatted],
                    "Percentage Change": [formatted_percentage_change],
                }
            )
        )

    combined_data = pd.concat(data_frames, ignore_index=True)
    return combined_data


# Initialize Dash app
app = Dash(
    __name__,
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"
    ],
)
server = app.server

# Dash App Layout
app.layout = html.Div(
    className="container mx-auto px-4",
    children=[
        html.H1("Sales Dashboard", className="text-3xl font-bold my-8"),
        html.H2("Month Performance Comparison", className="text-xl font-semibold mb-4"),
        # Month Selection Dropdown
        html.Div(
            className="mb-4",
            children=[
                html.Label(
                    "Select Month:", className="block text-lg font-medium text-gray-700"
                ),
                dcc.Dropdown(
                    id="month-dropdown",
                    options=[{"label": month, "value": month} for month in month_order],
                    value=month_order[0],  # Default to January
                    className="block w-full mt-1 rounded-md border-gray-300 shadow-sm",
                ),
            ],
        ),
        # Live Races Comparison Table
        html.Div(
            className="mb-8",
            children=[
                html.Label(
                    "Live Races:",
                    className="block text-lg font-medium text-gray-700",
                ),
                html.Div(id="live-races-comparison-table"),
            ],
        ),
        # Simulcast Comparison Table
        html.Div(
            className="mb-8",
            children=[
                html.Label(
                    "Simulcast:",
                    className="block text-lg font-medium text-gray-700",
                ),
                html.Div(id="simulcast-comparison-table"),
            ],
        ),
        html.Div(
            className="flex flex-wrap",
            children=[
                html.Div(
                    className="w-full pr-4",
                    children=[
                        html.H2(
                            "Yearly Sales Data", className="text-xl font-semibold mb-4"
                        ),
                        dcc.Dropdown(
                            id="year-dropdown",
                            options=[
                                {"label": year, "value": year}
                                for year in sorted(df["year"].unique())
                            ],
                            value=df["year"].max(),
                            className="w-full py-2 px-4 mb-4 border rounded-lg",
                        ),
                        dcc.Graph(id="yearly-sales-graph"),
                    ],
                ),
                html.Div(
                    className="w-full pl-4",
                    children=[
                        html.H2(
                            "Live Races & Simulcast Days",
                            className="text-xl font-semibold mb-4",
                        ),
                        dcc.Dropdown(
                            id="race-day-dropdown",
                            options=[
                                {"label": year, "value": year}
                                for year in sorted(df["year"].unique())
                            ],
                            value=df["year"].max(),
                            className="w-full py-2 px-4 mb-4 border rounded-lg",
                        ),
                        dcc.Graph(id="race-day-trend-graph"),
                    ],
                ),
            ],
        ),
        html.Div(
            className="flex",
            children=[
                html.Div(
                    style={"width": "75%"},
                    children=[
                        html.H2(
                            "2024 Monthly Sales Comparison",
                            className="text-xl font-semibold mb-4",
                        ),
                        dcc.Graph(id="monthly-comparison-graph-2024"),
                    ],
                    className="inline-block align-top",
                ),
                html.Div(
                    style={"width": "25%", "margin-left": "1%"},
                    children=[
                        html.Div(
                            style={"margin-top": "10px"},
                            children=[
                                html.H2(
                                    "Monthly Sales Target",
                                    className="text-xl font-semibold mb-4",
                                ),
                                dcc.Dropdown(
                                    id="year-target-dropdown",
                                    options=[
                                        {"label": year, "value": year}
                                        for year in sorted(df["year"].unique())
                                    ],
                                    value=df["year"].max(),
                                    className="w-full py-2 px-4 mb-4 border rounded-lg",
                                ),
                                dcc.Dropdown(
                                    id="month-target-dropdown",
                                    options=[],
                                    value=None,
                                    className="w-full py-2 px-4 mb-4 border rounded-lg",
                                ),
                                dcc.Graph(id="sales-target-gauge"),
                            ],
                        ),
                    ],
                    className="inline-block align-top",
                ),
            ],
        ),
    ]
)


@app.callback(
    Output("live-races-comparison-table", "children"),
    [Input("month-dropdown", "value")],
)
def display_live_races_table(selected_month):
    live_races_data = get_live_races_data(selected_month)
    return dash_table.DataTable(
        data=live_races_data.to_dict("records"),
        columns=[
            {"name": "Metric", "id": "Metric"},
            {
                "name": str(df["year"].min()),
                "id": str(df["year"].min()),
            },  # Previous year column
            {
                "name": str(df["year"].max()),
                "id": str(df["year"].max()),
            },  # Current year column
            {"name": "Variance", "id": "Variance"},
            {"name": "Percentage Change", "id": "Percentage Change"},
        ],
        style_table={"overflowX": "auto"},
        style_header={"fontWeight": "bold", "textAlign": "right"},
        style_header_conditional=[
            {
                "if": {"column_id": "Metric"},
                "textAlign": "left",  # Specifically align the "Metric" header to the left
            }
        ],
        style_data_conditional=[
            {
                "if": {"column_id": "Metric"},
                "textAlign": "left",
                "fontWeight": "bold",
            },
            {
                "if": {
                    "filter_query": '{Percentage Change} contains "Up"',
                    "column_id": "Percentage Change",
                },
                "color": "green",
                "fontWeight": "bold",
                "textAlign": "right",
            },
            {
                "if": {
                    "filter_query": '{Percentage Change} contains "Down"',
                    "column_id": "Percentage Change",
                },
                "color": "red",
                "fontWeight": "bold",
                "textAlign": "right",
            },
        ],
    )


@app.callback(
    Output("simulcast-comparison-table", "children"), Input("month-dropdown", "value")
)
def display_simulcast_table(selected_month):
    simulcast_data = get_simulcast_data(selected_month)
    return [
        dash_table.DataTable(
            data=simulcast_data.to_dict("records"),
            columns=[
                {"name": "Metric", "id": "Metric"},
                {
                    "name": str(df["year"].min()),
                    "id": str(df["year"].min()),
                },  # Previous year column
                {
                    "name": str(df["year"].max()),
                    "id": str(df["year"].max()),
                },  # Current year column
                {"name": "Variance", "id": "Variance"},
                {"name": "Percentage Change", "id": "Percentage Change"},
            ],
            style_table={"overflowX": "auto"},
            style_header={"fontWeight": "bold", "textAlign": "right"},
             style_header_conditional=[
            {
                "if": {"column_id": "Metric"},
                "textAlign": "left",  # Specifically align the "Metric" header to the left
            }
        ],
            style_data_conditional=[
                {
                    "if": {"column_id": "Metric"},
                    "textAlign": "left",
                    "fontWeight": "bold",
                },
                {
                    "if": {"column_id": "Percentage Change"},
                    "color": "green",
                    "fontWeight": "bold",
                    "textAlign": "right",
                },
                {
                    "if": {
                        "filter_query": '{Percentage Change} contains "Down"',
                        "column_id": "Percentage Change",
                    },
                    "color": "red",
                    "fontWeight": "bold",
                    "textAlign": "right",
                },
            ],
        )
    ]


# Callback to Update Yearly Sales Graph
@app.callback(Output("yearly-sales-graph", "figure"), [Input("year-dropdown", "value")])
def update_yearly_sales_graph(selected_year):
    monthly_sales = get_monthly_sales(selected_year)

    trace1 = go.Bar(
        x=monthly_sales["month"],
        y=monthly_sales["live_races_sales"],
        name="Live Races Sales",
        marker_color="blue",
    )
    trace2 = go.Bar(
        x=monthly_sales["month"],
        y=monthly_sales["simulcast_sales"],
        name="Simulcast Sales",
        marker_color="green",
    )

    return {
        "data": [trace1, trace2],
        "layout": go.Layout(
            title=f"Monthly Sales Data for {selected_year}",
            xaxis={
                "title": "Month",
                "categoryorder": "array",
                "categoryarray": month_order,
            },
            yaxis={"title": "Sales Amount"},
            barmode="group",
        ),
    }


# Callback to Update Live Races & Simulcast Days Graph
@app.callback(
    Output("race-day-trend-graph", "figure"), [Input("race-day-dropdown", "value")]
)
def update_race_day_trend_graph(selected_year):
    monthly_data = get_monthly_sales_extended(selected_year)
    trace1 = go.Scatter(
        x=monthly_data["month"],
        y=monthly_data["live_races_total"],
        mode="lines+markers",
        name="Live Races",
        marker=dict(color="DodgerBlue"),
    )
    trace2 = go.Bar(
        x=monthly_data["month"],
        y=monthly_data["simulcast_days_total"],
        name="Simulcast Days",
        marker=dict(color="Crimson"),
    )
    return {
        "data": [trace1, trace2],
        "layout": go.Layout(
            title=f"Live Races & Simulcast Days for {selected_year}",
            xaxis={
                "title": "Month",
                "categoryorder": "array",
                "categoryarray": month_order,
            },
            yaxis={"title": "Count"},
            barmode="group",
            hovermode="closest",
        ),
    }


# Callback to Update Monthly Sales Comparison Graph for 2024
@app.callback(
    Output("monthly-comparison-graph-2024", "figure"),
    Input("year-dropdown", "value"),  # This input is just to trigger the update
)
def update_monthly_comparison_graph_2024(_):
    monthly_sales_2024 = get_monthly_sales(2024)

    trace1 = go.Scatter(
        x=monthly_sales_2024["month"],
        y=monthly_sales_2024["live_races_sales"],
        mode="lines+markers",
        name="Live Races Sales 2024",
        marker_color="blue",
        line=dict(dash="solid"),
    )
    trace2 = go.Scatter(
        x=monthly_sales_2024["month"],
        y=monthly_sales_2024["simulcast_sales"],
        mode="lines+markers",
        name="Simulcast Sales 2024",
        marker_color="green",
        line=dict(dash="solid"),
    )

    # Assuming you want to compare with the previous year (2023)
    monthly_sales_2023 = get_monthly_sales(2023)
    trace3 = go.Scatter(
        x=monthly_sales_2023["month"],
        y=monthly_sales_2023["live_races_sales"],
        mode="lines+markers",
        name="Live Races Sales 2023",
        marker_color="blue",
        line=dict(dash="dot"),
    )
    trace4 = go.Scatter(
        x=monthly_sales_2023["month"],
        y=monthly_sales_2023["simulcast_sales"],
        mode="lines+markers",
        name="Simulcast Sales 2023",
        marker_color="green",
        line=dict(dash="dot"),
    )

    return {
        "data": [trace1, trace2, trace3, trace4],
        "layout": go.Layout(
            title="Monthly Sales Comparison for 2024 vs 2023",
            xaxis={
                "title": "Month",
                "categoryorder": "array",
                "categoryarray": month_order,
            },
            yaxis={"title": "Sales Amount"},
            hovermode="closest",
        ),
    }


# Callback to update the sales target gauge based on the selected month and year
@app.callback(
    Output("sales-target-gauge", "figure"),
    [Input("year-target-dropdown", "value"), Input("month-target-dropdown", "value")],
)
def update_sales_target_gauge(selected_year, selected_month):
    # Filter for the selected year and month
    selected_date = f"{selected_year}-{selected_month.zfill(2)}-01"  # Ensure the date format matches the CSV
    total_sales = (
        df[(df["year"] == selected_year) & (df["month_name"] == selected_month)][
            "live_races_sales"
        ].sum()
        / 1e6
    )  # Convert to millions
    # Check if there's a matching target for the selected date
    target_row = df_targets[df_targets["Month"] == selected_date]
    if not target_row.empty:
        sales_target = target_row["Target"].values[0] / 1e6  # Convert to millions
    else:
        # Set the sales target to 1 billion if no target is found
        sales_target = 1000  # 1 billion in millions

    # Create the gauge figure
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=total_sales,
            number={"suffix": "M"},  # Add 'M' suffix to the number
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": f"Sales Target for {selected_month} {selected_year} (Millions)"
            },
            gauge={
                "axis": {
                    "range": [0, max(total_sales, sales_target)]
                },  # Adjust the gauge range
                "bar": {"color": "blue"},
                "steps": [
                    {"range": [0, sales_target], "color": "lightblue"},
                    {
                        "range": [sales_target, sales_target],
                        "color": "blue",
                    },  # The step ends at the target itself
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": sales_target,
                },
            },
        )
    )

    return fig


# Callback to populate the month dropdown based on the selected year
@app.callback(
    Output("month-target-dropdown", "options"), [Input("year-target-dropdown", "value")]
)
def set_month_target_options(selected_year):
    months_in_year = df[df["year"] == selected_year]["month_name"].unique()
    return [{"label": month, "value": month} for month in months_in_year]


@app.callback(
    Output("month-target-dropdown", "value"),
    [Input("month-target-dropdown", "options")],
)
def set_month_target_value(available_months):
    if available_months:
        return available_months[0]["value"]
    return None


# Step 5: Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)
