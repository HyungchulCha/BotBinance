from BotConfig import *
from BotUtil import *
from pprint import pprint
import pandas as pd
import ccxt

apikey = BN_ACCESS_KEY_NAJU
secret = BN_SECRET_KEY_NAJU
curncy = 'USDT'
fltcnc = '/USDT'
basems = '30m'

bnc = ccxt.binance(config={'apiKey': apikey, 'secret': secret, 'enableRateLimit': True})
def get_rank_symbols():
    mks = bnc.load_markets()
    symbols = []
    for mk in mks:
        if mks[mk]['status'] == 'TRADING' and mks[mk]['spot'] and mks[mk]['info']['permissions'][0] == 'SPOT' and mk.endswith('/USDT'):
            symbols.append(mk)
    # _arr = []
    # for s in symbols:
    #     i = self.pb.fetch_ticker(s)
    #     if i['open'] != None and float(i['change']) > 0:
    #         _arr.append({'s': s, 'v': i['bidVolume']})
    # arr = sorted(_arr, key=lambda x: x['v'])[-60:]
    
    # return [s['s'] for s in arr]
    return symbols

mks = bnc.load_markets()
pprint(mks['MINA/USDT']['info'])
pprint(mks['NU/USDT']['info']['status'])
