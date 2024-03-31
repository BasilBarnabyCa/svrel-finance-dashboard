from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go
import pandas as pd

# Load the CSV data into a DataFrame
df = pd.read_csv('data/csvs/sales.csv')

# Convert 'date' column to datetime to extract year and month
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month_name'] = df['date'].dt.strftime('%B')

# Define the calendar order for months
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
df['month'] = pd.Categorical(df['month_name'], categories=month_order, ordered=True)

# Step 1: Prepare Data Functions
def get_monthly_sales(selected_year):
    year_data = df[df['year'] == selected_year].groupby('month', as_index=False).agg({
        'live_races_sales': 'sum',
        'simulcast_sales': 'sum'
    })
    return year_data

# Initialize Dash app
app = Dash(__name__)

# Step 2: Dash App Layout
app.layout = html.Div(children=[
    html.H1("Sales Dashboard"),

    html.Div([
        html.H2("Yearly Sales Data"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in sorted(df['year'].unique())],
            value=df['year'].min()
        ),
        dcc.Graph(id='yearly-sales-graph')
    ]),

    html.Div([
        html.H2("2024 Monthly Sales Comparison"),
        dcc.Graph(id='monthly-comparison-graph-2024')
    ])
])

# Step 3: Callback to Update Yearly Sales Graph
@app.callback(
    Output('yearly-sales-graph', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_yearly_sales_graph(selected_year):
    monthly_sales = get_monthly_sales(selected_year)

    trace1 = go.Bar(
        x=monthly_sales['month'],
        y=monthly_sales['live_races_sales'],
        name='Live Races Sales',
        marker_color='blue'
    )
    trace2 = go.Bar(
        x=monthly_sales['month'],
        y=monthly_sales['simulcast_sales'],
        name='Simulcast Sales',
        marker_color='green'
    )

    return {
        'data': [trace1, trace2],
        'layout': go.Layout(
            title=f'Monthly Sales Data for {selected_year}',
            xaxis={'title': 'Month', 'categoryorder': 'array', 'categoryarray': month_order},
            yaxis={'title': 'Sales Amount'},
            barmode='group'
        )
    }

# Step 4: Callback to Update Monthly Sales Comparison Graph for 2024
@app.callback(
    Output('monthly-comparison-graph-2024', 'figure'),
    Input('year-dropdown', 'value')  # This input is just to trigger the update
)
def update_monthly_comparison_graph_2024(_):
    monthly_sales_2024 = get_monthly_sales(2024)

    trace1 = go.Scatter(
        x=monthly_sales_2024['month'],
        y=monthly_sales_2024['live_races_sales'],
        mode='lines+markers',
        name='Live Races Sales 2024',
        marker_color='blue',
        line=dict(dash='solid')
    )
    trace2 = go.Scatter(
        x=monthly_sales_2024['month'],
        y=monthly_sales_2024['simulcast_sales'],
        mode='lines+markers',
        name='Simulcast Sales 2024',
        marker_color='green',
        line=dict(dash='solid')
    )

    # Assuming you want to compare with the previous year (2023)
    monthly_sales_2023 = get_monthly_sales(2023)
    trace3 = go.Scatter(
        x=monthly_sales_2023['month'],
        y=monthly_sales_2023['live_races_sales'],
        mode='lines+markers',
        name='Live Races Sales 2023',
        marker_color='blue',
        line=dict(dash='dot')
    )
    trace4 = go.Scatter(
        x=monthly_sales_2023['month'],
        y=monthly_sales_2023['simulcast_sales'],
        mode='lines+markers',
        name='Simulcast Sales 2023',
        marker_color='green',
        line=dict(dash='dot')
    )

    return {
        'data': [trace1, trace2, trace3, trace4],
        'layout': go.Layout(
            title='Monthly Sales Comparison for 2024 vs 2023',
            xaxis={'title': 'Month', 'categoryorder': 'array', 'categoryarray': month_order},
            yaxis={'title': 'Sales Amount'},
            hovermode='closest'
        )
    }

# Step 5: Run the Dash App
if __name__ == '__main__':
    app.run_server(debug=True)
