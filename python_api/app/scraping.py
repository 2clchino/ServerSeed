import csv
import requests
import bs4
import re
import os
import time
import numpy as np
import pandas as pd
from enum import Enum
import derby_func as func
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import learn_func as learn
import seaborn as sns
import collections
from sklearn import preprocessing
from sklearn import tree
from sklearn import svm
from sklearn import ensemble
from sklearn import neighbors
from sklearn import linear_model
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn import metrics

RACE = "/race/"
HORSE = "/horse/"
PRED = "/pred/"
CSV_DIR = "data"
URL_BASE = "https://db.netkeiba.com"
URL_RACE = "https://race.netkeiba.com/race/shutuba.html?race_id="
URL_PRED = "https://race.netkeiba.com/special/index.html?id="
RACE_TABLE_NAME = "race_table_01 nk_tb_common"

def get_trains(pred_id):
    TRAIN_RACE_ID = func.get_train_race_id(func.get_text_from_page('https://race.netkeiba.com/special/index.html?id=' + pred_id))
    return TRAIN_RACE_ID

def correct_train_data(race_id):
    url = URL_BASE + RACE + race_id
    text = func.get_text_from_page(url)
    print(race_id)
    race_name = func.get_name_from_text(text).replace('競馬データベース - netkeiba.com', '').split('｜')
    (info, horse_id, horse_names) = func.get_old_race_info_from_text(False, text, RACE_TABLE_NAME, race_id, race_name[0])
    file_path = CSV_DIR+ RACE + race_id + ".csv"
    with open(file_path, "w", newline="", encoding='shift_jis') as f:
        writer = csv.writer(f)
        writer.writerows(info)

def get_pred(pred_id):
    TEST_RACE_ID = func.get_pred_race_id(func.get_text_from_page(URL_PRED + pred_id))
    url = URL_RACE + TEST_RACE_ID
    text = func.get_text_from_page(url)
    race_name = func.get_name_from_text(text).replace(' - netkeiba.com', '').split('(')
    if not os.path.exists(CSV_DIR + "/pred"):
        os.makedirs(CSV_DIR + "/pred")
    (info, horse_id, horse_names) = func.get_race_info_from_text(text, "Shutuba_Table RaceTable01 ShutubaTable", TEST_RACE_ID[0:4], race_name[0])
    file_path = CSV_DIR+ PRED + TEST_RACE_ID + ".csv"
    with open(file_path, "w", newline="", encoding='shift_jis') as f:
        writer = csv.writer(f)
        writer.writerows(info)
    return TEST_RACE_ID

cnx = None
load_dotenv()
cnx = mysql.connector.connect(
    host=os.environ.get('DB_HOST') or '127.0.0.1',
    port=os.environ.get('DB_PORT') or '3306',
    user=os.environ.get('DB_USERNAME') or 'user',
    password=os.environ.get('DB_PASSWORD') or 'secret',
    database=os.environ.get('DB_DATABASE') or 'derby',
)
        
def scraping(pred_id):
    cursor = cnx.cursor()
    sql = "select exists(select * from preds where race_id=%s);"
    param = (pred_id,)
    cursor.execute(sql, param)
    if not cursor.fetchone()[0]:
        prace_id = get_pred(pred_id)
        sql = ('''
        INSERT INTO preds 
            (race_id, file_path)
        VALUES 
            (%s, %s)
        ''')
        data = [[pred_id, prace_id]]
        cursor.executemany(sql, data)
        cnx.commit()
    sql = ('''
    SELECT  file_path
    FROM    trains
    WHERE   pred_id = %s
    ''')
    param = (pred_id,)
    cursor.execute(sql, param)
    db_trains = []
    for cur in cursor:
        db_trains.append(cur[0])
    data = []
    trains = get_trains(pred_id)
    for train in trains:
        if train not in db_trains:
            data.append([pred_id, train])
    if (len(data) > 0):
        for race_id in trains:
            correct_train_data(race_id)
            time.sleep(3)
        sql = ('''
        INSERT INTO trains 
            (pred_id, file_path)
        VALUES 
            (%s, %s)
        ''')
        cursor.executemany(sql, data)
        cnx.commit()
    cursor.close()

def stratified_cv(X, y, clf_class, shuffle=True, n_folds=10, **kwargs):
    stratified_k_fold = StratifiedKFold(n_splits = n_folds, shuffle = shuffle).split(X, y)
    y_pred = y.copy()
    for ii, jj in stratified_k_fold:
        X_train, X_test = X[ii], X[jj]
        y_train = y[ii]
        clf = clf_class(**kwargs)
        clf.fit(X_train, y_train)
        y_pred[jj] = clf.predict(X_test)
    return y_pred

def prediction(pred_id):
    cursor = cnx.cursor()
    sql = (''' SELECT file_path FROM trains WHERE pred_id = %s ''')
    param = (pred_id,)
    cursor.execute(sql, param)
    TRAIN_RACE_ID = []
    RACE_DATA_COLUMNS = func.race_data_columns()
    HORSE_DATA_COLUMNS = func.horse_data_columns()
    RACE_RANK = func.race_rank()    
    for cur in cursor:
        TRAIN_RACE_ID.append(cur[0])
    df_races = []
    db_horses = {}
    for i in range(len(TRAIN_RACE_ID)):
        df_races.append(pd.read_csv(CSV_DIR + RACE + str(TRAIN_RACE_ID[i]) + ".csv", header=None, names = RACE_DATA_COLUMNS, encoding='shift_jis'))
    drop_columns = ['trainer', 'owner', 'jockey', 'reward', 'difference', 'lap_time', 'final_3F', 'time', 'time_score']
    for i in range(len(df_races)):
        df_races[i].fillna({'time_score': '**'})
        df_races[i].dropna(how='all', axis = 1, inplace=True)
        df_races[i] = learn.rank_to_int(df_races[i])
        df_races[i] = df_races[i].drop(columns = drop_columns, errors = 'ignore')
        df_races[i]['horse_data_key'] = df_races[i].apply(learn.load_horse_data, num = i, columns = HORSE_DATA_COLUMNS, db_horses = db_horses, race_id = TRAIN_RACE_ID, race_score = RACE_RANK, axis = 1)
        df_races[i]['race_count'] = df_races[i].apply(learn.serch_past_races, num = i, db_horses = db_horses, race_id = TRAIN_RACE_ID, axis = 1)
        df_races[i] = learn.feature_creation(df = df_races[i], db_horses = db_horses)
    df_races_train = []
    df_races_test = []
    df_races_all = pd.concat(df_races)
    for i in range(len(df_races)):
        tmp = []
        for j in range(len(df_races)):
            if (i == j):
                df_races_test.append(df_races[j])
            else:
                tmp.append(df_races[j])
        df_races_train.append(pd.concat(tmp))
    df_races_train_2 = df_races_train.copy()
    df_races_test_2 = df_races_test.copy()
    df_races_all_2 = df_races_all.copy()
    y_trains = []
    (df_races_all_2, y_all) = func.create_param(df_races_all_2)
    for i in range(len(df_races_train_2)):
        (df_races_train_2[i], df_races_test_2[i], tmp) = func.create_params(df_races_train_2[i], df_races_test_2[i])
        y_trains.append(tmp)
    TEST_NUM = 15
    y_train = y_trains[TEST_NUM]
    X_train = df_races_train_2[TEST_NUM].values.astype(float)
    X_test = df_races_test_2[TEST_NUM].values.astype(float)
    mm = preprocessing.MinMaxScaler()
    X_train = mm.fit_transform(X_train)
    X_test = mm.fit_transform(X_test)
    print('Passive Aggressive Classifier: {:.3f}'.format(metrics.accuracy_score(y_train, stratified_cv(X_train, y_train, linear_model.PassiveAggressiveClassifier))))
    print('Gradient Boosting Classifier:  {:.3f}'.format(metrics.accuracy_score(y_train, stratified_cv(X_train, y_train, ensemble.GradientBoostingClassifier))))
    print('Support vector machine(SVM):   {:.3f}'.format(metrics.accuracy_score(y_train, stratified_cv(X_train, y_train, svm.SVC))))
    print('Random Forest Classifier:      {:.3f}'.format(metrics.accuracy_score(y_train, stratified_cv(X_train, y_train, ensemble.RandomForestClassifier))))
    print('K Nearest Neighbor Classifier: {:.3f}'.format(metrics.accuracy_score(y_train, stratified_cv(X_train, y_train, neighbors.KNeighborsClassifier))))
    print('Dump Classifier: {:.3f}'.format(metrics.accuracy_score(y_train, [0 for ii in y_train.tolist()])))
    model = ensemble.RandomForestClassifier()
    model.fit(X_train, y_train)
    func.print_importance(func.calc_importance(model, X_train), df_races_test_2[0].columns.values)
    y_pred = model.predict(X_test)
    print(y_pred)
    for i in range(len(y_pred)):
        if (y_pred[i]):
            print(df_races[TEST_NUM].iloc[[i]]['horse_name'])
    sql = (''' SELECT file_path FROM preds WHERE race_id = %s ''')
    param = (pred_id,)
    cursor.execute(sql, param)
    PRED_RACE_ID=""
    for cur in cursor:
        PRED_RACE_ID = cur[0]
    df_pred_race = pd.read_csv(CSV_DIR+ PRED + str(PRED_RACE_ID) + ".csv", header=None, names = func.pred_race_columns(), encoding='shift_jis')
    drop_columns = ['trainer', 'owner', 'jockey', 'mark', 'url', 'blank_2', 'blank_3', 'blank_4', 'blank_5']
    df_pred_race.fillna({'time_score': '**'})
    df_pred_race.dropna(how='all', axis = 1, inplace=True)
    df_pred_race.dropna(how='all', axis = 0, inplace=True)
    df_pred_race = df_pred_race.reset_index()
    df_pred_race = df_pred_race.drop(columns = drop_columns, errors = 'ignore')
    df_pred_race['horse_data_key'] = df_pred_race.apply(learn.load_horse_data, num = 0, columns = HORSE_DATA_COLUMNS, db_horses = db_horses, race_id = TRAIN_RACE_ID, race_score = RACE_RANK, axis = 1)
    df_pred_race['race_count'] = df_pred_race.apply(lambda x: int(db_horses[x['horse_data_key']].shape[0]), axis = 1)
    df_pred_race = learn.feature_creation(df = df_pred_race, db_horses = db_horses, num = -1)
    horse_names = df_pred_race['horse_name']
    df_pred_race = df_pred_race.drop(columns = ["horse_name", "age", "horse_data_key", "horse_number", 'horse_weight', 'horse_id'], errors = 'ignore')
    x_pred = df_pred_race.values.astype(float)
    X_all = df_races_all_2.values.astype(float)
    X_all = mm.fit_transform(X_all)
    x_pred = mm.fit_transform(x_pred)
    models = []
    models.append(linear_model.PassiveAggressiveClassifier())
    models.append(ensemble.GradientBoostingClassifier())
    models.append(svm.SVC())
    models.append(ensemble.RandomForestClassifier())
    models.append(neighbors.KNeighborsClassifier())
    names = []
    preds = np.zeros(len(horse_names), dtype=np.int64)
    for _ in range(100):
        for i in range(len(models)):
            models[i].fit(X_all, y_all)
            y_pred = models[i].predict(x_pred)
            preds = preds + y_pred
            for j in range(len(y_pred)):
                if (y_pred[j]):
                    names.append(horse_names[j])
    print(preds.tolist())
    print(collections.Counter(names))
    return collections.Counter(names)

if __name__ == '__main__':
    scraping("0081")
    prediction("0081")
    cnx.close()