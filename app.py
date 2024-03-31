from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go
import pandas as pd

# Load the CSV data into a DataFrame
df = pd.read_csv('data/csvs/sales.csv')

# Convert 'date' column to datetime to extract year and month
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year  # Extract year for filtering
df['month_name'] = df['date'].dt.strftime('%B')  # Extract month name for display

# Create a month order based on the CSV ordering
month_order = df['month_name'].unique()

# Create a categorical type for preserving the month order
df['month'] = pd.Categorical(df['month_name'], categories=month_order, ordered=True)

# Step 1: Prepare Data Functions
def get_monthly_sales(selected_year):
    # Filter data for the selected year and group by month with the preserved order
    year_data = df[df['year'] == selected_year].groupby('month', as_index=False, observed=False).agg({
        'live_races_sales': 'sum',
        'simulcast_sales': 'sum'
    })
    return year_data

# Initialize Dash app
app = Dash(__name__)

# Step 2: Dash App Layout
app.layout = html.Div(children=[
    html.H1("Yearly Sales Dashboard"),
    
    # Dropdown to select the year
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in df['year'].unique()],
        value=df['year'].iloc[0]  # Default value to the first year in the data
    ),
    
    # Graph to display sales data
    dcc.Graph(id='sales-graph')
])

# Step 3: Callback to Update Graph
@app.callback(
    Output('sales-graph', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_graph(selected_year):
    monthly_sales = get_monthly_sales(selected_year)

    # Creating a bar chart with live and simulcast sales
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

    figure = {
        'data': [trace1, trace2],
        'layout': {
            'title': f'Monthly Sales Data for {selected_year}',
            'xaxis': {'title': 'Month', 'type': 'category'},
            'yaxis': {'title': 'Sales Amount'},
            'barmode': 'group'
        }
    }

    return figure

# Step 4: Run the Dash App
if __name__ == '__main__':
    app.run_server(debug=True)
