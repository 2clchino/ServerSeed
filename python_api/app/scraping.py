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

TEST_RACE_ID = "202201010411"
HORSE_ID = "/horse/2018105233"
RACE = "/race/"
CSV_DIR = "csv"
URL_BASE = "https://db.netkeiba.com"
URL_RACE = "https://race.netkeiba.com/race/shutuba.html?race_id="
RACE_TABLE_NAME = "race_table_01 nk_tb_common"

def get_trains(pred_id):
    TRAIN_RACE_ID = func.get_train_race_id(func.get_text_from_page('https://race.netkeiba.com/special/index.html?id=' + pred_id))
    return TRAIN_RACE_ID

def correct_train_data(race_id):
    url = URL_BASE + RACE + race_id
    text = func.get_text_from_page(url)
    print(race_id)
    race_name = func.get_name_from_text(text).replace('競馬データベース - netkeiba.com', '').split('｜')
    if not os.path.exists(CSV_DIR + "/horse/" + race_id[0:4] + race_name[0]):
        os.makedirs(CSV_DIR + "/horse/" + race_id[0:4] + race_name[0])
    if not os.path.exists(CSV_DIR + RACE + race_name[0]):
        os.makedirs(CSV_DIR + RACE + race_name[0])
    (info, horse_id, horse_names) = func.get_old_race_info_from_text(False, text, RACE_TABLE_NAME, race_id, race_name[0])
    file_path = CSV_DIR+ RACE + race_name[0] + "/" + race_id[0:4] + ".csv"
    with open(file_path, "w", newline="", encoding='shift_jis') as f:
        writer = csv.writer(f)
        writer.writerows(info)

if __name__ == '__main__':
    cnx = None

    try:
        load_dotenv()
        cnx = mysql.connector.connect(
            host=os.environ.get('DB_HOST') or '127.0.0.1',
            port=os.environ.get('DB_PORT') or '3306',
            user=os.environ.get('DB_USERNAME') or 'user',
            password=os.environ.get('DB_PASSWORD') or 'secret',
            database=os.environ.get('DB_DATABASE') or 'derby',
        )

        if cnx.is_connected:
            cursor = cnx.cursor()
            pred_id = "0080"
            sql = ('''
            INSERT INTO preds 
                (race_id)
            VALUES 
                (%s)
            ''')
            data = [[pred_id]]
            cursor.executemany(sql, data)
            cnx.commit()

            sql = ('''
            INSERT INTO trains 
                (pred_id, file_path)
            VALUES 
                (%s, %s)
            ''')
            data = []
            trains = get_trains(pred_id)
            for train in trains:
                data.append([pred_id, train])
            cursor.executemany(sql, data)
            cnx.commit()
            for race_id in trains:
                correct_train_data(race_id)
                time.sleep(3)
            cursor.close()

    except mysql.connector.Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("User name or password is invalid.")
        elif e.errno == errorcode.ER_ACCOUNT_HAS_BEEN_LOCKED:
            print("This account is locked.")
        else:
            print(e)

    except Exception as e:
        print(f"Error Occurred: {e}")

    finally:
        if cnx is not None and cnx.is_connected():
            cnx.close()