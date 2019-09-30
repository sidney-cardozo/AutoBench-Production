# -*- coding: utf-8 -*-
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sys
import time
import psycopg2

def postgres_test():
    try:
        connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")
        connection.close()
        return True
    except:
        return False

time.sleep(120)

print("Testing Database Connection")
test_connect = postgres_test()

while test_connect == False:
    test_connect = postgres_test()

print("Connected!")

connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")

select_metricsdata_sql = "SELECT * FROM model_metrics;"
# check that the model1 predictions table exists
metrics_data_exists = False
while metrics_data_exists == False:
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(select_metricsdata_sql)
        metrics_data_exists = True
    except:
        print("Error:", sys.exc_info()[0])
        metrics_data_exists = False
# with connection, connection.cursor() as cursor:
    time.sleep(10)
metrics = pd.read_sql_query(select_metricsdata_sql, connection, index_col = "model")

connection.close()

# accuracy_scores = {'textblob':0.0, 'random':0.8, 'vader':0.9}
# precision_scores = {'textblob':0.3, 'random':0.5, 'vader':0.2}
# recall_scores = {'textblob':0.8, 'random':0.5, 'vader':0.4}
# f1_scores = {'textblob':0.7, 'random':0.5, 'vader':0.6}
# run_time = {'textblob':10, 'random':3, 'vader':200}
# metrics = pd.DataFrame({"accuracy":pd.Series(accuracy_scores), "precision":pd.Series(precision_scores), "recall":pd.Series(recall_scores), "f1":pd.Series(f1_scores), "time":pd.Series(run_time)})

metrics_by_model = metrics.rename_axis('model').reset_index()
metrics_by_measure = metrics.T.rename_axis('measure').reset_index()

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Model Performance Metrics'),

    html.Div(children='''
        Visualizations go here!
    '''),

    dcc.Graph(
        id='by-model-graph',
        figure={
            'data': [
                {'x': list(metrics_by_model.model), 'y': list(metrics_by_model.accuracy), 'type': 'bar', 'name': 'Accuracy'},
                {'x': list(metrics_by_model.model), 'y': list(metrics_by_model.precision), 'type': 'bar', 'name': 'Precision'},
                {'x': list(metrics_by_model.model), 'y': list(metrics_by_model.recall), 'type': 'bar', 'name': 'Recall'},
                {'x': list(metrics_by_model.model), 'y': list(metrics_by_model.f1), 'type': 'bar', 'name': 'F1 Score'}
            ],
            'layout': {
                'title': 'Metrics by Model'
            }
        }
    ),

    dcc.Graph(
        id='by-measure-graph',
        figure={
            'data': [
                {'x': list(metrics_by_measure.measure[:-1]), 'y': list(metrics_by_measure.textblob[:-1]), 'type': 'bar', 'name': 'TextBlob'},
                {'x': list(metrics_by_measure.measure[:-1]), 'y': list(metrics_by_measure.random[:-1]), 'type': 'bar', 'name': 'Random'},
                {'x': list(metrics_by_measure.measure[:-1]), 'y': list(metrics_by_measure.vader[:-1]), 'type': 'bar', 'name': 'Vader'},
            ],
            'layout': {
                'title': 'Model Performance by Metric'
            }
        }
    ),

    dcc.Graph(
        id='time-graph',
        figure={
            'data': [
                {'x': list(metrics_by_model.model), 'y': list(metrics_by_model.time), 'type': 'bar', 'name': 'Time'},
            ],
            'layout': {
                'title': 'Model Run Time'
            }
        }
    ),

    html.H4(children='Test Metrics'),
    generate_table(metrics_by_model)

])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
