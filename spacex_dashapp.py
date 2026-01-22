# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read SpaceX data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Prepare launch site dropdown values
unique_launch_sites = spacex_df['Launch Site'].unique()
launch_sites = [{'label': 'All Sites', 'value': 'All Sites'}]

for site in unique_launch_sites:
    launch_sites.append({'label': site, 'value': site})

# Slider marks
marks_dict = {i: f"{i} Kg" for i in range(0, 11001, 1000)}

# Create Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    dcc.Dropdown(
        id='site-dropdown',
        options=launch_sites,
        value='All Sites',
        searchable=True,
        placeholder='Select a Launch Site'
    ),

    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    dcc.RangeSlider(
        id='payload_slider',
        min=0,
        max=10000,
        step=1000,
        marks=marks_dict,
        value=[min_payload, max_payload]
    ),

    html.Br(),

    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'All Sites':
        filtered_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            filtered_df,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            filtered_df,
            names='class',
            title=f'Total Success Launches for Site {selected_site}'
        )
    return fig

# Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload_slider', 'value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        spacex_df['Payload Mass (kg)'].between(low, high)
    ]

    if selected_site != 'All Sites':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        title = f'Correlation between Payload and Success for site {selected_site}'
    else:
        title = 'Correlation between Payload and Success for all Sites'

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title
    )
    return fig

# Run the application
if __name__ == '__main__':
    app.run_server()

