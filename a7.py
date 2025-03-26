# Published Dashboard: https://live-fifa-world-cup-map-a7.onrender.com

import numpy as np
import pandas as pd
import dash
import jupyter_dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from jupyter_dash import JupyterDash

# Create the dataset for World Cup finals
data = {
    'Year': [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 
             1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022],
    'Winner': ['Uruguay', 'Italy', 'Italy', 'Uruguay', 'West Germany', 'Brazil', 
               'Brazil', 'England', 'Brazil', 'West Germany', 'Argentina', 'Italy', 
               'Argentina', 'West Germany', 'Brazil', 'France', 'Brazil', 'Italy', 
               'Spain', 'Germany', 'France', 'Argentina'],
    'RunnerUp': ['Argentina', 'Czechoslovakia', 'Hungary', 'Brazil', 'Hungary', 'Sweden', 
                 'Czechoslovakia', 'West Germany', 'Italy', 'Netherlands', 'Netherlands', 
                 'West Germany', 'West Germany', 'Argentina', 'Italy', 'Brazil', 'Germany', 
                 'France', 'Netherlands', 'Argentina', 'Croatia', 'France']
}
df = pd.DataFrame(data)

# Standardize country names: Merge "West Germany" into "Germany"
df['Winner'] = df['Winner'].replace({'West Germany': 'Germany'})
df['RunnerUp'] = df['RunnerUp'].replace({'West Germany': 'Germany'})

df.head()

# Aggregate wins by country
win_counts = df['Winner'].value_counts().reset_index()
win_counts.columns = ['Country', 'Wins']

# Map winners to their ISO-3 codes for the choropleth map
iso_mapping = {
    'Uruguay': 'URY',
    'Italy': 'ITA',
    'Germany': 'DEU',
    'Brazil': 'BRA',
    'England': 'GBR',
    'Argentina': 'ARG',
    'France': 'FRA',
    'Spain': 'ESP'
}
win_counts['ISO'] = win_counts['Country'].map(iso_mapping)

win_counts

# Initialize the Dash app
app = JupyterDash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("FIFA World Cup Finals Dashboard", style={'text-align': 'center'}),
    
    # Choropleth Map displaying wins by country (increased size)
    dcc.Graph(
        id='choropleth-map',
        style={'height': '700px', 'width': '100%'},
        figure=px.choropleth(
            win_counts,
            locations='ISO',
            color='Wins',
            hover_name='Country',
            color_continuous_scale=px.colors.sequential.Plasma,
            title='World Cup Wins by Country',
            labels={'Wins': 'Number of Wins'}
        )
    ),
    
    html.H2("Interactive Components", style={'text-align': 'center'}),
    
    # Dropdown for country selection to view win count
    html.Div([
        html.H3("Select a country to view number of wins:"),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': c, 'value': c} for c in win_counts['Country']],
            placeholder="Select a country"
        ),
        html.Div(id='win-count-display', style={'margin-top': '10px'})
    ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top'}),
    
    # Dropdown for year selection to view the final match result
    html.Div([
        html.H3("Select a World Cup year to view the final result:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in df['Year']],
            placeholder="Select a year"
        ),
        html.Div(id='final-result-display', style={'margin-top': '10px'})
    ], style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top'}),
    
    # List of countries that have won the World Cup at the bottom
    html.Div([
        html.H3("Countries that have won the World Cup:"),
        html.Ul([html.Li(country) for country in win_counts['Country']])
    ], style={'width': '100%', 'text-align': 'center', 'margin-top': '20px'})
])

# Callback to update win count when a country is selected
@app.callback(
    Output('win-count-display', 'children'),
    Input('country-dropdown', 'value')
)
def display_win_count(selected_country):
    if selected_country is None:
        return ""
    count = win_counts.loc[win_counts['Country'] == selected_country, 'Wins'].values[0]
    return html.P(f"{selected_country} has won the World Cup {count} time{'s' if count != 1 else ''}.")

# Callback to display the final match result when a year is selected
@app.callback(
    Output('final-result-display', 'children'),
    Input('year-dropdown', 'value')
)
def display_final_result(selected_year):
    if selected_year is None:
        return ""
    record = df[df['Year'] == selected_year].iloc[0]
    return html.P(f"In {selected_year}, {record['Winner']} won the final against {record['RunnerUp']}.")

if __name__ == '__main__':
    # When running locally for development, you can run without the 'mode' parameter:
    app.run_server(debug=True, use_reloader=False)

