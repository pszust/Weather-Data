import plotly.graph_objects as go # or plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import re
import numpy as np


data_dir = 'd:/Katalog 1/Projekty/Weather/data/'
data_dir = ''
latlon = pd.read_csv(data_dir + 'latlon.csv')

df = pd.read_csv(data_dir + 'all.csv')
df['date'] = df['date'].apply(lambda row: datetime.strptime(row, '%Y-%m-%d'))
df['month'] = df['date'].apply(lambda row: row.month)
df['year'] = df['date'].apply(lambda row: row.year)

def get_yearly_data(names, periods):
    dfSel = df[df['name'].isin(names)]
    dfSel = dfSel[dfSel['month'].isin(periods)]
    dfSel = dfSel.groupby(['year'])['tmean'].agg([np.mean, np.std])
    return dfSel

    
def yearly_figure(names, periods):
    data = get_yearly_data(names, periods)

    fig = go.Figure()

    x = list(data.index)
    y_upper = list(data['mean'] + data['std'])
    y_lower = list(data['mean'] - data['std'])

    # Error bars
    t = go.Scatter(
        x=x + x[::-1],  # x, then x reversed
        y=y_upper + y_lower[::-1],  # upper, then lower reversed
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False)
    fig.add_trace(t)

    t = go.Scatter(x=x, y=data['mean'], mode='lines', name='T-mean')
    fig.add_trace(t)

    return fig


fig = go.Figure(go.Scattergeo(lat=latlon['lat'], lon=latlon['lon'], text = latlon['name']))
fig.update_geos(resolution=50,
                showcoastlines=True,
                coastlinecolor="RebeccaPurple",
                showland=True,
                landcolor="LightGreen",
                showocean=True,
                oceancolor="LightBlue",
                showlakes=True,
                lakecolor="Blue",
                showrivers=True,
                rivercolor="Blue",
                showcountries = True,
                projection_type="mercator")
fig['layout']['geo']['center']['lat'] = 52
fig['layout']['geo']['center']['lon'] = 19
rng = 5
fig['layout']['geo']['lonaxis'] = dict(range=[-rng, rng])
fig['layout']['geo']['lataxis'] = dict(range=[-rng, rng])
fig.update_layout(
    autosize=False,
    width=400,
    height=400,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=0
    ),
    paper_bgcolor="LightSteelBlue",
)


app = dash.Dash(__name__)
server = app.server
app.layout = html.Div(
    className = 'container',
    children = [
        html.Div(
        className = 'column',
        style = {'width': '25%'},
        children = [
            html.P("Simple Dash App with Plots!"),    
            dcc.Graph(figure=fig, style={'width': '100%'}, id='scatter-plot')
        ]),
        html.Div(
        className = 'column',
        style = {'width': '75%'},
        children = [
            html.P("Plot parameters!"),
            html.P("ruugvfn wirgj iuefb huierhn viuyefh viuj ndfibjn iufh bfi dhiusffdh giusf hg"),
            html.Button('Generate Plot', id='plot-button'),
            html.Div(id='selected-points-output') 
        ]),
        html.Div(
        className = 'column',
        style = {'width': '100%', 'background-color': 'lime'},
        children = [
            html.Div(id='main-plot-area') 
        ])
    ]
)

# Callback to capture selected points
@app.callback(
    Output('selected-points-output', 'children'),
    [Input('scatter-plot', 'selectedData')]
)
def display_selected_data(selected_data):
    if selected_data is not None:
        selected_points = selected_data['points']
        miasta = [point['text'] for point in selected_points]
        return f"Selected points: {miasta}"
    else:
        return 'All cities selected'
        
        
        
@app.callback(
    Output('main-plot-area', 'children'),
    [Input('plot-button', 'n_clicks')],
    [State('scatter-plot', 'selectedData')]
)
def update_plot(n_clicks, selected_data):
    if n_clicks is None:
        return dash.no_update
    else:
        # Call the create_plot function and return the figure
        if selected_data is not None:
            selected_points = selected_data['points']
            miasta = [point['text'] for point in selected_points]
        else:
            miasta = df['name'].values
        
        fig = yearly_figure(miasta, [1, 2, 11, 12])
        return dcc.Graph(figure=fig)
        

if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host="0.0.0.0", use_reloader=False)