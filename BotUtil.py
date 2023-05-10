from BotConfig import *
import pandas as pd
import os
import pickle
import requests
import math

def gen_neck_df(df, is_yf=False):

    '''
    종가 - 1000원 이상, 거래량 - 200000 이상
    종가 - 1봉전 종가 대비 5% 이하
    5봉전부터 20봉간 최고최저폭 20% 이상
    60이평 < 20이평 < 5이평
    20이평 < 종가 < 20이평 * 1.05
    '''

    if is_yf:
        df['high'] = df['High']
        df['low'] = df['Low']
        df['close'] = df['Adj Close']
        df['volume'] = df['Volume']

    if not (df is None):

        df['close_prev'] = df['close'].shift()
        df['ma05'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma60'] = df['close'].rolling(60).mean()
        df['ma05_prev'] = df['ma05'].shift()
        df['ma20_prev'] = df['ma20'].shift()
        df['ma60_prev'] = df['ma60'].shift()
        height_5_20_max = df['high'].rolling(20).max()
        height_5_20_min = df['low'].rolling(20).min()
        df['height_5_20'] = (((height_5_20_max / height_5_20_min) - 1) * 100).shift(5)

        return df


def save_xlsx(url, df):
    df.to_excel(url)


def load_xlsx(url):
    return pd.read_excel(url)


def save_file(url, obj):
    with open(url, 'wb') as f:
        pickle.dump(obj, f)


def load_file(url):
    with open(url, 'rb') as f:
        return pickle.load(f)
    

def delete_file(url):
    if os.path.exists(url):
        for file in os.scandir(url):
            os.remove(file.path)


def get_qty(crnt_p, max_p):
    q = int(max_p / crnt_p)
    return 1 if q == 0 else q


def ror(pv, nv, pr=1, pf=0.001, spf=0):
    cr = ((nv - (nv * pf) - (nv * spf)) / (pv + (pv * pf)))
    return pr * cr


def line_message(msg):
    print(msg)
    requests.post(LINE_URL, headers={'Authorization': 'Bearer ' + LINE_TOKEN}, data={'message': msg})