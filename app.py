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
        dcc.Tab(label='Изображение', children = [
            dcc.Upload(
            id='upload-image',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
            ),
        ]),
        dcc.Tab(label='Текст', children = [
                dcc.Textarea(
                id='textarea-example',
                value='Что-то написано',
                style={'width': '50%', 'height': 300, 'resize': 'none'},
                persistence='local',
                ),
        ]),
    ]),
    ]),
 ]),
    dash_draggable.ResponsiveGridLayout([
        html.Div(id='barchart-div'),
        html.Div(id='linechart-div'),
        html.Div(id='dotchart-div'),
        html.Div(id='piechart-div'),
        # html.Div(id='output-image-upload')
        html.Div(id='textarea-example-output', style={'whiteSpace': 'pre-line'})
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

######################################## processing the barchart ########################################
@app.callback(Output('output-axis_1', 'children'),
              Input('data-file', 'data'),
              prevent_initial_call=True)

def draw_axis(data):
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    # print(df.columns)
    return [html.Div(
            [html.P("Выберите ось X"),
        dcc.Dropdown(id='xaxis-data_1',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'),
        html.P("Выберите ось Y"),
        dcc.Dropdown(id='yaxis-data_1',
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
              Input('xaxis-data_1','value'),
              Input('yaxis-data_1', 'value'),
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

######################################## processing the linechart ########################################
@app.callback(Output('output-axis_2', 'children'),
              Input('data-file', 'data'),
              prevent_initial_call=True)

def draw_axis(data):
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    # print(df.columns)
    return [html.Div(
            [html.P("Выберите ось X"),
        dcc.Dropdown(id='xaxis-data_2',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'),
        html.P("Выберите ось Y"),
        dcc.Dropdown(id='yaxis-data_2',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        # html.Button(id="submit-button", children="Создать график"),
        html.P("Введите название графика"),
        dcc.Input(id="linechart-name", type="text", placeholder="Название", persistence='local'),
        html.Hr()],
        style=DROPDOWN_STYLE    
        )]

@app.callback(Output('linechart-div', 'children'),
              Input('data-file','data'),
            # Input('submit-button','n_clicks'),
              Input('xaxis-data_2','value'),
              Input('yaxis-data_2', 'value'),
              Input('linechart-name','value'),
              prevent_initial_call=False)

def make_graphs(data, x_data, y_data, linechart_name):
        # print(data)
        dataset = json.loads(data)['data']
        df = pd.read_json(dataset, orient='split')
        line_fig = px.line(df, x=x_data, y=y_data)
        # print(data)
        line_fig.update_layout(
            title={
                'text': linechart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        return dcc.Graph(figure=line_fig)

######################################## processing the dotchart ########################################
@app.callback(Output('output-axis_3', 'children'),
              Input('data-file', 'data'),
              prevent_initial_call=True)

def draw_axis(data):
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    # print(df.columns)
    return [html.Div(
            [html.P("Выберите ось X"),
        dcc.Dropdown(id='xaxis-data_3',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'),
        html.P("Выберите ось Y"),
        dcc.Dropdown(id='yaxis-data_3',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        # html.Button(id="submit-button", children="Создать график"),
        html.P("Выберите размер"),
        dcc.Dropdown(id='size-data_3',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        html.P("Выберите цвет"),
        dcc.Dropdown(id='color-data_3',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        html.P("Введите название графика"),
        dcc.Input(id="dotchart-name", type="text", placeholder="Название", persistence='local'),
        html.Hr()],
        style=DROPDOWN_STYLE    
        )]

@app.callback(Output('dotchart-div', 'children'),
              Input('data-file','data'),
            # Input('submit-button','n_clicks'),
              Input('xaxis-data_3','value'),
              Input('yaxis-data_3', 'value'),
              Input('size-data_3', 'value'),
              Input('color-data_3', 'value'),
              Input('dotchart-name','value'),
              prevent_initial_call=False)

def make_graphs(data, x_data, y_data, size_data, color_data, dotchart_name):
        # print(data)
        dataset = json.loads(data)['data']
        df = pd.read_json(dataset, orient='split')
        dot_fig = px.scatter(df, x=x_data, y=y_data, size=size_data, color=color_data)
        # print(data)
        dot_fig.update_layout(
            title={
                'text': dotchart_name,
                'y':0.94,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            }
        )
        return dcc.Graph(figure=dot_fig)

######################################## processing the piechart ########################################
@app.callback(Output('output-axis_4', 'children'),
              Input('data-file', 'data'),
              prevent_initial_call=True)

def draw_axis(data):
    dataset = json.loads(data)['data']
    df = pd.read_json(dataset, orient='split')
    # print(df.columns)
    return [html.Div(
            [html.P("Выберите секторы"),
        dcc.Dropdown(id='xaxis-data_4',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'),
        html.P("Выберите метки"),
        dcc.Dropdown(id='yaxis-data_4',
                     options=[{'label':x, 'value':x} for x in df.columns], persistence='local'), 
        # html.Button(id="submit-button", children="Создать график"),
        html.P("Введите название графика"),
        dcc.Input(id="piechart-name", type="text", placeholder="Название", persistence='local'),
        html.Hr()],
        style=DROPDOWN_STYLE    
        )]

@app.callback(Output('piechart-div', 'children'),
              Input('data-file','data'),
            # Input('submit-button','n_clicks'),
              Input('xaxis-data_4','value'),
              Input('yaxis-data_4', 'value'),
              Input('piechart-name','value'),
              prevent_initial_call=False)

def make_graphs(data, x_data, y_data, piechart_name):
        # print(data)
        dataset = json.loads(data)['data']
        df = pd.read_json(dataset, orient='split')
        bar_fig = px.pie(df, values=x_data, names=y_data)
        # print(data)
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
            #  automargin = True

        )

        return dcc.Graph(figure=bar_fig)

######################################## processing the image ########################################
# def img_parse_contents(contents, filename, date):
#     return html.Div([
#         html.H5(filename),
#         # HTML images accept base64 encoded strings in the same format
#         # that is supplied by the upload
#         html.Img(src=contents),
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
    Input('textarea-example', 'value')
)
def update_output(value):
    return dcc.Textarea(format(value),
                        value=value,
                        style={'width': '100%', 'height': 500, 'resize': 'none', 'overflow': 'hidden', },)

# running the server
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=True)