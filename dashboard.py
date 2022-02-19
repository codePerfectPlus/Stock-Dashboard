import pytz
import datetime
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, dash_table, Input, Output

import warnings
warnings.filterwarnings("ignore")

IST = pytz.timezone('Asia/Kolkata')
today_date = datetime.datetime.now(IST).strftime('%d-%m-%Y')

app = Dash(__name__)
app.title = 'Stock Alert Dashboard(v1.0)'


def get_filtered_data():
    df = pd.read_csv('data/stock.csv', header=None)
    df.rename(columns={0: 'Stock Name',
                       1: 'Previous Close',
                       2: 'Current Price',
                       3: 'Minimum(Day)',
                       4: 'Maximum(Day)',
                       5: 'Minimum(Year)',
                       6: 'Maximum(Year)',
                       7: 'Minimum(Threshold)',
                       8: 'Maximum(Threshold)',
                       9: 'Last Update',
                       10: 'difference',
                       11: 'watch'}, inplace=True)

    columns = ['Stock Name', 'Previous Close', 'Current Price', 'difference',
               'Minimum(Day)', 'Maximum(Day)', 'Minimum(Year)', 'Maximum(Year)', 'Minimum(Threshold)', 'Maximum(Threshold)']
    df = df.round(2)
    df['Last Update'] = pd.to_datetime(df['Last Update'])
    lastest_date = df.groupby(['Stock Name'])[
        'Last Update'].max().reset_index()['Last Update']

    filtered_df = df[df['Last Update'].isin(lastest_date)]
    filtered_df.sort_values(by=['difference'], inplace=True, ascending=False)
    filtered_df["Last Update"] = filtered_df["Last Update"].apply(
        lambda x: x.strftime('%H:%M:%S'))
    df["Last Update"] = df["Last Update"].apply(
        lambda x: x.strftime('%H:%M:%S'))
    fd1 = filtered_df[filtered_df['watch'] == True]
    fd2 = filtered_df[filtered_df['watch'] == False]
    fd1 = fd1[columns]
    fd2 = fd2[columns]
    return df, fd1, fd2


def overall_market_data():
    market_data = pd.read_csv('data/market.csv', header=None)
    columns = ['Stock Name', 'Previous Close', 'Current Price', 'difference',
               'Minimum(Day)', 'Maximum(Day)', 'Minimum(Year)', 'Maximum(Year)']
    market_data.rename(columns={0: 'Stock Name',
                                1: 'Previous Close',
                                2: 'Current Price',
                                3: 'Minimum(Day)',
                                4: 'Maximum(Day)',
                                5: 'Minimum(Year)',
                                6: 'Maximum(Year)',
                                7: 'Last Update',
                                8: 'difference'}, inplace=True)
    market_data = market_data.round(2)
    market_data['Last Update'] = pd.to_datetime(market_data['Last Update'])
    lastest_date = market_data.groupby(['Stock Name'])['Last Update'].max().reset_index()['Last Update']
    filtered_df = market_data[market_data['Last Update'].isin(lastest_date)]
    filtered_df = filtered_df[columns]

    return filtered_df, lastest_date[0]


df, fd1, fd2 = get_filtered_data()
market_data, latest_date = overall_market_data()

min_time = '09:00:00'
max_time = '16:00:00'

min_time = datetime.datetime.strptime(min_time, '%H:%M:%S')
max_time = datetime.datetime.strptime(max_time, '%H:%M:%S')

def get_dash_table(table_id, df):
    return dash_table.DataTable(
        id=table_id,
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_cell={'textAlign': 'center'},
        style_data={
            'border': '1px solid black',
        },
        style_header={
            'border': '1px solid black',
            'backgroundColor': 'white',
            'color': 'black',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'font-family': 'Courier New',
        },
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{difference} >= 0'},
                'backgroundColor': 'rgb(0, 102, 51)',
                'color': 'white',
                'fontWeight': 'bold'
            },
            {
                'if': {
                    'filter_query': '{difference} < 0'},
                'backgroundColor': 'rgb(102, 0, 0)',
                'color': 'white',
                'fontWeight': 'bold'
            }
        ],
        style_table={
            'width': '100%',
            'height': '100%',
            'overflowY': 'scroll',
            'overflowX': 'scroll',
            'textAlign': 'center',
        },
    )


app.layout = html.Div([
    dbc.Row([
        html.H1('Stock Alert Dashboard(v1.0)',
                style={'textAlign': 'center', 'color': '#0099ff', 'font-family': 'Courier New',
                       'font-size': '30px', 'font-weight': 'bold', 'margin-top': '20px'}),
        # update dbc badge
        html.H3(id='last-update-badge', style={'textAlign': 'center', 'color': '#0099ff',
                                               'font-family': 'Courier New', 'font-size': '20px', 'font-weight': 'bold'}),

        # overall market table
        html.H2('OverAll Market Status', style={
            'textAlign': 'center', 'color': '#0099ff', 'font-family': 'Courier New', 'font-size': '20px', 'font-weight': 'bold'}),
    ]),
    get_dash_table('overall-table', market_data),

    # buy table and watch table
    html.H2('Buy List',  style={'textAlign': 'center', 'color': '#0099ff',
                                'font-family': 'Courier New', 'font-size': '20px', 'font-weight': 'bold', 'margin-top': '20px'}),
    dbc.Row([
        get_dash_table('buy-table', fd1),
        dcc.Interval(
            id='interval-component',
            interval=5*1000,
            n_intervals=0
        ),
        html.H2('Watch List',  style={'textAlign': 'center', 'color': '#0099ff',
                                      'font-family': 'Courier New', 'font-size': '20px', 'font-weight': 'bold'}),
        get_dash_table('watch-table', fd2),
    ]),

    # graph by stock name select box
    html.Div([
        html.H3('Graph for Stock Data', style={'textAlign': 'center', 'color': '#0099ff', 'font-family': 'Courier New',
                                               'font-size': '30px', 'font-weight': 'bold', 'margin-top': '20px'}),
        dcc.Dropdown(
            id='stock-name-select',
            options=[{'label': i, 'value': i} for i in df['Stock Name'].unique()],
            value='Steel Authority of India Limited',
            style={'width': '100%', 'margin-top': '20px', 'color': '#0099ff',
                   'font-family': 'Courier New', 'font-size': '20px'}
        )
    ]),
    html.Div([
        dcc.Graph(id='stock-graph'),
    ]),
])

# callback for interval component


@app.callback(
    Output('buy-table', 'data'),
    Input('interval-component', 'n_intervals'))
def update_buy_table(n):
    _, fd1, _ = get_filtered_data()

    return fd1.to_dict('records')


@app.callback(
    Output('watch-table', 'data'),
    Input('interval-component', 'n_intervals'))
def update_watch_table(n):
    _, _, fd2 = get_filtered_data()

    return fd2.to_dict('records')


@app.callback(
    Output('overall-table', 'data'),
    Input('interval-component', 'n_intervals'))
def update_index_table(n):
    market_data, _ = overall_market_data()
    return market_data.to_dict('records')


@app.callback(
    Output('last-update-badge', 'children'),
    Input('interval-component', 'n_intervals'))
def update_badge(n):

    _, latest_date = overall_market_data()

    return "Dashboard last updated at {}".format(latest_date.strftime('%d-%m-%Y %H:%M:%S'))


@app.callback(
    Output('stock-graph', 'figure'),
    Input('stock-name-select', 'value'),
    Input('interval-component', 'n_intervals'))
def update_graph(stock_name, n):
    df, _, _ = get_filtered_data()
    filtered_df = df[df['Stock Name'] == stock_name]

    return {
        'data': [{
            'x': filtered_df['Last Update'],
            'y': filtered_df['Current Price'],
            'name': 'Current Price',
                    'mode': 'lines',
                    'line': {'width': 1}
        },
            {
            'x': filtered_df['Last Update'],
            'y': filtered_df['Minimum(Threshold)'],
            'name': 'Min Threshold',
                    'mode': 'lines',
                    'line': {'width': 1, 'dash': 'dash', 'color': 'red'},
        },
            {
            'x': filtered_df['Last Update'],
            'y': filtered_df['Maximum(Threshold)'],
            'name': 'Max Threshold',
                    'mode': 'lines',
                    'line': {'width': 1, 'dash': 'dash', 'color': 'green'},
        }],

        'layout': {
            'title': stock_name,
            'xaxis': {'title': 'Date',
                      'autorange': True,
                      'showgrid': True,
                      'zeroline': True,
                      'showline': True,
                      'mirror': True,
                      'ticks': '',
                      'showticklabels': True,
                      'tickangle': 90,
                      'tickfont': {'size': 10},
                      'range': [min_time, max_time]},
            'yaxis': {'title': 'Price',
                      'range': [min(filtered_df['Minimum(Threshold)']) - 10, max(filtered_df['Maximum(Threshold)']) + 10]},
            'height': 600,
            'margin': {'l': 60, 'r': 10},
            'hovermode': 'closest',
            'showlegend': True,
            'legend': {'x': 0.8, 'y': 1.1, 'orientation': 'h'},
        }
    }


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=5000)
