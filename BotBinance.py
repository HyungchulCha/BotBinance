from BotConfig import *
from BotUtil import *
from pprint import pprint
from dateutil.relativedelta import *
import ccxt
import datetime
import time
import threading
import datetime
import os
import copy

class BotBinance():


    def __init__(self):

        self.is_aws = True
        self.access_key = BN_ACCESS_KEY_AWS if self.is_aws else BN_ACCESS_KEY_NAJU
        self.secret_key = BN_SECRET_KEY_AWS if self.is_aws else BN_SECRET_KEY_NAJU
        self.bnc = ccxt.binance(config={'apiKey': self.access_key, 'secret': self.secret_key, 'enableRateLimit': True})
        
        self.q_l = []
        self.b_l = []
        self.o_l = {}
        self.p_l = {}

        self.time_order = None
        self.time_rebalance = None

        self.bool_start = False
        self.bool_balance = False
        self.bool_order = False
        
        self.prc_ttl = 0
        self.prc_lmt = 0

        self.const_up = 377500
        self.const_dn = 10

        self.prc_buy_min = 62.5
        self.prc_buy_max = 3775

    
    def init_per_day(self):

        if self.bool_balance == False:

            tn = datetime.datetime.now()
            tn_0 = tn.replace(hour=0, minute=0, second=0)
            tn_d = int(((tn - tn_0).seconds) % 300)
            print(tn_d)

            if tn_d <= 150:
                time.sleep(300 - tn_d - 150)
            else:
                time.sleep(300 - tn_d + 150)

            self.bool_balance = True

        # _tn = datetime.datetime.now()

        print('##################################################')

        self.bnc = ccxt.binance(config={'apiKey': self.access_key, 'secret': self.secret_key, 'enableRateLimit': True})
        
        self.q_l = self.get_filter_ticker()
        prc_ttl, prc_lmt, _, bal_lst  = self.get_balance_info()
        self.b_l = list(set(self.q_l + bal_lst))
        self.prc_ttl = prc_ttl if prc_ttl < self.const_up else self.const_up
        self.prc_lmt = prc_lmt if prc_ttl < self.const_up else prc_lmt - self.const_up

        if os.path.isfile(FILE_URL_PRFT_3M):
            self.p_l = load_file(FILE_URL_PRFT_3M)
        else:
            self.p_l = {}
            save_file(FILE_URL_PRFT_3M, self.p_l)

        for mk in self.b_l:
            if not (mk in self.p_l):
                self.p_l[mk] = {'ttl_pft': 1, 'sum_pft': 0, 'fst_qty': 0}

        line_message(f'BotBinance \nTotal Price : {self.prc_ttl} USDT \nSymbol List : {len(self.b_l)}')

        __tn = datetime.datetime.now()
        __tn_min = __tn.minute % 5
        __tn_sec = __tn.second

        self.time_rebalance = threading.Timer(300 - (60 * __tn_min) - __tn_sec + 150, self.init_per_day)
        self.time_rebalance.start()


    def stock_order(self):

        if self.bool_order == False:

            tn = datetime.datetime.now()
            tn_0 = tn.replace(hour=0, minute=0, second=0)
            tn_d = int(((tn - tn_0).seconds) % 300)
            time.sleep(300 - tn_d)
            self.bool_order = True

        _tn = datetime.datetime.now()

        # self.get_remain_cancel(self.b_l)

        _, _, bal_lst, _ = self.get_balance_info()
        sel_lst = []

        if os.path.isfile(FILE_URL_BLNC_3M):
            obj_lst = load_file(FILE_URL_BLNC_3M)
        else:
            obj_lst = {}
            save_file(FILE_URL_BLNC_3M, obj_lst)

        for symbol in self.b_l:

            # if symbol == 'CHESS/USDT':
            #     self.p_l['CHESS/USDT']['ttl_pft'] = 1.03

            is_notnul_obj = not (not obj_lst)
            is_symbol_bal = symbol in bal_lst
            is_symbol_obj = symbol in obj_lst

            df = self.gen_neck_df(self.gen_bnc_df(symbol, '5m', 80))

            if not (df is None):
                
                df_head = df.tail(2).head(1)
                cls_val = df_head['close'].iloc[-1]
                clp_val = df_head['close_prev'].iloc[-1]
                hgt_val = df_head['height_5_20'].iloc[-1]
                m05_val = df_head['ma05'].iloc[-1]
                m20_val = df_head['ma20'].iloc[-1]
                m60_val = df_head['ma60'].iloc[-1]

                cur_prc = float(cls_val)
                prc_buy = self.p_l[symbol]['ttl_pft'] * self.prc_buy_min
                prc_buy = self.prc_buy_max if (prc_buy > self.prc_buy_max) else self.prc_buy_min if (prc_buy < self.prc_buy_min) else prc_buy
                cur_bal = prc_buy / cur_prc
                is_posble_ord = self.prc_lmt > prc_buy

                if is_symbol_bal and (not is_symbol_obj):
                    obj_lst[symbol] = {'x': cur_prc, 'a': cur_prc, 's': 1, 'd': datetime.datetime.now().strftime('%Y%m%d')}
                    # print(f'{symbol} : Miss Match, Obj[X], Bal[O] !!!')
                
                if not is_symbol_bal and is_symbol_obj:
                    obj_lst.pop(symbol, None)
                    # print(f'{symbol} : Miss Match, Obj[O], Bal[X] !!!')

                if is_symbol_bal and ((self.p_l[symbol]['fst_qty'] == 0) or (cur_prc * bal_lst[symbol]['b'] <= self.const_dn)):
                    self.p_l[symbol]['fst_qty'] = copy.deepcopy(bal_lst[symbol]['b'])
                    self.p_l[symbol]['sum_pft'] = 0
                    # print(f'{symbol} : Insert Quantity, Pft[X], Bal[O] !!!')

                if is_posble_ord and ((not is_symbol_bal) or (is_symbol_bal and (cur_prc * bal_lst[symbol]['b'] <= self.const_dn))):

                    if \
                    (1.1 < hgt_val < 5) and \
                    (m60_val < m20_val < m05_val < cls_val < clp_val * 1.05) and \
                    (m20_val < cls_val < m20_val * 1.05) \
                    :
                        
                        resp = self.bnc.create_market_buy_order(symbol=symbol, amount=cur_bal)
                        # print(resp)
                        # resp = self.bnc.create_order(symbol, 'market', 'buy', cur_bal, None, {'test': True})
                        # print(resp)
                        obj_lst[symbol] = {'a': cur_prc, 'x': cur_prc, 's': 1, 'd': datetime.datetime.now().strftime('%Y%m%d')}
                        prv_qty = copy.deepcopy(self.p_l[symbol]['fst_qty'])
                        rel_qty = cur_bal - (cur_bal * 0.001) + prv_qty
                        self.p_l[symbol]['fst_qty'] = rel_qty
                        self.p_l[symbol]['sum_pft'] = 0
                        print(f'Buy - Symbol: {symbol}, Balance: {rel_qty}')
                        sel_lst.append({'c': '[B] ' + symbol, 'r': (rel_qty)})                   

                if is_symbol_bal and is_notnul_obj:
                    
                    t1 = 0.01
                    t2 = 0.015
                    t3 = 0.02
                    h1 = 1
                    h2 = 1
                    h3 = 1
                    ct = 0.975
                    hp = 1.05

                    if obj_lst[symbol]['x'] < cur_prc:

                        obj_lst[symbol]['x'] = cur_prc

                        obj_fst = copy.deepcopy(obj_lst[symbol]['a'])
                        obj_max = copy.deepcopy(obj_lst[symbol]['x'])
                        sel_cnt = copy.deepcopy(obj_lst[symbol]['s'])
                        obj_pft = ror(obj_fst, obj_max)
                        bal_pft = ror(obj_fst, cur_prc)

                        ord_qty_00 = copy.deepcopy(bal_lst[symbol]['b'])
                        ord_qty_01 = ord_qty_00 * 0.3
                        ord_qty_02 = ord_qty_00 * 0.5
                        psb_ord_00 = cur_prc * ord_qty_00 > self.const_dn
                        psd_ord_01 = cur_prc * ord_qty_01 > self.const_dn
                        psb_ord_02 = cur_prc * ord_qty_02 > self.const_dn

                        # print(f'{symbol} : Current Price {cur_prc}, Current Profit {round(bal_pft, 4)}, Increase !!!')

                        if 1 < bal_pft < hp:

                            if (sel_cnt == 1) and (h1 <= bal_pft) and psb_ord_00:
                                
                                bool_01_end = False
                                if psd_ord_01:
                                    qty = ord_qty_01
                                elif psb_ord_02:
                                    qty = ord_qty_02
                                else:
                                    qty = ord_qty_00
                                    bool_01_end = True

                                resp = self.bnc.create_market_sell_order(symbol=symbol, amount=qty)
                                # print(resp)
                                # resp = self.bnc.create_order(symbol, 'market', 'sell', qty, None, {'test': True})
                                # print(resp)
                                _ror = ror(obj_fst * qty, cur_prc * qty)
                                print(f'Sell - Symbol: {symbol}, Profit: {round(_ror, 4)}')
                                sel_lst.append({'c': '[SH1] ' + symbol, 'r': round(_ror, 4)})
                                obj_lst[symbol]['d'] = datetime.datetime.now().strftime('%Y%m%d')
                                obj_lst[symbol]['s'] = sel_cnt + 1

                                if bool_01_end:
                                    obj_lst.pop(symbol, None)

                                self.set_profit_list(symbol, qty, _ror, bool_01_end)
                            
                            elif (sel_cnt == 2) and (h2 <= bal_pft) and psb_ord_00:

                                bool_02_end = False
                                if psb_ord_02:
                                    qty = ord_qty_02
                                else:
                                    qty = ord_qty_00
                                    bool_02_end = True

                                resp = self.bnc.create_market_sell_order(symbol=symbol, amount=qty)
                                # print(resp)
                                # resp = self.bnc.create_order(symbol, 'market', 'sell', qty, None, {'test': True})
                                # print(resp)
                                _ror = ror(obj_fst * qty, cur_prc * qty)
                                print(f'Sell - Symbol: {symbol}, Profit: {round(_ror, 4)}')
                                sel_lst.append({'c': '[SH2] ' + symbol, 'r': round(_ror, 4)})
                                obj_lst[symbol]['d'] = datetime.datetime.now().strftime('%Y%m%d')
                                obj_lst[symbol]['s'] = sel_cnt + 1

                                if bool_02_end:
                                    obj_lst.pop(symbol, None)

                                self.set_profit_list(symbol, qty, _ror, bool_02_end)

                            elif (sel_cnt == 3) and (h3 <= bal_pft) and psb_ord_00:

                                resp = self.bnc.create_market_sell_order(symbol=symbol, amount=ord_qty_00)
                                # print(resp)
                                # resp = self.bnc.create_order(symbol, 'market', 'sell', ord_qty_00, None, {'test': True})
                                # print(resp)
                                _ror = ror(obj_fst * ord_qty_00, cur_prc * ord_qty_00)
                                print(f'Sell - Symbol: {symbol}, Profit: {round(_ror, 4)}')
                                sel_lst.append({'c': '[SH3] ' + symbol, 'r': round(_ror, 4)})
                                obj_lst[symbol]['d'] = datetime.datetime.now().strftime('%Y%m%d')
                                obj_lst[symbol]['s'] = sel_cnt + 1
                                obj_lst.pop(symbol, None)

                                self.set_profit_list(symbol, ord_qty_00, _ror, True)

                        elif (hp <= bal_pft) and psb_ord_00:

                            resp = self.bnc.create_market_sell_order(symbol=symbol, amount=ord_qty_00)
                            # print(resp)
                            # resp = self.bnc.create_order(symbol, 'market', 'sell', ord_qty_00, None, {'test': True})
                            # print(resp)
                            _ror = ror(obj_fst * ord_qty_00, cur_prc * ord_qty_00)
                            print(f'Sell - Symbol: {symbol}, Profit: {round(_ror, 4)}')
                            sel_lst.append({'c': '[S+] ' + symbol, 'r': round(_ror, 4)})
                            obj_lst.pop(symbol, None)

                            self.set_profit_list(symbol, ord_qty_00, _ror, True)

                    elif obj_lst[symbol]['x'] > cur_prc:
                        
                        obj_fst = copy.deepcopy(obj_lst[symbol]['a'])
                        obj_max = copy.deepcopy(obj_lst[symbol]['x'])
                        obj_pft = ror(obj_fst, obj_max)
                        bal_pft = ror(obj_fst, cur_prc)
                        los_dif = obj_pft - bal_pft
                        sel_cnt = copy.deepcopy(obj_lst[symbol]['s'])

                        ord_qty_00 = copy.deepcopy(bal_lst[symbol]['b'])
                        ord_qty_01 = ord_qty_00 * 0.3
                        ord_qty_02 = ord_qty_00 * 0.5
                        psb_ord_00 = cur_prc * ord_qty_00 > self.const_dn
                        psd_ord_01 = cur_prc * ord_qty_01 > self.const_dn
                        psb_ord_02 = cur_prc * ord_qty_02 > self.const_dn

                        # print(f'{symbol} : Max Price {obj_max}, Max Profit {round(obj_pft, 4)}, Current Price {cur_prc}, Current Profit {round(bal_pft, 4)}')

                        if 1 < bal_pft < hp:

                            if (sel_cnt == 1) and (t1 <= los_dif) and psb_ord_00:
                                
                                bool_01_end = False
                                if psd_ord_01:
                                    qty = ord_qty_01
                                elif psb_ord_02:
                                    qty = ord_qty_02
                                else:
                                    qty = ord_qty_00
                                    bool_01_end = True

                                resp = self.bnc.create_market_sell_order(symbol=symbol, amount=qty)
                                # print(resp)
                                # resp = self.bnc.create_order(symbol, 'market', 'sell', qty, None, {'test': True})
                                # print(resp)
                                _ror = ror(obj_fst * qty, cur_prc * qty)
                                print(f'Sell - Symbol: {symbol}, Profit: {round(_ror, 4)}')
                                sel_lst.append({'c': '[ST1] ' + symbol, 'r': round(_ror, 4)})
                                obj_lst[symbol]['d'] = datetime.datetime.now().strftime('%Y%m%d')
                                obj_lst[symbol]['s'] = sel_cnt + 1

                                if bool_01_end:
                                    obj_lst.pop(symbol, None)

                                self.set_profit_list(symbol, qty, _ror, bool_01_end)
                            
                            elif (sel_cnt == 2) and (t2 <= los_dif) and psb_ord_00:

                                bool_02_end = False
                                if psb_ord_02:
                                    qty = ord_qty_02
                                else:
                                    qty = ord_qty_00
                                    bool_02_end = True

                                resp = self.bnc.create_market_sell_order(symbol=symbol, amount=qty)
                                # print(resp)
                                # resp = self.bnc.create_order(symbol, 'market', 'sell', qty, None, {'test': True})
                                # print(resp)
                                _ror = ror(obj_fst * qty, cur_prc * qty)
                                print(f'Sell - Symbol: {symbol}, Profit: {round(_ror, 4)}')
                                sel_lst.append({'c': '[ST2] ' + symbol, 'r': round(_ror, 4)})
                                obj_lst[symbol]['d'] = datetime.datetime.now().strftime('%Y%m%d')
                                obj_lst[symbol]['s'] = sel_cnt + 1

                                if bool_02_end:
                                    obj_lst.pop(symbol, None)

                                self.set_profit_list(symbol, qty, _ror, bool_02_end)

                            elif (sel_cnt == 3) and (t3 <= los_dif) and psb_ord_00:

                                resp = self.bnc.create_market_sell_order(symbol=symbol, amount=ord_qty_00)
                                # print(resp)
                                # resp = self.bnc.create_order(symbol, 'market', 'sell', ord_qty_00, None, {'test': True})
                                # print(resp)
                                _ror = ror(obj_fst * ord_qty_00, cur_prc * ord_qty_00)
                                print(f'Sell - Symbol: {symbol}, Profit: {round(_ror, 4)}')
                                sel_lst.append({'c': '[ST3] ' + symbol, 'r': round(_ror, 4)})
                                obj_lst[symbol]['d'] = datetime.datetime.now().strftime('%Y%m%d')
                                obj_lst[symbol]['s'] = sel_cnt + 1
                                obj_lst.pop(symbol, None)

                                self.set_profit_list(symbol, ord_qty_00, _ror, True)

                        elif (hp <= bal_pft) and psb_ord_00:

                            resp = self.bnc.create_market_sell_order(symbol=symbol, amount=ord_qty_00)
                            # print(resp)
                            # resp = self.bnc.create_order(symbol, 'market', 'sell', ord_qty_00, None, {'test': True})
                            # print(resp)
                            _ror = ror(obj_fst * ord_qty_00, cur_prc * ord_qty_00)
                            print(f'Sell - Symbol: {symbol}, Profit: {round(_ror, 4)}')
                            sel_lst.append({'c': '[S+] ' + symbol, 'r': round(_ror, 4)})
                            obj_lst.pop(symbol, None)

                            self.set_profit_list(symbol, ord_qty_00, _ror, True)

                        elif (bal_pft <= ct) and psb_ord_00:

                            resp = self.bnc.create_market_sell_order(symbol=symbol, amount=ord_qty_00)
                            # print(resp)
                            # resp = self.bnc.create_order(symbol, 'market', 'sell', ord_qty_00, None, {'test': True})
                            # print(resp)
                            _ror = ror(obj_fst * ord_qty_00, cur_prc * ord_qty_00)
                            print(f'Sell - Symbol: {symbol}, Profit: {round(_ror, 4)}')
                            sel_lst.append({'c': '[S-] ' + symbol, 'r': round(_ror, 4)})
                            obj_lst.pop(symbol, None)

                            self.set_profit_list(symbol, ord_qty_00, _ror, True)

        save_file(FILE_URL_BLNC_3M, obj_lst)
        save_file(FILE_URL_PRFT_3M, self.p_l)
        # print(self.p_l)

        sel_txt = ''
        for sl in sel_lst:
            sel_txt = sel_txt + '\n' + str(sl['c']) + ' : ' + str(sl['r'])

        __tn = datetime.datetime.now()
        __tn_min = __tn.minute % 5
        __tn_sec = __tn.second

        self.time_backtest = threading.Timer(300 - (60 * __tn_min) - __tn_sec, self.stock_order)
        self.time_backtest.start()

        line_message(f'BotBinance \nStart : {_tn}, \nEnd : {__tn}, \nTotal Price : {float(self.prc_ttl)} USDT, {sel_txt}')


    # Spot, USDT Filter Ticker
    def get_filter_ticker(self):
        mks = self.bnc.load_markets()
        lst = []
        for mk in mks:
            if \
            mk.endswith('/USDT') and \
            mks[mk]['info']['status'] == 'TRADING' and \
            mks[mk]['info']['isSpotTradingAllowed'] == True and \
            mks[mk]['info']['isMarginTradingAllowed'] == False and \
            'SPOT' in mks[mk]['info']['permissions'] and \
            not ('MARGIN' in mks[mk]['info']['permissions']) \
            :
                lst.append(mk)

        return lst
    

    # Generate Neck Dataframe
    def gen_neck_df(self, df):

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
    

    # Generate Dataframe
    def gen_bnc_df(self, tk, tf, lm):
        ohlcv = self.bnc.fetch_ohlcv(tk, timeframe=tf, limit=lm)
        if not (ohlcv is None) and len(ohlcv) >= lm:
            df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
            pd_ts = pd.to_datetime(df['datetime'], utc=True, unit='ms')
            pd_ts = pd_ts.dt.tz_convert("Asia/Seoul")
            pd_ts = pd_ts.dt.tz_localize(None)
            df.set_index(pd_ts, inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']]

            return self.gen_neck_df(df)
        

    # Balance Code List
    def get_balance_info(self):
        balance = self.bnc.fetch_balance()
        bal_ttl = balance['total']
        bal_lst = balance['info']['balances']
        bal_fre = float(balance['USDT']['free'])
        prc = 0
        obj = {}
        lst = []
        for bl in bal_lst:
            free = float(bl['free'])
            asst = bl['asset']
            tikr = asst + '/USDT'
            if free > 0 and asst != 'USDT':
                obj[tikr] = {
                    'b': free,
                }
                cls = self.bnc.fetch_ticker(tikr)['close']
                prc = prc + (cls * bal_ttl[asst])
                lst.append(tikr)
        prc = prc + bal_fre

        return prc, bal_fre, obj, lst
    
    
    # Not Signed Cancel Order
    def get_remain_cancel(self, l):
        for _l in l:
            rmn_lst = self.bnc.fetch_open_orders(_l)
            print(rmn_lst)
            if len(rmn_lst) > 0:
                for rmn in rmn_lst:
                    if rmn['status'] == 'open':
                        self.bnc.cancel_order(rmn['info']['orderId'], _l)

    
    # Set Profit List
    def set_profit_list(self, symbol, qty, _ror, end=False):
        pft_sum = copy.deepcopy(self.p_l[symbol]['sum_pft'])
        pft_cur = (qty / self.p_l[symbol]['fst_qty']) * _ror
        self.p_l[symbol]['sum_pft'] = pft_sum + pft_cur

        if end:
            pft_ttl = copy.deepcopy(self.p_l[symbol]['ttl_pft'])
            pft_sum = copy.deepcopy(self.p_l[symbol]['sum_pft'])

            self.p_l[symbol]['ttl_pft'] = pft_ttl * pft_sum
            self.p_l[symbol]['fst_qty'] = 0
            self.p_l[symbol]['sum_pft'] = 0

            print(symbol, self.p_l[symbol]['ttl_pft'])

            if self.p_l[symbol]['ttl_pft'] > 2:
                line_message(symbol, pft_ttl, pft_sum)

    
    # All Sell
    def all_sell_order(self):
        _, _, bal_lst, _  = self.get_balance_info()
        for bl in bal_lst:
            cls = self.bnc.fetch_ticker(bl)['close']
            prc = cls * bal_lst[bl]['b']
            if prc > 10:
                resp = self.bnc.create_market_sell_order(bl, bal_lst[bl]['b'])
                print(resp)
                time.sleep(0.25)


if __name__ == '__main__':

    bb = BotBinance()
    # bb.init_per_day()
    # bb.stock_order()
    # bb.all_sell_order()

    while True:

        try:

            tn = datetime.datetime.now()
            tn_start = tn.replace(hour=0, minute=0, second=0)

            if tn >= tn_start and bb.bool_start == False:
                bb.init_per_day()
                bb.stock_order()
                bb.bool_start = True

        except Exception as e:

            line_message(f"BotBinance Error : {e}")
            break