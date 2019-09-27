import psycopg2
from textblob import TextBlob
import pandas as pd
import time

def review_exists(review_id):
    with connection, connection.cursor() as cursor:
        select_id_sql = "SELECT id FROM test_textblob WHERE id = %s"
        cursor.execute(select_id_sql, (review_id,))
        row = cursor.fetchone()
    return row is not None

def postgres_test():
    try:
        connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")
        connection.close()
        return True
    except:
        return False

time.sleep(5)

print("Testing Database Connection")
test_connect = postgres_test()

while test_connect == False:
    test_connect = postgres_test()

print("Connected!")

connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")

# define sql commands
delete_table_sql = "DROP TABLE IF EXISTS test_textblob CASCADE;"
create_table_sql = "CREATE TABLE test_textblob (id TEXT PRIMARY KEY, pred_sent float8, time float8);"
insert_sql = "INSERT INTO test_textblob (id, pred_sent, time) VALUES (%s, %s, %s);"

# if a test_textblob table already exists, delete it then create a new empty one
with connection, connection.cursor() as cursor:
    cursor.execute(delete_table_sql)
    cursor.execute(create_table_sql)
# connection.commit()
# cursor.close()

# fetch id and text from testdata table in tuple (id, text)
select_testdata_sql = "SELECT id, text FROM testdata;"
# check that the test data table exists
test_data_exists = False
while test_data_exists == False:
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(select_testdata_sql)
        test_data_exists = True
    except:
        test_data_exists = False

print('TESTING MODEL')

prev_rowcount = -1
with connection, connection.cursor() as cursor:
    cursor.execute(select_testdata_sql)
    rows = cursor.fetchall()
# row have form (id, text)
# iterate over rows and get textblob sentiment predictions
while len(rows) > prev_rowcount:
    if len(rows) > 0:
        print("prev", prev_rowcount, "new", len(rows))
        prev_rowcount = len(rows)
        for row in rows:
            review_id = row[0]
            review_text = row[1]
            if review_exists(review_id) == False:
                start_time = time.time()
                predict_sentiment = TextBlob(review_text).sentiment.polarity
                # write results to test_textblob table
                with connection, connection.cursor() as cursor:
                    run_time = time.time() - start_time
                    cursor.execute(insert_sql, (review_id, predict_sentiment, run_time))
                    # connection.commit()
    with connection, connection.cursor() as cursor:
        cursor.execute(select_testdata_sql)
        rows = cursor.fetchall()

with connection, connection.cursor() as cursor:
    cursor.execute("SELECT id from test_textblob;")
    model_test_rows = cursor.fetchall()
print("DONE! num rows test_textblob", len(model_test_rows))

connection.close()

# calculate accuracy to numerical rating and to polarity
## accuracy to numerical rating needs to be calculated in a smarter way
# print('RUNNING METRICS')
# textblob_data['rating_diff'] = textblob_data.apply(lambda row: abs(row['scaled']-row['pred_sent']), axis=1)
# avg_rating_difference = textblob_data.rating_diff.mean()
# print("Average accuracy to numerical rating:", avg_rating_difference/2)
# textblob_data['agreement'] = textblob_data.apply(lambda row: (row['scaled']>0 and row['pred_sent']>0) or (row['scaled']<0 and row['pred_sent']<0), axis=1)
# agree_rate = sum(textblob_data['agreement'])/len(textblob_data['agreement'])
# print("Accuracy to positive/negative polarity:", agree_rate)
# print(textblob_data.head())
