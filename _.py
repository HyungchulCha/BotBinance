from BotConfig import *
from BotUtil import *
from pprint import pprint
import pandas as pd
import ccxt

def get_symbols(tks, currency):
    symbols = tks.keys()
    return [x for x in symbols if x.endswith(currency)]

def get_rank_symbols(tks, currency):
    symbols = get_symbols(tks, currency)
    _a = []
    for s in symbols:
        i = bnc.fetch_ticker(s)
        if float(i['change']) > 0:
            _a.append({'s': s, 'v': i['bidVolume']})
    a = sorted(_a, key=lambda x: x['v'])
    return [s['s'] for s in a]

def gen_bnc_df(tk, timeframe, limit):
    ohlcv = bnc.fetch_ohlcv(tk, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    pd_ts = pd.to_datetime(df['datetime'], utc=True, unit='ms')
    pd_ts = pd_ts.dt.tz_convert("Asia/Seoul")
    pd_ts = pd_ts.dt.tz_localize(None)
    df.set_index(pd_ts, inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    return df

####################

apikey = BN_ACCESS_KEY_NAJU
secret = BN_SECRET_KEY_NAJU
curncy = 'USDT'
fltcnc = '/USDT'
basems = '30m'

bnc = ccxt.binance(config={'apiKey': apikey, 'secret': secret, 'enableRateLimit': True})
# mks = bnc.load_markets()
# tks = bnc.fetch_tickers()
# rnk = get_rank_symbols(tks, fltcnc)
# # print(rnk)

# # for r in rnk:
# #     df = gen_bnc_df(r, basems, 80)
# #     print(df)

# blnc = bnc.fetch_balance()[curncy]
# _ttl_evl_prc = float(blnc['total'])
# _buy_max_lmt = float(blnc['free'])
# if _ttl_evl_prc > 300000:
#     _ttl_evl_prc = 300000
#     _buy_max_lmt = blnc['free'] - 300000
# _buy_max_prc = _ttl_evl_prc / 120
# print(_buy_max_lmt > _buy_max_prc)

# test = bnc.fetch_balance()
# print(test.keys())
# print(test['info'])
# print(test['SUI'])
# _balances = test['info']['balances']
# balances = [b for b in _balances if float(b['free']) > 0]
# print(balances)
# print(test['free'])
# print(test['used'])
# print(test['total'])
'''
주문평균가
현재가격, 
보유수량
'''

# _buy_max_lmt > _buy_max_prc
# _buy_max_prc > 10
# # 현재가 * 수량 < 10


# # 매수
# tks_dollar = bnc.fetch_ticker('SUI/USDT')['lastPrice'] # 현재가 - 저장, 갱신값 - 저장
# _buy_max_prc / tks_dollar # 수량
# # 보정수량 * 현재가 > 최소주문금액
# print(tks)

# cancel = bnc.cancel_all_orders()

def get_total_price():
    res = bnc.fetch_balance()
    res_ttl = res['total']
    res_bal = res['info']['balances']
    price_fre = res['USDT']['free']
    price_ttl = 0
    for rb in res_bal:
        if float(rb['free']) > 0 and rb['asset'] != 'USDT':
            current_price = bnc.fetch_ticker(rb['asset'] + '/USDT')['close']
            price_ttl = price_ttl + current_price * res_ttl[rb['asset']]
    price_ttl = price_ttl + price_fre
    return float(price_ttl), float(price_fre)

def get_rank_symbols():
    _symbols = bnc.fetch_tickers().keys()
    symbols = [x for x in _symbols if x.endswith('/USDT')]
    _arr = []
    for s in symbols:
        i = bnc.fetch_ticker(s)
        if i['open'] != None and float(i['change']) > 0:
            _arr.append({'s': s, 'v': i['bidVolume']})
    arr = sorted(_arr, key=lambda x: x['v'])[-60:]
    
    return [s['s'] for s in arr]

def get_balance_code_list(obj=False):
    bal_lst = bnc.fetch_balance()['info']['balances']
    o = {}
    l = [b['asset'] + '/USDT' for b in bal_lst if ((b['asset'] != 'USDT') and (float(b['free']) > 0))]
    for b in bal_lst:
        if float(b['free']) > 0:
            o[b['asset']] = {
                'b': float(b['free']),
            }
    return o if obj else l

# print(get_total_price())
# print(bnc.fetch_ticker('SNT/USDT'))
# print(get_rank_symbols())
# print(get_balance_code_list())
# print(get_balance_code_list(True))
# res = bnc.fetch_open_orders('SUI/USDT')
# for r in res:
#     print(r['info']['orderId'])
#     print(r['info']['side'])
#     print(r['info']['status'])
#     resp = bnc.cancel_order(r['info']['orderId'], 'SUI/USDT')
#     print(resp['info']['status'] == 'CANCELD')
# print(bnc.fetch_closed_orders('SUI/USDT'))
# ADADOWN/USDT
arr = []
bl = bnc.fetch_balance()['info']['balances']
for b in bl:
    arr.append(b['asset'])

# print(arr)


tks = bnc.fetch_tickers()




mks = bnc.load_markets()
pprint(mks['ADADOWN/USDT'])
pprint(mks['FIO/USDT']['info']['permissions'][0])
psb_mks = []
for mk in mks:
    pprint(mks[mk])
    if mks[mk]['spot'] and mks[mk]['info']['permissions'][0] == 'SPOT' and not (mks[mk]['margin']) and mk.endswith('/USDT'):
        psb_mks.append(mk)

print(psb_mks)
print(len(psb_mks))
