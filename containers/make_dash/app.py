# -*- coding: utf-8 -*-
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sys
import random
import time
import datetime
import psycopg2

### BEGIN FUNCTIONS ###

def ping_postgres_db(db_name):
    '''Tests whether the given PostgreSQL database is live.'''
    try:
        connection = psycopg2.connect(user = "root", dbname = db_name, password = "password")
        connection.close()
        return True
    except:
        return False

def table_exists(table_name):
    sql_query = "SELECT EXISTS (SELECT 1 FROM "+ table_name + ");"
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(sql_query)
        return True
    except:
        return False

### END FUNCTIONS ###

time.sleep(120)

print("Waiting for connection to model-test database")
connected_to_db = False
while not connected_to_db:
    connected_to_db = ping_postgres_db("model-test")
print("Connected to model-test database")

connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")

# check that the model1 predictions table exists
metrics_data_exists = False
while not metrics_data_exists:
    metrics_data_exists = table_exists("model_metrics")

time.sleep(5)

metrics = pd.read_sql_query("SELECT * FROM model_metrics;", connection, index_col = "model")

select_samples_sql = "SELECT compiled_results.review_id, compiled_results.true_label, compiled_results.textblob_pred, compiled_results.vader_pred, testdata.review_text FROM compiled_results JOIN testdata ON testdata.review_id = compiled_results.review_id WHERE compiled_results.true_label != compiled_results.textblob_pred OR compiled_results.true_label != compiled_results.vader_pred;"
sample_data = pd.read_sql_query(select_samples_sql, connection, index_col = "review_id")

connection.close()

metrics_by_model = metrics.rename_axis('model').reset_index()
metrics_by_measure = metrics.T.rename_axis('measure').reset_index()

print(metrics_by_model)
print(metrics_by_measure)

data_header = ["True Label", "TextBlob Prediction", "Vader Prediction", "Review Text"]

def generate_table(dataframe, header=None, max_rows=10):
    if header != None:
        header = [html.Tr([html.Th(name) for name in header])]
    else:
        header = [html.Tr([html.Th(col) for col in dataframe.columns])]
    num_samples = min(len(dataframe), max_rows)
    sample_rows = random.sample(range(len(dataframe)), num_samples)
    num_samples = min(len(dataframe), max_rows)
    sample_rows = random.sample(range(len(dataframe)), num_samples)
    body = []
    for i in sample_rows:
        body_contents = []
        for col in dataframe.columns:
            if col == "review_text":
                body_contents.append(html.Details([html.Summary('Review Text'), html.Div(dataframe.iloc[i][col])]))
            else:
                body_contents.append(html.Td(dataframe.iloc[i][col]))
        body.append(html.Tr(body_contents))
    return html.Table(header + body)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='AutoBench: Model Performance Metrics'),

    html.Div(children='Coral Hughto, Insight DE Fellow 2019'),

    html.Div(children=['Last updated: ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' PDT']),

    html.Div([
        dcc.Graph(
            id='by-measure-graph',
            figure={
                'data': [
                    {'x': list(metrics_by_measure.measure[1:-1]), 'y': list(metrics_by_measure.textblob[1:-1]), 'type': 'bar', 'name': 'TextBlob'},
                    {'x': list(metrics_by_measure.measure[1:-1]), 'y': list(metrics_by_measure.random[1:-1]), 'type': 'bar', 'name': 'Random'},
                    {'x': list(metrics_by_measure.measure[1:-1]), 'y': list(metrics_by_measure.vader[1:-1]), 'type': 'bar', 'name': 'Vader'},
                ],
            'layout': {'title': 'Model Performance by Metric'}
            }
        ),
        dcc.Graph(
            id='time-graph',
            figure={
                'data': [
                    {'x': list(metrics_by_model.model), 'y': list(metrics_by_model.time), 'type': 'bar', 'name': 'Time'},
                ],
                'layout': {'title': 'Model Run Time'}
            }
        )
    ], style={'columnCount':2}),

    html.H4(children='Sample texts with incorrect predictions'),
    generate_table(sample_data, data_header, 5)

])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
