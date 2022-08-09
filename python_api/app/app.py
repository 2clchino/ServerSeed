from flask import Flask, jsonify
from flask_cors import CORS
import derby_func as func
import bs4
import re
import os
import csv
import time
import asyncio
import numpy as np
import pandas as pd

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
TEST_RACE_ID = "202201010411"
HORSE_ID = "/horse/2018105233"
RACE = "/race/"
CSV_DIR = "csv"
URL_BASE = "https://db.netkeiba.com"
URL_RACE = "https://race.netkeiba.com/race/shutuba.html?race_id="
RACE_TABLE_NAME = "race_table_01 nk_tb_common"

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

CORS(
  app,
  supports_credentials=True
)

def get_race_id():
  TRAIN_RACE_ID = func.get_train_race_id(func.get_text_from_page('https://race.netkeiba.com/special/index.html?id=0080'))
  print(TRAIN_RACE_ID)

@app.route('/')
def index():
  return jsonify({
    "message": "test message!!!"
  })

if __name__ == '__main__':
  app.run(debug=True)
