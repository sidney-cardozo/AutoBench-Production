import psycopg2
import re
import os, sys
import time

def review_exists(review_id):
    with connection, connection.cursor() as cursor:
        select_id_sql = "SELECT id FROM testdata WHERE id = %s"
        cursor.execute(select_id_sql, (review_id,))
        row = cursor.fetchone()
    return row is not None

def add_review(filename):
    return None

def postgres_test():
    try:
        connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")
        connection.close()
        return True
    except:
        return False

replace_with_space = re.compile("(<br\s*/>)|(\-)|(\/)")

time.sleep(3)

print("Testing Database Connection")
test_connect = postgres_test()

while test_connect == False:
    # print("Trying to connect", counter)
    test_connect = postgres_test()

print("Connected!")

# map to rescaled ratings {raw: scaled}
rating_rescale = {1:-1, 2:(-7/9), 3:(-5/9), 4:(-3/9), 5:(-1/9), 6:(1/9), 7:(3/9), 8:(5/9), 9:(7/9), 10:1}

connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")

print("READY!")

delete_table_sql = "DROP TABLE IF EXISTS testdata CASCADE;"
create_table_sql = "CREATE TABLE testdata (id TEXT PRIMARY KEY, text TEXT, gold float8, scaled float8, source TEXT);"
insert_sql = "INSERT INTO testdata (id, text, gold, scaled, source) VALUES (%s, %s, %s, %s, %s);"

# if a testdata table already exists, delete it then create a new empty one
with connection, connection.cursor() as cursor:
    cursor.execute(delete_table_sql)
    cursor.execute(create_table_sql)

path_to_reviews = "aclImdb/test/"
pos_reviews = ['pos/'+f for f in os.listdir(path_to_reviews+'pos/')]
neg_reviews = ['neg/'+f for f in os.listdir(path_to_reviews+'neg/')]
all_reviews = pos_reviews + neg_reviews
# review1 = "0_2.txt"

print("BUILDING DB!")
for r in all_reviews:
    # split path to file, yield [PATH*, id_label, rating, txt]
    split_review = re.split("[\W\_]", r)
    review_rating = float(split_review[-2])
    rescaled_rating = rating_rescale[review_rating]
    if review_exists(r) == False:
        # read in review text
        with open(path_to_reviews+r) as f:
            review_text = f.read()
        f.close()
        review_text = replace_with_space.sub(" ", review_text)
        # add row to testdata table
        with connection, connection.cursor() as cursor:
            cursor.execute(insert_sql, (r, review_text, review_rating, rescaled_rating, 'IMDB'))

with connection, connection.cursor() as cursor:
    cursor.execute("SELECT * FROM testdata")
    print("DONE!", cursor.rowcount)

connection.close()
