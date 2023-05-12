import os
DIRECTORY = os.getcwd()

BN_ACCESS_KEY_AWS = 'k6YQiFK0UZPUkreaWbddBzlKp4f9l7RPteM8Dq0hFWKTqkyjsSTZRGnsK5SkQCNa'
BN_SECRET_KEY_AWS = 'e5Akp75hIopjlhRGFnDuLnzT3k1oY789rBIC6Im1GbXefYgZHT5CvHMtsHx02yOl'
BN_IP_AWS = '3.37.89.67'

BN_ACCESS_KEY_NAJU = 'k6YQiFK0UZPUkreaWbddBzlKp4f9l7RPteM8Dq0hFWKTqkyjsSTZRGnsK5SkQCNa'
BN_SECRET_KEY_NAJU = 'e5Akp75hIopjlhRGFnDuLnzT3k1oY789rBIC6Im1GbXefYgZHT5CvHMtsHx02yOl'
BN_IP_NAJU = '58.125.138.167'

FILE_URL = DIRECTORY + '/Data'
FILE_URL_BLNC_3M = FILE_URL + '/BalanceList_Coin.pickle'
FILE_URL_SYMB_3M = FILE_URL + '/SymbolList_Coin.pickle'
FILE_URL_PRFT_3M = FILE_URL + '/ProfitList_Coin.pickle'
FILE_URL_BACK = DIRECTORY + '/BacktestResult'
FILE_URL_BLNC_TEST_3M = FILE_URL_BACK + '/BalanceListTest_Coin.pickle'

LINE_URL = 'https://notify-api.line.me/api/notify'
LINE_TOKEN = '48zl8RmuB0lZoPOoVmqowZzjsUE0P53JO7jfVFCyLwh'