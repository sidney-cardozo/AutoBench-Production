import pandas as pd
import psycopg2
import time

def review_exists(review_id):
    with connection, connection.cursor() as cursor:
        select_id_sql = "SELECT id FROM joined_results WHERE id = %s"
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

def get_gold_label(gold_rating):
    if gold_rating <= 5:
        gold_label = "Neg"
        gold_pos = 0
    elif gold_rating >= 6:
        gold_label = "Pos"
        gold_pos = 1
    return (gold_label, gold_pos)

def get_textblob_label(textblob_rating):
    if textblob_rating <= 0:
        textblob_pred = "Neg"
        pred_pos = 0
    elif textblob_rating > 0:
        textblob_pred = "Pos"
        pred_pos = 1
    return (textblob_pred, pred_pos)

def get_flair_label(flair_rating):
    if "NEG" in flair_rating:
        flair_pred = "Neg"
        pred_pos = 0
    elif "POS" in flair_rating:
        flair_pred = "Pos"
        pred_pos = 1
    return (flair_pred, pred_pos)

def get_random_label(random_rating):
    if random_rating <= 0:
        random_pred = "Neg"
        pred_pos = 0
    elif random_rating > 0:
        random_pred = "Pos"
        pred_pos = 1
    return (random_pred, pred_pos)

def get_vader_label(vader_rating):
    if vader_rating <= 0:
        vader_pred = "Neg"
        pred_pos = 0
    elif vader_rating > 0:
        vader_pred = "Pos"
        pred_pos = 1
    return (vader_pred, pred_pos)

def calc_accuracy(n_true_pos, n_true_neg, pop_counter):
    accuracy = (n_true_pos + n_true_neg) / pop_counter
    return accuracy

def calc_precision(n_true_pos, n_pred_pos):
    precision = (n_true_pos / n_pred_pos)
    return precision

def calc_recall(n_true_pos, n_gold_pos):
    recall = n_true_pos / n_gold_pos
    return recall

def calc_f1_score(precision, recall):
    f1 = 2 * ((precision * recall) / (precision + recall))
    return f1

time.sleep(60)

print("Testing Database Connection")
test_connect = postgres_test()

while test_connect == False:
    test_connect = postgres_test()

print("Connected!")

connection = psycopg2.connect(user = "root", dbname = "model-test", password = "password")

# define sql commands
delete_table_sql = "DROP TABLE IF EXISTS joined_results CASCADE;"
# create_table_sql = "CREATE TABLE joined_results (id TEXT PRIMARY KEY, true_label TEXT, textblob_pred TEXT, flair_pred TEXT, vader_pred TEXT);"
# insert_sql = "INSERT INTO joined_results (id, true_label, textblob_pred, flair_pred, vader_pred) VALUES (%s, %s, %s, %s, %s);"
create_table_sql = "CREATE TABLE joined_results (id TEXT PRIMARY KEY, true_label TEXT, textblob_pred TEXT, random_pred TEXT, vader_pred TEXT);"
insert_sql = "INSERT INTO joined_results (id, true_label, textblob_pred, random_pred, vader_pred) VALUES (%s, %s, %s, %s, %s);"

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

select_model1data_sql = "SELECT * FROM test_textblob;"
# check that the model1 predictions table exists
model1_data_exists = False
while model1_data_exists == False:
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(select_model1data_sql)
        model1_data_exists = True
    except:
        model1_data_exists = False
print("Textblob table exists!")

# select_model2data_sql = "SELECT * FROM test_flair;"
# # check that the model1 predictions table exists
# model2_data_exists = False
# while model2_data_exists == False:
#     time.sleep(3)
#     try:
#         with connection, connection.cursor() as cursor:
#             cursor.execute(select_model2data_sql)
#         model2_data_exists = True
#     except:
#         model2_data_exists = False
# print("Flair table exists!")
select_model2data_sql = "SELECT * FROM test_random;"
# check that the model2 predictions table exists
model2_data_exists = False
while model2_data_exists == False:
    time.sleep(3)
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(select_model2data_sql)
        model2_data_exists = True
    except:
        model2_data_exists = False
print("Random table exists!")

select_model3data_sql = "SELECT * FROM test_vader;"
# check that the model1 predictions table exists
model3_data_exists = False
while model3_data_exists == False:
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute(select_model3data_sql)
        model3_data_exists = True
    except:
        model3_data_exists = False
print("Vader table exists!")

# metrics variables
# true_pos = {'textblob':0, 'flair':0, 'vader':0}
# true_neg = {'textblob':0, 'flair':0, 'vader':0}
# pred_pos = {'textblob':0, 'flair':0, 'vader':0}
run_time = {'textblob':0, 'random':0, 'vader':0}
true_pos = {'textblob':0, 'random':0, 'vader':0}
true_neg = {'textblob':0, 'random':0, 'vader':0}
pred_pos = {'textblob':0, 'random':0, 'vader':0}
gold_pos = 0
pop_counter = 0
# join together testdata and test_textblob tables
# join_sql = "SELECT testdata.id, testdata.gold, test_textblob.pred_sent AS textblob_pred, test_flair.pred_sent AS flair_pred, test_vader.pred_sent AS vader_pred FROM testdata JOIN test_textblob ON testdata.id = test_textblob.id JOIN test_flair ON testdata.id = test_flair.id JOIN test_vader ON testdata.id = test_vader.id;"
join_sql = "SELECT testdata.id, testdata.gold, test_textblob.pred_sent AS textblob_pred, test_textblob.time AS textblob_time, test_random.pred_sent AS random_pred, test_random.time AS random_time, test_vader.pred_sent AS vader_pred, test_vader.time AS vader_time FROM testdata JOIN test_textblob ON testdata.id = test_textblob.id JOIN test_random ON testdata.id = test_random.id JOIN test_vader ON testdata.id = test_vader.id;"
with connection, connection.cursor() as cursor:
    cursor.execute(join_sql)
    joined_rows = cursor.fetchall()
# row have form (id, gold, textblob_pred, textblob_time, random_pred, random_time, vader_pred, vader_time)
prev_rowcount = -1
while len(joined_rows) > prev_rowcount:
    if len(joined_rows) > 0:
        with connection, connection.cursor() as cursor:
            cursor.execute(join_sql)
            sample_row = cursor.fetchone()
        print("prev", prev_rowcount, "new", len(joined_rows))
        prev_rowcount = len(joined_rows)
        for row in joined_rows:
            review_id = row[0]
            if review_exists(review_id) == False:
                pop_counter += 1
                gold_rating = row[1]
                textblob_rating = row[2]
                textblob_time = row[3]
                random_rating = row[4]
                random_time = row[5]
                vader_rating = row[6]
                vader_time = row[7]
                gold_label = get_gold_label(gold_rating)
                gold_pos += gold_label[1]
                textblob_pred = get_textblob_label(textblob_rating)
                pred_pos['textblob'] += textblob_pred[1]
                run_time['textblob'] += textblob_time
                # flair_pred = get_flair_label(flair_rating)
                # pred_pos['flair'] += flair_pred[1]
                random_pred = get_random_label(random_rating)
                pred_pos['random'] += random_pred[1]
                run_time['random'] += random_time
                vader_pred = get_vader_label(vader_rating)
                pred_pos['vader'] += vader_pred[1]
                run_time['vader'] += vader_time
                preds = {'textblob':textblob_pred[0], 'random':random_pred[0], 'vader':vader_pred[0]}
                with connection, connection.cursor() as cursor:
                    cursor.execute(insert_sql, (review_id, gold_label[0], preds['textblob'], preds['random'], preds['vader']))
                for model in preds.keys():
                    if gold_label[0] == preds[model]:
                        if gold_label[0] == "Pos":
                            true_pos[model] += 1
                        elif gold_label[0] == "Neg":
                            true_neg[model] += 1
    time.sleep(30)
    with connection, connection.cursor() as cursor:
        cursor.execute(join_sql)
        joined_rows = cursor.fetchall()

# accuracy_scores = {'textblob':0, 'flair':0, 'vader':0}
# precision_scores = {'textblob':0, 'flair':0, 'vader':0}
# recall_scores = {'textblob':0, 'flair':0, 'vader':0}
# f1_scores = {'textblob':0, 'flair':0, 'vader':0}
accuracy_scores = {'textblob':0, 'random':0, 'vader':0}
precision_scores = {'textblob':0, 'random':0, 'vader':0}
recall_scores = {'textblob':0, 'random':0, 'vader':0}
f1_scores = {'textblob':0, 'random':0, 'vader':0}

for model in accuracy_scores.keys():
    accuracy_scores[model] = calc_accuracy(true_pos[model], true_neg[model], pop_counter)
    precision_scores[model] = calc_precision(true_pos[model], pred_pos[model])
    recall_scores[model] = calc_recall(true_pos[model], gold_pos)
    f1_scores[model] = calc_f1_score(precision_scores[model], recall_scores[model])

metrics = pd.DataFrame({"Accuracy":pd.Series(accuracy_scores), "Precision":pd.Series(precision_scores), "Recall":pd.Series(recall_scores), "F1":pd.Series(f1_scores), "Time":pd.Series(run_time)})
print("pop counter", pop_counter)
print(metrics)

delete_metrics_table_sql = "DROP TABLE IF EXISTS model_metrics CASCADE;"
create_metrics_table_sql = "CREATE TABLE model_metrics (model TEXT PRIMARY KEY, accuracy float8, precision float8, recall float8, f1 float8, time float8)"
insert_metrics_sql = "INSERT INTO model_metrics (model, accuracy, precision, recall, f1, time) VALUES (%s, %s, %s, %s, %s, %s);"

with connection, connection.cursor() as cursor:
    cursor.execute(delete_metrics_table_sql)
    cursor.execute(create_metrics_table_sql)

for model in accuracy_scores.keys():
    with connection, connection.cursor() as cursor:
        cursor.execute(insert_metrics_sql, (model, accuracy_scores[model], precision_scores[model], recall_scores[model], f1_scores[model], run_time[model]))

connection.close()
