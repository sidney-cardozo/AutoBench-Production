import psycopg2
from textblob import TextBlob
import pandas as pd
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

def map_rating_to_label(rating):
    if rating <= 0:
        pred_label = "neg"
    else:
        pred_label = "pos"
    return pred_label

### END FUNCTIONS ###

if __name__ == "__main__":
    print("Waiting for connection to model-test database")
    connected_to_db = False
    while not connected_to_db:
        connected_to_db = ping_postgres_db("model-test")
    print("Connected to model-test database")

    connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")

    # if a test_textblob table already exists, delete it then create a new empty one
    with connection, connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS textblob CASCADE;")
        cursor.execute("CREATE TABLE textblob (review_id TEXT PRIMARY KEY, pred_label TEXT, time float8);")

    # check that the test data table exists
    test_data_exists = False
    while not test_data_exists:
        test_data_exists = table_exists('testdata')

    print('Beginning textblob model testing')

    select_testdata_sql = "SELECT review_id, review_text FROM testdata;"
    test_data_col_names = ["review_id", "review_text"]
    insert_row_sql = "INSERT INTO textblob (review_id, pred_label, time) VALUES (%s, %s, %s);"

    prev_rowcount = -1
    with connection, connection.cursor() as cursor:
        cursor.execute(select_testdata_sql)
        rows = cursor.fetchall()
    # rows have form (review_id, review_text)
    # iterate over rows and get textblob sentiment predictions
    while len(rows) > prev_rowcount:
        if len(rows) > 0:
            print("prev", prev_rowcount, "new", len(rows))
            prev_rowcount = len(rows)
            for row_values in rows:
                row = dict(zip(test_data_col_names, row_values))
                if not review_exists(row['review_id'], "textblob"):
                    start_time = time.time()
                    prediction = TextBlob(row['review_text']).sentiment.polarity
                    pred_label = map_rating_to_label(prediction)
                    with connection, connection.cursor() as cursor:
                        run_time = time.time() - start_time
                        cursor.execute(insert_row_sql, (row['review_id'], pred_label, run_time))
        with connection, connection.cursor() as cursor:
            cursor.execute(select_testdata_sql)
            rows = cursor.fetchall()

    print("Textblob model testing complete")

    connection.close()
