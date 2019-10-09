import psycopg2
import re
import os, sys

### BEGIN FUNCTIONS ###

def ping_postgres_db(db_name):
    '''Tests whether the given PostgreSQL database is live.'''
    try:
        connection = psycopg2.connect(user = "root", dbname = db_name, password = "password")
        connection.close()
        return True
    except:
        return False

def clean_text(text):
    '''Replaces html tags, dashes, and slashes with a space.'''
    to_replace = re.compile("(<br\s*/>)|(\-)|(\/)")
    text = to_replace.sub(" ", text)
    return text

def review_exists(review_id, table_name):
    '''Tests whether a given review already exists in the given table.'''
    with connection, connection.cursor() as cursor:
        select_id_sql = "SELECT review_id FROM " + table_name + " WHERE review_id = %s;"
        cursor.execute(select_id_sql, (review_id,))
        row = cursor.fetchone()
    return row is not None

def get_list_of_reviews(path_to_reviews):
    '''Create list of all IMDB review text files. Text files in this test set
    are named using a numeric label and the star rating for the review. Each name
    appended to the list all_reviews has the form (pos/|neg/)LABEL_RATING.txt.'''
    pos_reviews = ['pos/'+f for f in os.listdir(path_to_reviews+'pos/')]
    neg_reviews = ['neg/'+f for f in os.listdir(path_to_reviews+'neg/')]
    all_reviews = pos_reviews + neg_reviews
    return all_reviews

def get_review_text(path_to_reviews, filename):
    with open(path_to_reviews+r) as f:
        review_text = f.read()
    f.close()
    return review_text

### END FUNCTIONS ###

if __name__ == "__main__":

    print("Waiting for connection to model-test database")
    connected_to_db = False
    while not connected_to_db:
        connected_to_db = ping_postgres_db("model-test")
    print("Connected to model-test database")

    connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")

    # if testdata table already exists, delete it then create a new empty one
    with connection, connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS testdata CASCADE;")
        cursor.execute("CREATE TABLE testdata (review_id TEXT PRIMARY KEY, review_text TEXT, true_label TEXT);")

    all_reviews = get_list_of_reviews("aclImdb/test/")

    insert_row_sql = "INSERT INTO testdata (review_id, review_text, true_label) VALUES (%s, %s, %s);"

    print("Building testdata table")
    for r in all_reviews:
        if not review_exists(r, "testdata"):
            # split path to file, returns [pos|neg, id_label, rating, txt]
            split_review_path = re.split("[\W\_]", r)
            true_label = split_review_path[0]
            review_text = get_review_text("aclImdb/test/", r)
            review_text = clean_text(review_text)
            with connection, connection.cursor() as cursor:
                cursor.execute(insert_row_sql, (r, review_text, true_label))

    print("Completed testdata table")
    connection.close()
