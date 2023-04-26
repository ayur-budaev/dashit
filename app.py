import base64
# import datetime
import io
import json
import plotly.express as px

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table

import pandas as pd
import dash_draggable

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

DROPDOWN_STYLE = {
    'width': '25%'
}

app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1("Junior-viz", style={'textAlign': 'center'}),
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Перетащите или ', html.A('выберите файл')]),
        style={
            'width': '99%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    dcc.Store(id='data-file', storage_type='local'),
    html.Div(id='output-datatable'),
    dcc.Tabs([
        dcc.Tab(label='Столбчатая диаграмма', children = [
            html.Div(id='output-axis_1'),
        ]),
        dcc.Tab(label='Линейная диаграмма', children = [
            html.Div(id='output-axis_2'),
        ]),
        dcc.Tab(label='Точечная диаграмма', children = [
            html.Div(id='output-axis_3'),
        ]),
        dcc.Tab(label='Круговая диаграмма', children = [
            html.Div(id='output-axis_4'),
        ]),
    ]),
    dash_draggable.ResponsiveGridLayout([
        html.Div(id='barchart-div'),
    ])
])

def parse_contents(contents, filename):
    df_uploaded = pd.DataFrame()

    if contents:
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df_uploaded = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df_uploaded = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print('parse_contents: ', e)

    return df_uploaded


@app.callback(Output('data-file', 'data'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'), prevent_initial_call=True)
#               State('upload-data', 'last_modified'))

def set_data(contents, filename):
    json_data = {'filename':filename}
    df = parse_contents(contents, filename)
    try:
        dataset = df.to_json(orient='split', date_format='iso')

        json_data['data'] = dataset 
        # print(dataset)
        return json.dumps(json_data)
    except Exception as e:
        print(e)
        return json.dumps(json_data)

@app.callback(Output('output-datatable', 'children'),
              Input('data-file', 'data'), prevent_initial_call=True)
def get_table(data):
    dataset = json.loads(data)
    df = pd.read_json(dataset['data'], orient='split')

    return [html.H5(dataset['filename']),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi", 
            column_selectable="single",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size=10
        ),

        # dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr()

        # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # })
    ]

@app.callback(Output('output-axis_1', 'children'),
              Input('data-file', 'data'), prevent_initial_call=True)

def draw_axis(data):
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    # print(df.columns)
    return [html.Div(
            [html.P("Выберите ось X"),
        dcc.Dropdown(id='xaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'),
        html.P("Выберите ось Y"),
        dcc.Dropdown(id='yaxis-data',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        # html.Button(id="submit-button", children="Создать график"),
        html.P("Введите название графика"),
        dcc.Input(id="barchart-name", type="text", placeholder="Название", persistence='local'),
        html.Hr()],
        style=DROPDOWN_STYLE    
        )]

@app.callback(Output('barchart-div', 'children'),
              Input('data-file','data'),
            # Input('submit-button','n_clicks'),
              Input('xaxis-data','value'),
              Input('yaxis-data', 'value'),
              Input('barchart-name','value'),
              prevent_initial_call=False)

def make_graphs(data, x_data, y_data, barchart_name):
        # print(data)
        dataset = json.loads(data)['data']
        df = pd.read_json(dataset, orient='split')
        bar_fig = px.bar(df, x=x_data, y=y_data)
        # print(data)
        bar_fig.update_layout(
            title={
                'text': barchart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        return dcc.Graph(figure=bar_fig)

# running the server
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)