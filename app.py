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
app.title = "SVREL Sales Analysis"
server = app.server

# Dash App Layout
app.layout = html.Div(
    style={
        "display": "flex",
        "flexDirection": "column",
        "minHeight": "100vh",
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
                html.H1("Sales Analysis", className="text-4xl font-bold my-8"),
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
                html.H2(
                    "Monthly Targets",
                    className="text-2xl font-semibold mb-4 mt-10 text-center",
                ),
                html.Div(
                    className="flex justify-center items-center mt-4",
                    children=[
                        dcc.Graph(id="live-races-sales-gauge", className="mr-4"),
                        dcc.Graph(id="simulcast-sales-gauge", className="ml-4"),
                    ],
                ),
                html.H2(
                    "Metric Comparison", className="text-2xl font-semibold mb-4 mt-10"
                ),
                html.Div(
                    className="mb-4",
                    children=[
                        html.Label(
                            "Select Metric:",
                            className="block text-lg font-medium text-gray-700",
                        ),
                        dcc.Dropdown(
                            id="metric-dropdown",
                            options=[
                                {"label": "Local Sales", "value": "live_races_sales"},
                                {"label": "Purses", "value": "live_races_purse"},
                                {"label": "Race Days", "value": "live_races_total"},
                                {
                                    "label": "Simulcast Sales",
                                    "value": "simulcast_sales",
                                },
                                {"label": "Average", "value": "simulcast_average"},
                                {"label": "Days", "value": "simulcast_days_total"},
                            ],
                            value="live_races_sales",  # Default metric
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


# Callback to update the live races sales gauge
@app.callback(
    Output("live-races-sales-gauge", "figure"),
    [Input("month-dropdown", "value")],
)
def update_live_races_sales_gauge(selected_month):
    selected_year = int(df["year"].max())
    # Filter for the selected year and month
    total_sales = (
        df[(df["year"] == selected_year) & (df["month_name"] == selected_month)][
            "live_races_sales"
        ].sum()
        / 1e6
    )  # Convert to millions
    # Get sales target for the selected month
    sales_target = get_sales_target(selected_month) / 1e6  # Convert to millions

    # Check if there's a matching target for the selected date
    target_row = df_targets[df_targets["Month"] == selected_month]
    if not target_row.empty:
        sales_target = target_row["Target"].values[0] / 1e6  # Convert to millions
    else:
        # Set the sales target to 1 billion if no target is found
        sales_target = 1000  # 1 billion in millions

    # Set the maximum range for the gauge to the sales target
    max_range = sales_target

    # Create the gauge figure
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=total_sales,
            number={"suffix": "M"},  # Add 'M' suffix to the number
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": f"Live Races Sales for {selected_month} {selected_year} (Millions)"
            },
            gauge={
                "axis": {"range": [0, max_range]},  # Adjust the gauge range
                "bar": {"color": "blue"},
                "steps": [
                    {"range": [0, sales_target], "color": "lightblue"},
                    {
                        "range": [sales_target, max_range],
                        "color": "blue",
                    },  # The step ends at the maximum range
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


# Callback to update the simulcast sales gauge
@app.callback(
    Output("simulcast-sales-gauge", "figure"),
    [Input("month-dropdown", "value")],
)
def update_simulcast_sales_gauge(selected_month):
    selected_year = int(df["year"].max())
    # Filter for the selected year and month
    total_sales = (
        df[(df["year"] == selected_year) & (df["month_name"] == selected_month)][
            "simulcast_sales"
        ].sum()
        / 1e6
    )  # Convert to millions
    # Get sales target for the selected month
    sales_target = get_sales_target(selected_month) / 1e6  # Convert to millions

    # Check if there's a matching target for the selected date
    target_row = df_targets[df_targets["Month"] == selected_month]
    if not target_row.empty:
        sales_target = target_row["Target"].values[0] / 1e6  # Convert to millions
    else:
        # Set the sales target to 1 billion if no target is found
        sales_target = 1000  # 1 billion in millions

    # Set the maximum range for the gauge to the sales target
    max_range = sales_target

    # Create the gauge figure
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=total_sales,
            number={"suffix": "M"},  # Add 'M' suffix to the number
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": f"Simulcast Sales for {selected_month} {selected_year} (Millions)"
            },
            gauge={
                "axis": {"range": [0, max_range]},  # Adjust the gauge range
                "bar": {"color": "blue"},
                "steps": [
                    {"range": [0, sales_target], "color": "lightblue"},
                    {
                        "range": [sales_target, max_range],
                        "color": "blue",
                    },  # The step ends at the maximum range
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


# Step 5: Run the Dash App
if __name__ == "__main__":
    app.run_server(debug=True)
