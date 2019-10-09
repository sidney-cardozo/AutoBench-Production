import pandas as pd
import psycopg2
import time

### BEGIN FUNCTIONS ###

def review_exists(review_id, table_name):
    '''Tests whether a given review already exists in the given table.'''
    with connection, connection.cursor() as cursor:
        select_id_sql = "SELECT review_id FROM " + table_name + " WHERE review_id = %s;"
        cursor.execute(select_id_sql, (review_id,))
        row = cursor.fetchone()
    return row is not None

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

model_results_tables = ["random", "textblob", "vader"]

if __name__ == "__main__":
    time.sleep(60)

    print("Waiting for connection to model-test database")
    connected_to_db = False
    while not connected_to_db:
        connected_to_db = ping_postgres_db("model-test")
    print("Connected to model-test database")

    connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")

    # if compiled_results table already exists, delete it and create a new one
    with connection, connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS compiled_results CASCADE;")
        cursor.execute("CREATE TABLE compiled_results (review_id TEXT PRIMARY KEY, true_label TEXT, textblob_pred TEXT, random_pred TEXT, vader_pred TEXT);")

    for table in model_results_tables:
        does_table_exist = False
        while not does_table_exist:
            does_table_exist = table_exists(table)
        print("Table " + table + " exists")

    insert_row_sql = "INSERT INTO compiled_results (review_id, true_label, textblob_pred, random_pred, vader_pred) VALUES (%s, %s, %s, %s, %s);"
    select_testdata_sql = "SELECT * FROM testdata;"
    # metrics variables
    metric_variables = {'run_time':dict.fromkeys(model_results_tables, 0),
                        'true_pos':dict.fromkeys(model_results_tables, 0),
                        'true_neg':dict.fromkeys(model_results_tables, 0),
                        'pred_pos':dict.fromkeys(model_results_tables, 0)}
    class_pos = 0
    total_items = 0
    # join together testdata and model test results tables
    join_sql = "SELECT testdata.review_id, testdata.true_label, textblob.pred_label AS textblob_pred, textblob.time AS textblob_time, random.pred_label AS random_pred, random.time AS random_time, vader.pred_label AS vader_pred, vader.time AS vader_time FROM testdata JOIN textblob ON testdata.review_id = textblob.review_id JOIN random ON testdata.review_id = random.review_id JOIN vader ON testdata.review_id = vader.review_id;"
    col_names = ["review_id", "true_label", "textblob_pred", "textblob_time", "random_pred", "random_time", "vader_pred", "vader_time"]
    with connection, connection.cursor() as cursor:
        cursor.execute(join_sql)
        joined_rows = cursor.fetchall()
    with connection, connection.cursor() as cursor:
        cursor.execute(select_testdata_sql)
        num_test_rows = cursor.rowcount
    prev_rowcount = -1
    while len(joined_rows) <= num_test_rows:
        if len(joined_rows) > 0 and len(joined_rows) > prev_rowcount:
            print("prev", prev_rowcount, "new", len(joined_rows), "test", num_test_rows)
            prev_rowcount = len(joined_rows)
            for row_values in joined_rows:
                row = dict(zip(col_names, row_values))
                if not review_exists(row['review_id'], 'compiled_results'):
                    total_items += 1
                    class_pos += (row['true_label']=='pos')
                    for model in model_results_tables:
                        metric_variables['pred_pos'][model] += (row[model+'_pred']=='pos')
                        metric_variables['run_time'][model] += row[model+'_time']
                    with connection, connection.cursor() as cursor:
                        cursor.execute(insert_row_sql, (row['review_id'], row['true_label'], row['textblob_pred'], row['random_pred'], row['vader_pred']))
                    for model in model_results_tables:
                        if row['true_label'] == row[model+'_pred']:
                            if row['true_label'] == "pos":
                                metric_variables['true_pos'][model] += 1
                            else:
                                metric_variables['true_neg'][model] += 1
            with connection, connection.cursor() as cursor:
                cursor.execute(join_sql)
                joined_rows = cursor.fetchall()
            with connection, connection.cursor() as cursor:
                cursor.execute(select_testdata_sql)
                num_test_rows = cursor.rowcount
        elif prev_rowcount == num_test_rows:
            break

    metrics = {'accuracy':dict.fromkeys(model_results_tables, 0),
                'precision':dict.fromkeys(model_results_tables, 0),
                'recall':dict.fromkeys(model_results_tables, 0),
                'f1_score':dict.fromkeys(model_results_tables, 0)}

    for model in model_results_tables:
        metrics['accuracy'][model] = (metric_variables['true_pos'][model] + metric_variables['true_neg'][model]) / total_items
        metrics['precision'][model] = metric_variables['true_pos'][model] / metric_variables['pred_pos'][model]
        metrics['recall'][model] = metric_variables['true_pos'][model] / class_pos
        metrics['f1_score'][model] = 2 * ((metrics['precision'][model] * metrics['recall'][model]) / (metrics['precision'][model] + metrics['recall'][model]))

    metrics_df = pd.DataFrame({"Accuracy":pd.Series(metrics['accuracy']), "Precision":pd.Series(metrics['precision']), "Recall":pd.Series(metrics['recall']), "F1":pd.Series(metrics['f1_score']), "Time":pd.Series(metric_variables['run_time'])})
    print("Total Items", total_items)
    print(metrics_df)

    with connection, connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS model_metrics CASCADE;")
        cursor.execute("CREATE TABLE model_metrics (model TEXT PRIMARY KEY, accuracy float8, precision float8, recall float8, f1 float8, time float8);")

    insert_metrics_sql = "INSERT INTO model_metrics (model, accuracy, precision, recall, f1, time) VALUES (%s, %s, %s, %s, %s, %s);"

    for model in model_results_tables:
        with connection, connection.cursor() as cursor:
            cursor.execute(insert_metrics_sql, (model, metrics['accuracy'][model], metrics['precision'][model], metrics['recall'][model], metrics['f1_score'][model], metric_variables['run_time'][model]))

    metrics_table = pd.read_sql_query("SELECT * FROM model_metrics;", connection, index_col = "model")
    print(metrics_table)
    
    connection.close()
