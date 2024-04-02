from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# Load the CSV data into a DataFrame
df = pd.read_csv("data/csvs/sales.csv")

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

excess_step_color = "#6ee7b7"


# Prepare Data Functions
def get_sales_target(target_file, month_name, year):
    df_targets = pd.read_csv("data/csvs/" + target_file + ".csv")
    # Ensure the 'Month' column is in datetime format
    df_targets["Month"] = pd.to_datetime(df_targets["Month"])
    # Find the target for the given month and year
    target_row = df_targets[
        (df_targets["Month"].dt.strftime("%B") == month_name)
        & (df_targets["Month"].dt.year == year)
    ]
    if not target_row.empty:
        return target_row["Target"].values[0]
    return 0


def format_percentage_change(value):
    if value is None or np.isnan(value):
        return "No Change"  # Or use "Data Not Available" or "-"
    elif value > 0:
        return f"Up {value:.2f}%"
    elif value < 0:
        return f"Down {abs(value):.2f}%"
    else:
        return "No Change"


def format_currency(value):
    if value is None or np.isnan(value):
        return "-"  # Here you can return "-" or "Data Not Available"
    if value < 0:
        return f"-${abs(value):,.2f}"
    else:
        return f"${value:,.2f}"


def format_value(metric_name, value):
    if np.isnan(value) or value is None:
        return "-"
    if (
        "Revenue" in metric_name
        or "Purse Structure" in metric_name
        or "Average" in metric_name
    ):
        return format_currency(value)
    else:  # For non-currency metrics like "No. of Races" or "No. of Days"
        return f"{int(value)}"  # Use int() to convert float to int and remove decimals


def get_live_races_data(selected_month):
    current_year = df["year"].max()
    previous_year = current_year - 1

    metrics = {
        "Revenue": "live_racing_revenue",
        "Purse Structure": "purse_structure",
        "No. of Races": "number_of_live_races",
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

        # Format data based on metric type
        current_data_formatted = format_value(metric_name, current_data)
        previous_data_formatted = format_value(metric_name, previous_data)
        variance_formatted = format_value(metric_name, variance)

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


def get_simulcast_data(selected_month):
    current_year = df["year"].max()
    previous_year = current_year - 1

    metrics = {
        "Revenue": "simulcast_revenue",
        "Daily Averages": "simulcast_daily_averages",
        "No. of Days": "number_of_simulcast_days",
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

        # Format data based on metric type
        current_data_formatted = format_value(metric_name, current_data)
        previous_data_formatted = format_value(metric_name, previous_data)
        variance_formatted = format_value(metric_name, variance)

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
app.title = "SVREL Sales Analysis Dashboard"
server = app.server

# Dash App Layout
app.layout = html.Div(
    style={
        "display": "flex",
        "flexDirection": "column",
        "minHeight": "100vh",
        "font-size": "1.35em",
        # "backgroundColor": "#f8fafc",
    },  # Main container with flex display
    children=[
        # Full-width Header Bar with Logo
        html.Div(
            className="bg-white w-full p-4 flex justify-between items-center shadow-md",  # Adjust the background color and padding as needed
            children=[
                html.Img(
                    src=app.get_asset_url("img/logo.png"), style={"height": "50px"}
                ),  # Adjust the height as needed
                html.H1("Caymanas Park", className="text-white text-xl"),
            ],
        ),
        # Container for the rest of the content
        html.Div(
            className="flex-grow container mx-auto px-4",
            children=[
                html.H1(
                    "Sales Analysis Dashboard", className="text-4xl font-bold my-8"
                ),
                html.H2(
                    "Monthly Performance Comparison",
                    className="text-2xl font-semibold mb-4",
                ),
                # Month Selection Dropdown
                html.Div(
                    className="mb-4",
                    children=[
                        html.Label(
                            "Select Month:",
                            className="block text-lg font-medium text-gray-700",
                        ),
                        dcc.Dropdown(
                            id="month-dropdown",
                            options=[
                                {"label": month, "value": month}
                                for month in month_order
                            ],
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
                            "Live Racing:",
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
                html.H2(
                    "Monthly Targets",
                    className="text-2xl font-semibold mb-4 mt-10 text-center",
                ),
                html.Div(
                    className="flex justify-center items-center mt-4",
                    children=[
                        dcc.Graph(id="live-race-sales-gauge", className="mr-4"),
                        dcc.Graph(id="simulcast-sales-gauge", className="ml-4"),
                    ],
                ),
                html.H2("KPI Review", className="text-2xl font-semibold mb-4 mt-10"),
                html.Div(
                    className="mb-4",
                    children=[
                        html.Label(
                            "Select an Option:",
                            className="block text-lg font-medium text-gray-700",
                        ),
                        dcc.Dropdown(
                            id="metric-dropdown",
                            options=[
                                {
                                    "label": "Live Racing Revenue",
                                    "value": "live_racing_revenue",
                                },
                                {
                                    "label": "Purse Structure",
                                    "value": "purse_structure",
                                },
                                {
                                    "label": "No. of Live Races",
                                    "value": "number_of_live_races",
                                },
                                {
                                    "label": "Simulcast Revenue",
                                    "value": "simulcast_revenue",
                                },
                                {
                                    "label": "Simulcast Daily Averages",
                                    "value": "simulcast_daily_averages",
                                },
                                {
                                    "label": "No. of Simulcast Days",
                                    "value": "number_of_simulcast_days",
                                },
                            ],
                            value="live_racing_revenue",  # Default metric
                            className="block w-full mt-1 rounded-md border-gray-300 shadow-sm",
                        ),
                    ],
                ),
                dcc.Graph(id="monthly-metric-comparison-graph", className="mt-4"),
            ],
        ),
        html.Div(
            className="bg-gray-800 text-white py-4 px-8 flex justify-center items-center",
            children=[html.H1("Developed by Devmassive LLC", className="text-sm")],
            style={"width": "100%"},
        ),
    ],
)


# Callback to Live Races
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
        style_header={"fontWeight": "bold", "textAlign": "right", "background-color": "#bae6fd"},
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


# Callback to Simulcast
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
            style_header={"fontWeight": "bold", "textAlign": "right", "background-color": "#fed7aa"},
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


# Callback to update the graph based on selected metric
@app.callback(
    Output("monthly-metric-comparison-graph", "figure"),
    [Input("metric-dropdown", "value")],
)
def update_graph(selected_metric):
    current_year = df["year"].max()
    previous_year = current_year - 1

    current_month_data = df[(df["year"] == current_year)][
        ["month_name", selected_metric]
    ]
    previous_year_data = df[(df["year"] == previous_year)][
        ["month_name", selected_metric]
    ]

    # Create traces for current year and previous year
    trace1 = go.Scatter(
        x=current_month_data["month_name"],
        y=current_month_data[selected_metric],
        mode="lines+markers",
        name=f"Current Year ({current_year})",
        marker_color="blue",
        line=dict(dash="solid"),
    )

    trace2 = go.Scatter(
        x=previous_year_data["month_name"],
        y=previous_year_data[selected_metric],
        mode="lines+markers",
        name=f"Previous Year ({previous_year})",
        marker_color="#aaaaaa",
        line=dict(dash="dot"),
    )

    return {
        "data": [trace1, trace2],
        "layout": go.Layout(
            title=f"Comparison of {selected_metric.replace('_', ' ').title()} between {current_year} and {previous_year}",
            xaxis={"title": "Month"},
            yaxis={"title": selected_metric.replace("_", " ").title()},
        ),
    }


@app.callback(
    Output("live-race-sales-gauge", "figure"),
    [Input("month-dropdown", "value")],
)
def update_live_racing_revenue_gauge(selected_month):
    selected_year = int(df["year"].max())
    total_sales = (
        df[(df["year"] == selected_year) & (df["month_name"] == selected_month)][
            "live_racing_revenue"
        ].sum()
        / 1e6
    )
    sales_target = get_sales_target("live-targets", selected_month, selected_year) / 1e6
    bar_color = "#00a2ff"
    step_color = "#e5f6fd"

    # Use max to ensure the gauge's range accommodates both sales and target
    max_range = max(sales_target, total_sales)

    title_text = f"Live Racing Revenue for {selected_month} {selected_year} (Millions)"

    fig_live_races = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=total_sales,
            number={"suffix": "M"},
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title_text},
            gauge={
                "axis": {"range": [0, max_range]},
                "bar": {"color": bar_color},
                "steps": [
                    {"range": [0, sales_target], "color": step_color},
                    {"range": [sales_target, max_range], "color": excess_step_color},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": sales_target,
                },
            },
        )
    )

    # Add annotation for the target
    fig_live_races.add_annotation(
        x=0.5,
        y=0.3,
        text=f"Target: {sales_target:.2f}M",
        showarrow=False,
        font=dict(size=16, color="#475569"),
    )

    return fig_live_races


@app.callback(
    Output("simulcast-sales-gauge", "figure"),
    [Input("month-dropdown", "value")],
)
def update_simulcast_revenue_gauge(selected_month):
    selected_year = int(df["year"].max())
    total_sales = (
        df[(df["year"] == selected_year) & (df["month_name"] == selected_month)][
            "simulcast_revenue"
        ].sum()
        / 1e6
    )
    sales_target = (
        get_sales_target("simulcast-targets", selected_month, selected_year) / 1e6
    )
    bar_color = "#fa8231"
    step_color = "#ffe5d8"

    # Use max to ensure the gauge's range accommodates both sales and target
    max_range = max(sales_target, total_sales)

    title_text = f"Simulcast Revenue for {selected_month} {selected_year} (Millions)"

    fig_simulcast = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=total_sales,
            number={"suffix": "M"},
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": title_text},
            gauge={
                "axis": {"range": [0, max_range]},
                "bar": {"color": bar_color},
                "steps": [
                    {"range": [0, sales_target], "color": step_color},
                    {"range": [sales_target, max_range], "color": excess_step_color},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": sales_target,
                },
            },
        )
    )

    # Add annotation for the target
    fig_simulcast.add_annotation(
        x=0.5,
        y=0.3,
        text=f"Target: {sales_target:.2f}M",
        showarrow=False,
        font=dict(size=16, color="#475569"),
    )

    return fig_simulcast


# Step 5: Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)
