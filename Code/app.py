import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the CSV data, specifying dtype for columns with mixed types
data = pd.read_csv('C:/Users/Fikri/Documents/Data_Kpp/daily_rent_detail.csv', 
                   dtype={'start_station_id': str, 'end_station_id': str})

# Clean 'started_at' column (remove unwanted characters like '.510' if present)
data['started_at'] = data['started_at'].astype(str).str.replace(r'\.510', '', regex=True)

# Convert 'started_at' column to datetime format, handling errors by coercing invalid values to NaT
data['started_at'] = pd.to_datetime(data['started_at'], errors='coerce')

# Drop rows with NaT in the 'started_at' column (if any)
data = data.dropna(subset=['started_at'])

# Extract year from 'started_at' column and create a new column 'year'
data['year'] = data['started_at'].dt.year

# Create Dash app
app = dash.Dash(__name__)

# Dropdown options for 'rideable_type' and 'member_casual'
column_options = [{'label': 'Rideable Type', 'value': 'rideable_type'},
                  {'label': 'User Type', 'value': 'member_casual'}]

# Layout of the app
app.layout = html.Div([
    html.H1("Interactive Data Analysis"),
    
    # Dropdown for selecting the column to visualize
    dcc.Dropdown(
        id='column-dropdown',
        options=column_options,
        value='rideable_type'  # Default value
    ),
    
    # Slider for selecting the year range (based on the 'started_at' column)
    dcc.Slider(
        id='year-slider',
        min=data['year'].min(),
        max=data['year'].max(),
        value=data['year'].min(),
        marks={str(year): str(year) for year in range(data['year'].min(), data['year'].max() + 1)},
    ),
    
    # Graph to show the updated plot
    dcc.Graph(id='updated-graph')
])

# Callback to update the graph based on the selected year and column
@app.callback(
    Output('updated-graph', 'figure'),
    [Input('year-slider', 'value'), Input('column-dropdown', 'value')]
)
def update_graph(selected_year, selected_column):
    # Filter data up to the selected year
    filtered_data = data[data['year'] <= selected_year]
    
    # Group by the selected column ('rideable_type' or 'member_casual') and year, and count the occurrences
    grouped_data = filtered_data.groupby(['year', selected_column]).size().reset_index(name='count')
    
    # Calculate the cumulative count for each year
    grouped_data['cumulative_count'] = grouped_data.groupby(selected_column)['count'].cumsum()
    
    # Generate a bar chart with cumulative count
    fig = px.bar(grouped_data, x='year', y='cumulative_count', color=selected_column,
                 title=f"Cumulative Data for {selected_column} in {selected_year}")
    
    return fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
