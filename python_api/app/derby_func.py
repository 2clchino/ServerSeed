import csv
import requests
import bs4
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# https://race.netkeiba.com/special/index.html?id=0059
# ↑の形式のURLから過去レースID取得
def get_train_race_id(text, max_cnt = 21, min_cnt = 0):
    try:  
        info = []
        soup = bs4.BeautifulSoup(text, "html.parser")
        base_elem = soup.find(class_="All_Special_Table")
        elems = base_elem.find_all("tr")
        for elem in elems:
            r_class = elem.find_all("a")
            for r_c in r_class:
                r_url = r_c.get("href")
                if (not r_url == None):
                    if ('/race/' in r_url and not "?race_id" in r_url):
                        info.append(r_url[-13:-1])
        return (info[min_cnt:max_cnt])
    except:
        print("err")
        return None

class RaceRank(object):
    def __init__(self, id, score, rank):
        self.id = id
        self.score = score
        self.rank = rank

def race_rank():
    rank = []
    rank.append(RaceRank(1, 100, "G1"))
    rank.append(RaceRank(2, 70, "G2"))
    rank.append(RaceRank(3, 50, "G3"))
    rank.append(RaceRank(4, 40, "L"))
    rank.append(RaceRank(5, 40, "OP"))
    rank.append(RaceRank(6, 30, "3勝"))
    rank.append(RaceRank(7, 30, "1600万下"))
    rank.append(RaceRank(8, 20, "2勝"))
    rank.append(RaceRank(9, 20, "1000万下"))
    rank.append(RaceRank(10, 10, "1勝"))
    rank.append(RaceRank(11, 10, "500万下"))
    rank.append(RaceRank(12, 5, "未勝利"))
    rank.append(RaceRank(13, 5, "新馬"))
    return rank

def race_data_columns():
    return [
    "rank",
    "frame_number",
    "horse_number",
    "horse_name",
    "aptitude_course",
    "aptitude_distance",
    "aptitude_run",
    "aptitude_growth",
    "aptitude_ground",
    "age",
    "weight",
    "jockey",
    "time",
    "difference",
    "time_score",
    "lap_time",
    "final_3F",
    "odds",
    "popularity",
    "horse_weight",
    "traning_time",
    "coment",
    "coment_2",
    "trainer",
    "owner",
    "reward"]

def horse_data_columns():
    return [
    "date",
    "place",
    "weather",
    "R",
    "race_name",
    "video",
    "head_count",
    "frame_number",
    "horce_number",
    "odds",
    "popularity",
    "rank",
    "jockey",
    "weight",
    "distance",
    "ground",
    "ground_score",
    "time",
    "difference",
    "time_score",
    "lap_time",
    "pace",
    "final_3F",
    "horce_weight",
    "coment",
    "coment_2",
    "winner",
    "reward",
    "race_id"]

def clear_all_str(df):
    df = df.drop(columns = ["horse_name", "age", "horse_data_key", "odds", "popularity", "horse_number"], errors = 'ignore')
    df['horse_weight_plus'] = df.apply(lambda x: x['horse_weight'].split('(')[1].strip(')'), axis = 1)
    df['horse_weight'] = df.apply(lambda x: x['horse_weight'].split('(')[0], axis = 1)
    df = df.drop(columns = ["horse_weight", 'horse_weight_plus'])
    df['rank'] = df.apply(lambda x: 0 if x['rank'] > 3 else 1, axis = 1)
    return df

def create_param(df):
    df_all_races_train = df.copy()
    df_all_races_train = clear_all_str(df_all_races_train)
    tmp = df_all_races_train['rank'].values.astype(np.int).flatten()
    df_all_races_train = df_all_races_train.drop(columns = ["rank"])
    return (df_all_races_train, tmp)

def create_params(df_all_races_train_2, df_all_races_test_2):
    df_all_races_train = df_all_races_train_2.copy()
    df_all_races_train = clear_all_str(df_all_races_train)
    tmp = df_all_races_train['rank'].values.astype(np.int).flatten()
    df_all_races_train = df_all_races_train.drop(columns = ["rank"])
    df_all_races_test = df_all_races_test_2.copy()
    df_all_races_test = clear_all_str(df_all_races_test)
    df_all_races_test = df_all_races_test.drop(columns = ["rank"])
    return (df_all_races_train, df_all_races_test, tmp)

def calc_importance(model, x_train):
    s = []
    g = x_train
    orig_out = model.predict(g)
    for i in range(x_train.shape[1]):
        new_x = g.copy()
        perturbation = np.random.normal(0.0, 100.0, size=new_x.shape[:1])
        new_x[:, i] = new_x[:, i] + perturbation
        perturbed_out = model.predict(new_x)
        effect = ((orig_out - perturbed_out) ** 2).mean() ** 0.5
        s.append(effect)
    return s

def print_importance(array, columns):
    s = array.copy()
    s.sort(reverse=True)
    d = []
    for i in range(len(s)):
        for j in range(len(array)):
            if s[i] == array[j]:
                d.append(columns[j])
    for i in range(len(s)):
        a = s[i] / sum(s) * 100
        print(f'{d[i]}, perturbation effect: {a:.2f}%')

def plot_importance(array, columns):
    importances = pd.DataFrame({"features":columns, "importances" : array})
    importances.sort_values(by="importances", inplace=True, ignore_index=True)
    plt.figure(figsize=(8, 5))
    plt.barh(importances['features'], importances['importances'])
    plt.title("perturbation effect", fontsize=14)
    plt.show()

def get_old_race_info_from_text(header_flg, text, table_name, race_id, race_name):
    try:  
        info = []
        horse_id = []
        horse_names = []
        soup = bs4.BeautifulSoup(text, "html.parser")
        base_elem = soup.find(class_=table_name)
        elems = base_elem.find_all("tr")
        for elem in elems:
            row_info = []
            r_class = elem.get("class")
            r_cols = None
            if r_class==None:
                r_cols = elem.find_all("td")
            else:
                if header_flg:
                    r_cols = elem.find_all("th")
            if not r_cols==None:
                for r_col in r_cols:
                    scores = []
                    tmp_text = r_col.text
                    link = r_col.find("a")
                    if not link==None:
                        tmp = link.get('href')
                        if 'horse' in tmp and not '?pid' in tmp:
                            horse_id.append(tmp[:-1])
                            (name, scores) = get_horse_data(tmp[:-1], race_id, race_name)
                            horse_names.append(name)
                    tmp_text = tmp_text.replace("\n", "")
                    row_info.append(tmp_text.strip())
                    for score in scores:
                        row_info.append(score[0])
                info.append(row_info)
        return (info, horse_id, horse_names)
    except:
        print("err")
        return None

def get_race_info_from_text(text, table_name, race_id, race_name):
    try:  
        info = []
        horse_id = []
        horse_names = []
        soup = bs4.BeautifulSoup(text, "html.parser")
        base_elem = soup.find(class_=table_name)
        elems = base_elem.find_all("tr")
        for elem in elems:
            row_info = []
            scores = []
            r_cols = elem.find_all("td")
            if not r_cols==None:
                for r_col in r_cols:
                    if (not r_col==None):
                        tmp_text = r_col.text
                        tmp_text = tmp_text.replace("\n", "")
                        row_info.append(tmp_text.strip())
                        links = r_col.find_all("a")
                        for link in links:
                            if not link==None:
                                r_a = link.get("href")
                                if "horse/" in r_a:
                                    row_info.append(r_a)
                                    horse_id.append(r_a[23:])
                                    (name, scores) = get_horse_data(r_a[23:], race_id, race_name)
                                    horse_names.append(name)
                                    for score in scores:
                                        row_info.append(score[0])
            info.append(row_info)
        return (info, horse_id, horse_names)
    except:
        print("err")
        return None

def get_horse_info_from_text(header_flg, text, table_name):
    try:
        info = []
        soup = bs4.BeautifulSoup(text, "html.parser")
        base_elem = soup.find(class_=table_name)
        elems = base_elem.find_all("tr")
        param = soup.find(class_="db_prof_box")
        params = param.find_all("img")
        score = []
        score_2 = []
        for prm in params:
            score.append(prm.get("width"))
        if (len(score) > 18):
            for i in range(5):
                score_2.append([score[i * 5 + 1], score[i * 5 + 3]])
        for elem in elems:
            race_id = ""
            row_info = []
            r_class = elem.get("class")
            r_cols = None
            if r_class==None:
                r_cols = elem.find_all("td")
            else:
                if header_flg:
                    r_cols = elem.find_all("th")
            if not r_cols==None:
                for r_col in r_cols:
                    links = r_col.find_all("a")
                    for link in links:
                        if (not link==None):
                            tmp = link.get('href')
                            if '/race/' in tmp and not 'sum' in tmp and not 'list' in tmp and not 'movie' in tmp:
                                race_id = str(tmp)
                    tmp_text = r_col.text
                    tmp_text = tmp_text.replace("\n", "")
                    row_info.append(tmp_text.strip())
                if not race_id=="":
                    row_info.append(race_id[6:len(race_id) - 1])
                info.append(row_info)
            
        return (info, score_2)
    except:
        print("err")
        return None

def get_name_from_text(text):
    try:
        soup = bs4.BeautifulSoup(text, "html.parser")
        title_text = soup.find('title').get_text()
        return title_text
    except:
        print("err")
        return None

def get_horse_data(horse_id, race_id, race_name):
    URL_BASE = "https://db.netkeiba.com"
    HORSE_TABLE_NAME = "db_h_race_results nk_tb_common"
    url = URL_BASE + horse_id
    text = get_text_from_page(url)
    (info, score) = get_horse_info_from_text(False, text, HORSE_TABLE_NAME)
    tmp = get_name_from_text(text)
    if not tmp==None:
        horse_name = tmp.replace('競馬データベース - netkeiba.com', '').split(' ')
        print(horse_name[0])
        file_path = "csv/horse/" + race_id[0:4] + race_name + "/" + horse_name[0] + ".csv"
        with open(file_path, "w", newline="", encoding='shift_jis') as f:
            writer = csv.writer(f)
            writer.writerows(info)
        return (horse_name[0], score)

def get_text_from_page(url):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36   '
    }
    try:
        res = requests.get(url, headers=HEADERS)
        res.encoding = res.apparent_encoding  
        text = res.text
        return text
    except:
        return None