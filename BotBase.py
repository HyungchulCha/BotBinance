# from BotConfig import *
# from BotUtil import *
# from pprint import pprint
# import pandas as pd
# import ccxt

# # Account
# bnc = ccxt.binance(config={'apiKey': BN_ACCESS_KEY_NAJU, 'secret': BN_SECRET_KEY_NAJU, 'enableRateLimit': True})

# # Spot, USDT Filter Ticker
# def get_filter_ticker():
#     mks = bnc.load_markets()
#     lst = []
#     for mk in mks:
#         if \
#         mk.endswith('/USDT') and \
#         mks[mk]['info']['status'] == 'TRADING' and \
#         mks[mk]['info']['isSpotTradingAllowed'] == True and \
#         mks[mk]['info']['isMarginTradingAllowed'] == False and \
#         'SPOT' in mks[mk]['info']['permissions'] and \
#         not ('MARGIN' in mks[mk]['info']['permissions']) \
#         :
#             lst.append(mk)

#     return lst

# # Generate Neck Dataframe
# def gen_neck_df(df):

#     df['close_prev'] = df['close'].shift()
#     df['ma05'] = df['close'].rolling(5).mean()
#     df['ma20'] = df['close'].rolling(20).mean()
#     df['ma60'] = df['close'].rolling(60).mean()
#     df['ma05_prev'] = df['ma05'].shift()
#     df['ma20_prev'] = df['ma20'].shift()
#     df['ma60_prev'] = df['ma60'].shift()
#     height_5_20_max = df['high'].rolling(20).max()
#     height_5_20_min = df['low'].rolling(20).min()
#     df['height_5_20'] = (((height_5_20_max / height_5_20_min) - 1) * 100).shift(5)

#     return df

# # Generate Dataframe
# def gen_bnc_df(tk, tf, lm):
#     ohlcv = bnc.fetch_ohlcv(tk, timeframe=tf, limit=lm)
#     if not (ohlcv is None) and len(ohlcv) >= lm:
#         df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
#         pd_ts = pd.to_datetime(df['datetime'], utc=True, unit='ms')
#         pd_ts = pd_ts.dt.tz_convert("Asia/Seoul")
#         pd_ts = pd_ts.dt.tz_localize(None)
#         df.set_index(pd_ts, inplace=True)
#         df = df[['open', 'high', 'low', 'close', 'volume']]

#         return gen_neck_df(df)

# # Balance Code List
# def get_balance_info():
#     balance = bnc.fetch_balance()
#     bal_ttl = balance['total']
#     bal_lst = balance['info']['balances']
#     bal_fre = balance['USDT']['free']
#     prc = 0
#     obj = {}
#     lst = []
#     for bl in bal_lst:
#         free = float(bl['free'])
#         asst = bl['asset']
#         tikr = asst + '/USDT'
#         if free > 0:
#             obj[tikr] = {
#                 'b': free,
#             }
#             if asst != 'USDT':
#                 cls = bnc.fetch_ticker(tikr)['close']
#                 prc = prc + (cls * bal_ttl[asst])
#                 lst.append(tikr)
#     prc = prc + bal_fre

#     return prc, obj, lst

_, _, _, a = (1, 2, 3, 4)
print(a)