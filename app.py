import base64
# import datetime
import io
import json
import plotly.express as px
import dash
import numpy as np
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import dash_daq as daq
import pandas as pd
import dash_draggable
import dash_bootstrap_components as dbc
from dash_holoniq_wordcloud import DashWordcloud

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

TABS_STYLE = {
    #  'height': 600
}

DROPDOWN_STYLE = {
    # 'width': '25%'
}

app = dash.Dash(__name__, 
                # external_stylesheets=external_stylesheets,
                external_stylesheets=[dbc.themes.LUX],
                suppress_callback_exceptions=True)

app.layout = html.Div([
         
            html.H1("Junior-viz", style={'textAlign': 'center', 'margin-top': 7}),

            dcc.Tabs([
                dcc.Tab(label='Данные', children = [
                    
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

                    ]),
            dcc.Tab(label='Визуализация', children = [

            dcc.Tabs([
                dcc.Tab(label='Столбчатая диаграмма', children = [
                    dbc.Container([
                         
                        dbc.Row([ 
                            dbc.Col([
                                 
                                 html.Div(id='output-axis_1', style=TABS_STYLE)

                            ], width={'size':4}),
                            
                            dbc.Col([
                                html.Div(id='barchart-div-dupl'),
                            ], width={'size':6, 'offset':2})
                        ]), 

                    ], fluid=True)

                ]),
                dcc.Tab(label='Линейная диаграмма', children = [
                    dbc.Container([
                         
                        dbc.Row([ 
                            dbc.Col([
                                 
                                 html.Div(id='output-axis_2', style=TABS_STYLE),

                            ], width={'size':4}),
                            
                            dbc.Col([
                                html.Div(id='linechart-div-dupl'),
                            ], width={'size':6, 'offset':2})
                        ]), 

                    ], fluid=True)

                    # html.Div(id='output-axis_2', style=TABS_STYLE),
                    # html.Div(id='linechart-div-dupl'),
                ]),
                dcc.Tab(label='Точечная диаграмма', children = [
                    dbc.Container([
                         
                        dbc.Row([ 
                            dbc.Col([
                                 
                                 html.Div(id='output-axis_3', style=TABS_STYLE),

                            ], width={'size':4}),
                            
                            dbc.Col([
                                html.Div(id='dotchart-div-dupl'),
                            ], width={'size':6, 'offset':2})
                        ]), 

                    ], fluid=True)
                ]),
                dcc.Tab(label='Круговая диаграмма', children = [
                    dbc.Container([
                         
                        dbc.Row([ 
                            dbc.Col([
                                 
                                 html.Div(id='output-axis_4', style=TABS_STYLE),

                            ], width={'size':4}),
                            
                            dbc.Col([
                                html.Div(id='piechart-div-dupl'),
                            ], width={'size':6, 'offset':2})
                        ]), 

                    ], fluid=True)
                ]),
                dcc.Tab(label='Облако слов', children = [
                    dbc.Container([
                         
                        dbc.Row([ 
                            dbc.Col([
                                 
                                 html.Div(id='output-worcloud', style=TABS_STYLE),

                            ], width={'size':4}),
                            
                            dbc.Col([
                                html.Div(id='wordcloud-div-dupl'),
                            ], width={'size':6, 'offset':2})
                        ]), 

                    ], fluid=True)
                ]),

                # dcc.Tab(label='Изображение', children = [
                #     html.Div(dcc.Upload(
                #     id='upload-image',
                #     children=html.Div([
                #         'Drag and Drop or ',
                #         html.A('Select Files')
                #     ]),
                #     style={
                #         'width': '100%',
                #         'height': '60px',
                #         'lineHeight': '60px',
                #         'borderWidth': '1px',
                #         'borderStyle': 'dashed',
                #         'borderRadius': '5px',
                #         'textAlign': 'center',
                #         'margin': '10px'
                #     },
                #     # Allow multiple files to be uploaded
                #     multiple=True
                #     ), style=TABS_STYLE),
                # ]),
                
                dcc.Tab(label='Текст', children = [
                    dbc.Container([
                         
                        dbc.Row([ 
                            dbc.Col([
                                html.P("Размер текста"),
                                dcc.Slider(min=6, max=24, step=1, value=14, id='text-size-slider', marks=None,
                                    tooltip={"placement": "bottom", "always_visible": True}, persistence='local')
                            ], width={'size':4}),
                            
                            dbc.Col([
                                dcc.Textarea(
                                    id='textarea-example',
                                    value='Что-то написано',
                                    style={'width': '50%', 'height': 400, 'resize': 'none'},
                                    persistence='local',
                                ),
                            ], width={'size':6, 'offset':2})
                        ]), 

                    ], fluid=True)
                ]),
 

            ]),
            ]),
        ]),
            dash_draggable.ResponsiveGridLayout([
                html.Div(id='barchart-div'),
                html.Div(id='linechart-div'),
                html.Div(id='dotchart-div'),
                html.Div(id='piechart-div'),
                html.Div(id='wordcloud-div'),
                # html.Div(id='output-image-upload'),
                html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line'}),
            
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
                # Ase that the user uploaded an excel file
                df_uploaded = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print('parse_contents: ', e)

    return df_uploaded

@app.callback(Output('data-file', 'data'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'), prevent_initial_call=True)

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
            id = 'df-table',
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

        html.Hr()
    ]


######################################## processing the barchart ########################################

@app.callback(Output('output-axis_1', 'children'),
              Input('data-file', 'data'),
              prevent_initial_call=True)
def draw_axis(data):
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    return [html.Div(
            [html.P("Выберите ось X"),
        dcc.Dropdown(id='xaxis-data_1',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'),
        html.P("Выберите ось Y"),
        dcc.Dropdown(id='yaxis-data_1',
                     options=[{'label':x, 'value':x} for x in df.columns], multi=True, persistence='local'), 
        html.P("Агрегация"),
        dcc.Dropdown(id='agg-data_1',
                     options={
                         'sum': 'Сумма',
                         'avg': 'Среднее',
                         'count': 'Количество',
                         'min': 'Минимум',
                         'max': 'Максимум',
                         }, persistence='local'), 
        html.P("Введите название графика"),
        dcc.Input(id="barchart-name", type="text", placeholder="Название", persistence='local'),
        # html.Hr()
        ],
        style=DROPDOWN_STYLE    
        )]

### dictionary for an aggregation ###
d = {'sum': 'sum()', 'avg':'mean()', 'count': 'count()', 'min':'min()', 'max':'max()'}
    
@app.callback([
              Output('barchart-div-dupl', 'children'),
              Output('barchart-div', 'children')],
              [Input('data-file','data'),
              Input('xaxis-data_1','value'),
              Input('yaxis-data_1', 'value'),
              Input('agg-data_1', 'value'),
              Input('barchart-name','value')],
              prevent_initial_call=False)

def make_graphs(data, x_data, y_data, agg_data, barchart_name):
        dataset = json.loads(data)['data']
        df = pd.read_json(dataset, orient='split')
        nnn = df.groupby(x_data)[y_data]
        r = {'nnn':nnn}
        exec('nnn = nnn.'+d[agg_data], r)
        bar_fig = px.bar(r['nnn'], x=r['nnn'].index, y=y_data)
        bar_fig.update_layout(
            title={
                'text': barchart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        return dcc.Graph(figure=bar_fig), dcc.Graph(figure=bar_fig)

######################################## processing the linechart ########################################
@app.callback(Output('output-axis_2', 'children'),
              Input('data-file', 'data'),
              prevent_initial_call=True)

def draw_axis(data):
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    return [html.Div(
            [html.P("Выберите ось X"),
        dcc.Dropdown(id='xaxis-data_2',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'),
        html.P("Выберите ось Y"),
        dcc.Dropdown(id='yaxis-data_2',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        html.P("Введите название графика"),
        dcc.Input(id="linechart-name", type="text", placeholder="Название", persistence='local'),
        # html.Hr()
        ],
        style=DROPDOWN_STYLE    
        )]

@app.callback([Output('linechart-div-dupl', 'children'),
               Output('linechart-div', 'children')],
              [Input('data-file','data'),
              Input('xaxis-data_2','value'),
              Input('yaxis-data_2', 'value'),
              Input('linechart-name','value')],
              prevent_initial_call=False)

def make_graphs(data, x_data, y_data, linechart_name):
        dataset = json.loads(data)['data']
        df = pd.read_json(dataset, orient='split')
        line_fig = px.line(df, x=x_data, y=y_data)
        line_fig.update_layout(
            title={
                'text': linechart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        return dcc.Graph(figure=line_fig), dcc.Graph(figure=line_fig)

######################################## processing the dotchart ########################################
@app.callback(Output('output-axis_3', 'children'),
              Input('data-file', 'data'),
              prevent_initial_call=True)

def draw_axis(data):
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    return [html.Div(
            [html.P("Выберите ось X"),
        dcc.Dropdown(id='xaxis-data_3',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'),
        html.P("Выберите ось Y"),
        dcc.Dropdown(id='yaxis-data_3',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        html.P("Выберите размер"),
        dcc.Dropdown(id='size-data_3',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        html.P("Выберите цвет"),
        dcc.Dropdown(id='color-data_3',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        html.P("Введите название графика"),
        dcc.Input(id="dotchart-name", type="text", placeholder="Название", persistence='local'),
        # html.Hr()
        ],
        style=DROPDOWN_STYLE    
        )]

@app.callback([Output('dotchart-div-dupl', 'children'),
               Output('dotchart-div', 'children')],
              [Input('data-file','data'),
              Input('xaxis-data_3','value'),
              Input('yaxis-data_3', 'value'),
              Input('size-data_3', 'value'),
              Input('color-data_3', 'value'),
              Input('dotchart-name','value')],
              prevent_initial_call=False)

def make_graphs(data, x_data, y_data, size_data, color_data, dotchart_name):
        dataset = json.loads(data)['data']
        df = pd.read_json(dataset, orient='split')
        for i in [x_data, y_data, size_data, color_data]:
            if not pd.isna(i):
                df = df.loc[~df[i].isna()]
        dot_fig = px.scatter(df, x=x_data, y=y_data, size=size_data, color=color_data)
        dot_fig.update_layout(
            title={
                'text': dotchart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        return dcc.Graph(figure=dot_fig), dcc.Graph(figure=dot_fig)

######################################## processing the piechart ########################################
@app.callback(Output('output-axis_4', 'children'),
              Input('data-file', 'data'),
              prevent_initial_call=True)

def draw_axis(data):
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    return [html.Div(
            [html.P("Выберите секторы"),
        dcc.Dropdown(id='xaxis-data_4',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'),
        html.P("Выберите метки"),
        dcc.Dropdown(id='yaxis-data_4',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        html.P("Введите название графика"),
        dcc.Input(id="piechart-name", type="text", placeholder="Название", persistence='local'),
        ],
        style=DROPDOWN_STYLE    
        )]

@app.callback([Output('piechart-div-dupl', 'children'),
               Output('piechart-div', 'children')],
              [Input('data-file','data'),
              Input('xaxis-data_4','value'),
              Input('yaxis-data_4', 'value'),
              Input('piechart-name','value')],
              prevent_initial_call=False)

def make_graphs(data, x_data, y_data, piechart_name):
        dataset = json.loads(data)['data']
        df = pd.read_json(dataset, orient='split')
        
        df_temp = df.groupby(y_data).count()
        
        if df_temp.shape[0] > 9:
             df_temp = df_temp.sort_values(x_data, ascending = False).reset_index()
             df_temp.loc[7:, y_data] = 'Другое'
             df_temp = df_temp.groupby(y_data).sum()

        # bar_fig = px.pie(df, values=x_data, names=y_data)
        bar_fig = px.pie(df_temp, values=x_data, names=df_temp.index)
        bar_fig.update_layout(
            title={
                'text': piechart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )

        bar_fig.update_traces(
             textposition="inside", 
             textinfo='percent+label'

        )

        return dcc.Graph(figure=bar_fig), dcc.Graph(figure=bar_fig)

######################################## processing the image ########################################

# def img_parse_contents(contents, filename, date):
#     return html.Div([
#         html.H5(filename),
#         html.Img(src=contents),
#         # html.Div(html.Img(src=contents), style = {'width': 222, 'height': 400,'background-image': 'url("html.Img(src=contents)")'})
#         # HTML images accept base64 encoded strings in the same format
#         # that is supplied by the upload
#         # html.Div(style = {'width': 222, 'height': 400,'background-image': contents}),
#         # html.Div(style = {'width': 222, 'height': 400,'background-image': 'url("data:image/png;base64, base64.b64encode(image).decode(\'utf-8\')")'})
        
#     ])


# @app.callback(Output('output-image-upload', 'children'),
#               Input('upload-image', 'contents'),
#               State('upload-image', 'filename'),
#               State('upload-image', 'last_modified'))
# def update_output(list_of_contents, list_of_names, list_of_dates):
#     if list_of_contents is not None:
#         children = [
#             img_parse_contents(c, n, d) for c, n, d in
#             zip(list_of_contents, list_of_names, list_of_dates)]
#         return children

######################################## processing the text ########################################
@app.callback(
    Output('textarea-example-output', 'children'),
    Input('textarea-example', 'value'),
    Input('text-size-slider', 'value')
    
)
def update_output(text, size):
    return html.P(format(text), 
                  style = {
                    'font-size': size
                    })

######################################## processing the wordcloud ########################################

@app.callback(Output('output-worcloud', 'children'),
              Input('data-file', 'data'),
              prevent_initial_call=True)
def set_worcloud(data):    
    
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    return [html.Div(
                    [html.P("Выберите данные"),
                    dcc.Dropdown(id='worcloud_column',
                        options=df.columns[np.array([df[i].dtype == 'object' for i in df.columns])].tolist(),
                        persistence='local'),
                    html.P("Ширина"),
                    dcc.Slider(min=200, max=1000, step=50, value=500, id='width-slider', marks=None,
                                tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
                    html.P("Высота"),
                    dcc.Slider(min=200, max=1000, step=50, value=500, id='height-slider', marks=None,
                                tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
                    html.P("Сетка"),
                    dcc.Slider(min=5, max=100, step=5, value=30, id='grid-slider', marks=None,
                                tooltip={"placement": "bottom", "always_visible": True}, persistence='local'),
                    html.P("Выберите цвет"),
                    daq.ColorPicker(
                        id='words-color',
                        value=dict(hex='#000000'),
                        size=200,
                        persistence='local'
                    )],
                    style=DROPDOWN_STYLE
                    )
            ]

@app.callback([Output('wordcloud-div-dupl', 'children'),
               Output('wordcloud-div', 'children')],
              [Input('data-file', 'data'),
              Input('worcloud_column', 'value'),
              Input('width-slider', 'value'),
              Input('height-slider', 'value'),
              Input('grid-slider', 'value'),
              Input('words-color', 'value')],
              prevent_initial_call=True)

def draw_wordcloud(data, column, sliderWidth, sliderHeight, sliderGrid, wordsColor):
    security_data = [
    ["Equity", 74, "Zillions of equity based funds"],
    ["Bond", 45],
    ["Global", 30],
    ["Sector Equity", 17],
    ["EUR", 15],
    ["Large Cap", 13],
    ["Europe", 11],
    ]

    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')

    try:
        security_data = []
        df_temp = df[column].value_counts()
        for k, v in df_temp.items():
            security_data.append([k, v])            
    except:
        pass        
    
    jopa = DashWordcloud(
            id='wordcloud',
            list=security_data,
            width=sliderWidth, height=sliderHeight,
            gridSize=sliderGrid,
            weightFactor = 3,
            color=wordsColor['hex'],
            backgroundColor='#fff',
            shuffle=False,
            rotateRatio=0.5,
            shrinkToFit=True,
            shape='square',
            hover=True
            )

    return jopa, jopa

# running the server
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)