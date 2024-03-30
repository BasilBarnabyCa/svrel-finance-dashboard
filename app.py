from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go
import pandas as pd

# Step 1: Prepare Data Functions
def load_and_aggregate_sales(sheet_name):
    df = pd.read_excel('data/sales.xlsx', sheet_name=sheet_name, skiprows=2)  # Adjust path and skiprows as necessary
    print(df.head())
    df['SALES'] = pd.to_numeric(df['SALES'], errors='coerce')  # Adjust 'SALES' if your column name is different
    df = df.dropna(subset=['SALES'])

    total_sales = df['SALES'].sum()
    average_sales = df['SALES'].mean()

    return total_sales, average_sales

# Initialize Dash app
app = Dash(__name__)

# Step 2: Dash App Layout
app.layout = html.Div(children=[
    html.H1("Sales Dashboard"),
    
    dcc.Dropdown(
        id='month-dropdown',
        options=[{'label': month, 'value': month} for month in ['July 2020', 'August 2020', '...']],  # Populate with all relevant months
        value='July 2020'  # Default value
    ),
    
    dcc.Graph(id='sales-graph')
])

# Step 3: Callback to Update Graph
@app.callback(
    Output('sales-graph', 'figure'),
    [Input('month-dropdown', 'value')]
)
def update_graph(selected_month):
    total_sales, average_sales = load_and_aggregate_sales(selected_month)

    # Creating a bar chart with total and average sales
    data = [
        go.Bar(x=['Total Sales', 'Average Sales'], y=[total_sales, average_sales], marker_color=['blue', 'green'])
    ]

    figure = {
        'data': data,
        'layout': {
            'title': f'Sales Data for {selected_month}',
            'xaxis': {'title': 'Metric'},
            'yaxis': {'title': 'Amount'}
        }
    }

    return figure

# Step 4: Run the Dash App
if __name__ == '__main__':
    app.run_server(debug=True)
