import plotly.graph_objects as go  # or plotly.express as px
import dash
# import dash_core_components as dcc
# import dash_html_components as html
from matplotlib import pyplot as plt
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import re
import numpy as np


data_dir = 'd:/Katalog 1/Projekty/Weather/data/'
data_dir = ''

months = {
    1: 'sty',
    2: 'lut',
    3: 'mar',
    4: 'kwi',
    5: 'maj',
    6: 'cze',
    7: 'lip',
    8: 'sie',
    9: 'wrz',
    10: 'paź',
    11: 'lis',
    12: 'gru'
}

latlon = pd.read_csv(data_dir + 'latlon.csv')

df = pd.read_csv(data_dir + 'all.csv')
df['date'] = df['date'].apply(lambda row: datetime.strptime(row, '%Y-%m-%d'))
df['month'] = df['date'].apply(lambda row: row.month)
df['year'] = df['date'].apply(lambda row: row.year)

def yearly_figure(cities, selectedMonths, dataType, trendline=None):
    # select data and calculate mean and std
    data = df[df['name'].isin(cities)]
    data = data[data['month'].isin(selectedMonths)]
    data = data.groupby(['year'])[dataType].agg([np.mean, np.std])

    # select chart-specific title and labels based on dataType
    titlePostfix = ' (średnia ze wszystkich miesięcy)'
    if len(selectedMonths) < 12:
        titlePostfix = ' (średnia z ' + ', '.join(
            months[m] for m in selectedMonths) + ')'
    if dataType == 'tmean':
        title = 'Średnia dobowa temperatura w danym roku' + titlePostfix
        ylabel = 'Temperatura [°C]'
    if dataType == 'tmax':
        title = 'Maksymalna dobowa temperatura w danym roku' + titlePostfix
        ylabel = 'Temperatura [°C]'
    if dataType == 'tmin':
        title = 'Minimalna dobowa temperatura w danym roku' + titlePostfix
        ylabel = 'Temperatura [°C]'
    if dataType == 'tmin_grnd':
        title = 'Minimalna dobowa temperatura gruntu w danym roku' + titlePostfix
        ylabel = 'Temperatura [°C]'
    if dataType == 'prec':
        title = 'Dobowe opady w danym roku' + titlePostfix
        ylabel = 'Wyskość opadów [mm]'
    if dataType == 'snow':
        title = 'Wysokość pokrywy śnieżnej w danym roku' + titlePostfix
        ylabel = 'Wyskość pokrywy [mm]'

    fig = go.Figure()

    x = list(data.index)

    # error bars
    y_upper = list(data['mean'] + data['std'])
    y_lower = list(data['mean'] - data['std'])
    t = go.Scatter(
        x=x + x[::-1],  # x, then x reversed
        y=y_upper + y_lower[::-1],  # upper, then lower reversed
        fill='toself',
        fillcolor='rgba(79, 99, 90, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False)
    fig.add_trace(t)

    t = go.Scatter(x=x, y=data['mean'], mode='lines', name='średnia roczna')
    fig.add_trace(t)

    if trendline:
        data['roll'] = data['mean'].rolling(window=trendline).mean()
        t = go.Scatter(x=x,
                       y=data['roll'],
                       mode='lines',
                       name=f'średnia {trendline}-letnia',
                       line=dict(dash='dash', width=2,
                                 color='rgb(40, 40, 40)'))
        fig.add_trace(t)

    fig['layout']['title'] = title
    #     fig['layout']['title_x'] = 0.5
    fig['layout']['xaxis_title'] = 'Rok'
    fig['layout']['yaxis_title'] = ylabel
    fig['layout']['legend_title'] = 'Legenda'
    return fig


def monthly_figure(cities, selectedYears, dataType, trendline=None):
    # select data
    data = df[df['name'].isin(cities)]

    # select chart-specific title and labels based on dataType
    if dataType == 'tmean':
        title = 'Średnia dobowa temperatura w danym miesiącu'
        ylabel = 'Temperatura [°C]'
    if dataType == 'tmax':
        title = 'Maksymalna dobowa temperatura w danym miesiącu'
        ylabel = 'Temperatura [°C]'
    if dataType == 'tmin':
        title = 'Minimalna dobowa temperatura w danym miesiącu'
        ylabel = 'Temperatura [°C]'
    if dataType == 'tmin_grnd':
        title = 'Minimalna dobowa temperatura gruntu w danym miesiącu'
        ylabel = 'Temperatura [°C]'
    if dataType == 'prec':
        title = 'Dobowe opady w danym miesiącu'
        ylabel = 'Wyskość opadów [mm]'
    if dataType == 'snow':
        title = 'Wysokość pokrywy śnieżnej w danym miesiącu'
        ylabel = 'Wyskość pokrywy [mm]'

    fig = go.Figure()

    # create traces for each period
    for i, period in enumerate(selectedYears):
        # calculate mean and std for specific period
        dataPeriod = data[data['year'].isin(range(period[0], period[1] + 1))]
        dataPeriod = dataPeriod.groupby(['month'
                                         ])[dataType].agg([np.mean, np.std])

        color = plt.get_cmap('gist_rainbow')(i / len(selectedYears))
        # plot std
        x = list(dataPeriod.index)
        if len(selectedYears) <= 2:
            y_upper = list(dataPeriod['mean'] + dataPeriod['std'])
            y_lower = list(dataPeriod['mean'] - dataPeriod['std'])
            t = go.Scatter(
                x=x + x[::-1],  # x, then x reversed
                y=y_upper + y_lower[::-1],  # upper, then lower reversed
                fill='toself',
                fillcolor='rgba(' +
                ','.join(str(int(255 * c)) for c in color[:3]) + ',0.1)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False)
            fig.add_trace(t)

        # plot mean
        t = go.Scatter(
            x=x,
            y=dataPeriod['mean'],
            mode='lines',
            name=f'{period[0]}-{period[1]}',
            line=dict(color='rgb(' +
                      ','.join(str(int(255 * c)) for c in color[:3]) + ')'))
        fig.add_trace(t)

    fig['layout']['title'] = title
    #     fig['layout']['title_x'] = 0.5
    fig['layout']['xaxis_title'] = 'Miesiąc'
    fig['layout']['yaxis_title'] = ylabel
    fig['layout']['legend_title'] = 'Legenda'
    return fig


def daily_figure(cities, selectedPeriod, dataType, trendline=None):
    # select data
    data = df[df['name'].isin(cities)]
    data = data[(data['date'] > selectedPeriod[0])
                & (data['date'] <= selectedPeriod[1])]
    data = data.groupby(['date'])[dataType].agg([np.mean, np.std])

    # select chart-specific title and labels based on dataType
    if dataType == 'tmean':
        title = 'Średnia dobowa temperatura w danym miesiącu'
        ylabel = 'Temperatura [°C]'
    if dataType == 'tmax':
        title = 'Maksymalna dobowa temperatura w danym miesiącu'
        ylabel = 'Temperatura [°C]'
    if dataType == 'tmin':
        title = 'Minimalna dobowa temperatura w danym miesiącu'
        ylabel = 'Temperatura [°C]'
    if dataType == 'tmin_grnd':
        title = 'Minimalna dobowa temperatura gruntu w danym miesiącu'
        ylabel = 'Temperatura [°C]'
    if dataType == 'prec':
        title = 'Dobowe opady w danym miesiącu'
        ylabel = 'Wyskość opadów [mm]'
    if dataType == 'snow':
        title = 'Wysokość pokrywy śnieżnej w danym miesiącu'
        ylabel = 'Wyskość pokrywy [mm]'

    fig = go.Figure()

    # plot std
    x = list(data.index)
    y_upper = list(data['mean'] + data['std'])
    y_lower = list(data['mean'] - data['std'])
    t = go.Scatter(
        x=x + x[::-1],  # x, then x reversed
        y=y_upper + y_lower[::-1],  # upper, then lower reversed
        fill='toself',
        fillcolor='rgba(79, 99, 90, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False)
    fig.add_trace(t)

    # plot mean
    t = go.Scatter(x=x, y=data['mean'], mode='lines', name='średnia dzienna')
    fig.add_trace(t)

    if trendline:
        data['roll'] = data['mean'].rolling(window=trendline).mean()
        t = go.Scatter(x=x,
                       y=data['roll'],
                       mode='lines',
                       name=f'średnia {trendline}-dniowa',
                       line=dict(dash='dash', width=2,
                                 color='rgb(40, 40, 40)'))
        fig.add_trace(t)

    fig['layout']['title'] = title
    #     fig['layout']['title_x'] = 0.5
    fig['layout']['xaxis_title'] = 'Miesiąc'
    fig['layout']['yaxis_title'] = ylabel
    fig['layout']['legend_title'] = 'Legenda'
    return fig


def make_map_chart():
    fig = go.Figure(
        go.Scattergeo(lat=latlon['lat'],
                      lon=latlon['lon'],
                      text=latlon['name']))
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
                    showcountries=True,
                    projection_type="mercator")
    fig['layout']['geo']['center']['lat'] = 52
    fig['layout']['geo']['center']['lon'] = 19
    rng = 5
    fig['layout']['geo']['lonaxis'] = dict(range=[-rng, rng])
    fig['layout']['geo']['lataxis'] = dict(range=[-rng, rng])
    fig['layout']['dragmode'] = 'lasso'
    fig.update_layout(
        autosize=False,
        width=400,
        height=400,
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        paper_bgcolor="LightSteelBlue",
    )
    return fig


mapPlot = make_map_chart()

app = dash.Dash(__name__)
server = app.server
app.layout = html.Div(
    className='container',
    children=[
        html.Div(
            className='column',
            style={'width': '25%'},
            children=[
                html.P("Simple Dash App with Plots!"),
                dcc.Graph(figure=mapPlot, style={
                    'width': '100%'}, id='scatter-plot')
            ]),
        html.Div(
            className='column',
            style={'width': '75%'},
            children=[
                html.P("Plot parameters!"),
                html.P(
                    "ruugvfn wirgj iuefb huierhn viuyefh viuj ndfibjn iufh bfi dhiusffdh giusf hg"),

                # dropdown to select which plot setting should be displayed
                dcc.Dropdown(options=[
                    {'label': 'Roczny', 'value': 'yearly'},
                    {'label': 'Miesięczny', 'value': 'monthly'},
                    {'label': 'Dobowy', 'value': 'daily'}
                ], value='yearly', id='type-selector'),

                # divs with plot settings and switchable visibility
                html.Div(
                    id='settings-yearly',
                    style={'display': 'none'},  # initial visibility
                    children=[
                        html.P('Wykres grupowany po latach'),
                        html.P('Wybrane miesiące:'),
                        dcc.Checklist(
                            options=[{'label': val, 'value': key}
                                     for key, val in months.items()],
                            value = list(months.keys()),
                            id='selected-months',
                            style={'display': 'flex', 'flexWrap': 'wrap'},
                            inputStyle={'marginRight': '10px'},
                            labelStyle={'display': 'inline-block', 'marginRight': '10px', 'marginBottom': '10px'}
                        ),
                        html.Button('Generate Yearly Plot', id='plot-yearly-button')
                    ]
                ),
                html.Div(
                    id='settings-monthly',
                    style={'display': 'none'},  # initial visibility
                    children=[
                        html.P('Wykres grupowany po miesiącach'),
                        dcc.RadioItems(
                            id='radio-buttons',
                            options=[
                                {'label': 'Option 1', 'value': 'option1'},
                                {'label': 'Option 2', 'value': 'option2'},
                                {'label': 'Option 3', 'value': 'option3'}
                            ],
                            value='option1',  # default selected value
                        )]
                ),
                html.Div(
                    id='settings-daily',
                    style={'display': 'none'},  # initial visibility
                    children=[
                        html.P('Wykres grupowany po dniach'),
                        dcc.RadioItems(
                            id='radio-buttons',
                            options=[
                                {'label': 'Option 1', 'value': 'option1'},
                                {'label': 'Option 2', 'value': 'option2'},
                                {'label': 'Option 3', 'value': 'option3'}
                            ],
                            value='option1',  # default selected value
                        )]
                ),
                html.Div(id='selected-points-output')
            ]),
        html.Div(
            className='column',
            style={'width': '60%', 'background-color': 'lime'},
            children=[
                html.Div(id='main-plot-area')
            ])
    ]
)


@app.callback(
    [Output('settings-yearly', 'style'),
     Output('settings-monthly', 'style'),
     Output('settings-daily', 'style')],
    [Input('type-selector', 'value')]
)
def update_visibility(selectedVisibility):
    styleShow = {'display': 'block'}
    styleHide = {'display': 'none'}
    if selectedVisibility == 'daily':
        return styleHide, styleHide, styleShow
    if selectedVisibility == 'monthly':
        return styleHide, styleShow, styleHide
    if selectedVisibility == 'yearly':
        return styleShow, styleHide, styleHide

# callback to capture selected points


@app.callback(
    Output('selected-points-output', 'children'),
    [Input('scatter-plot', 'selectedData')]
)
def display_selected_data(selected_data):
    if selected_data is not None:
        selected_points = selected_data['points']
        miasta = [point['text'] for point in selected_points]
        return f"Wybrane stacje: {', '.join(m.capitalize() for m in miasta)}"
    else:
        return 'Wszystkie stacje są zaznaczone'


@app.callback(
    Output('main-plot-area', 'children'),
    [Input('plot-yearly-button', 'n_clicks')],
    [State('scatter-plot', 'selectedData'), State('selected-months', 'value')]
)
def update_yearly_plot(nClicks, selectedData, selectedMonths):
    if nClicks is None:
        return dash.no_update
    else:
        # Call the create_plot function and return the figure
        if selectedData is not None:
            selectedPoints = selectedData['points']
            miasta = [point['text'] for point in selectedPoints]
        else:
            miasta = df['name'].values

        fig = yearly_figure(miasta, selectedMonths, 'tmean', trendline=5)
        return dcc.Graph(figure=fig)


if __name__ == '__main__':
    app.run_server(debug=True, port=8050, host="0.0.0.0", use_reloader=True)
