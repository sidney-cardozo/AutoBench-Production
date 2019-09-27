import psycopg2
import time
import random

def review_exists(review_id):
    with connection, connection.cursor() as cursor:
        select_id_sql = "SELECT id FROM test_random WHERE id = %s"
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

time.sleep(10)

print("Testing Database Connection")
test_connect = postgres_test()

while test_connect == False:
    test_connect = postgres_test()

print("Connected!")

connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")

# define sql commands
delete_table_sql = "DROP TABLE IF EXISTS test_random CASCADE;"
create_table_sql = "CREATE TABLE test_random (id TEXT PRIMARY KEY, pred_sent float8, time float8);"
insert_sql = "INSERT INTO test_random (id, pred_sent, time) VALUES (%s, %s, %s);"

with connection, connection.cursor() as cursor:
    cursor.execute(delete_table_sql)
    cursor.execute(create_table_sql)
    # connection.commit()

select_testdata_sql = "SELECT * FROM testdata;"
# check that the test data table exists
test_data_exists = False
while test_data_exists == False:
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(select_testdata_sql)
        test_data_exists = True
    except:
        test_data_exists = False
print("Test table exists!")

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
                prediction = random.uniform(-1,1)
                # write results to test_random table
                with connection, connection.cursor() as cursor:
                    run_time = time.time() - start_time
                    cursor.execute(insert_sql, (review_id, prediction, run_time))
    with connection, connection.cursor() as cursor:
        cursor.execute(select_testdata_sql)
        rows = cursor.fetchall()

with connection, connection.cursor() as cursor:
    cursor.execute("SELECT id from test_random;")
    model_test_rows = cursor.fetchall()
print("num rows test_random", len(model_test_rows))

print("DONE!")

connection.close()
