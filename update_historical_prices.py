from StupidDB.stupiddb import StupidDB
from lib.api_stuff import API_Stuff
from time import strftime
import datetime
import json
import os
import sys

#today = datetime.datetime.now()
#yesterday = datetime.datetime.now() - datetime.timedelta(hours=24)

today = datetime.datetime.now() - datetime.timedelta(hours=24)
yesterday = datetime.datetime.now() - datetime.timedelta(hours=48)

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

api = API_Stuff()

db = StupidDB(os.path.dirname(__file__)+'/config')
res = db.read('pyquant', 'get_update_close_list')
for r in res:
    close_data = api.yahoo_api_current(r['yahoo_symbol'])
    db.write('pyquant',
        'update_historical_price',
        symbol = r['symbol'],
        close_date = str(today)[:10],
        open = close_data['open'],
        high = close_data['high'],
        low = close_data['low'],
        close = close_data['close'],
        volume = close_data['volume']
        )
    db.write('pyquant', 'update_log_close',
        symbol = r['symbol'],
        date = str(today)[:10]
        )

"""
For some reason, yahoo doesn't supply volume data in api.yahoo_api_current
Retrieving it here
"""
res = db.read('pyquant', 'get_update_yesterday_vol_list')
for r in res:
    data = db.read_single('pyquant', 'get_day', symbol=r['symbol'], close_date=str(yesterday)[:10])
    yest_close_data = api.yahoo_api_hist(r['yahoo_symbol'], str(yesterday)[:10])
    if data is not None and ((data['volume']==0 and yest_close_data['volume']>0) or (data['adj_close']==0.00 and yest_close_data['adj_close']>0.00)):
        db.write('pyquant', 'update_yesterdays_vol',
            volume = yest_close_data['volume'],
            symbol = r['symbol'],
            adj_close = yest_close_data['adj_close'],
            close_date = str(yesterday)[:10]
            )
    db.write('pyquant', 'update_log_vol',
        symbol = r['symbol'],
        date = str(yesterday)[:10]
        )
