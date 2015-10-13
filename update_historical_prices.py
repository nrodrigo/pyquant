from StupidDB.stupiddb import StupidDB
from lib.api_stuff import API_Stuff
from time import strftime
import datetime
import json
import os
import sys

today = datetime.datetime.now()
#today = datetime.datetime.strptime('2015-10-08', '%Y-%m-%d')
yesterday = datetime.datetime.now() - datetime.timedelta(hours=24)

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

api = API_Stuff()

# insert historical prices
db = StupidDB(os.path.dirname(os.path.abspath(__file__))+'/config')
res = db.read('pyquant', 'get_update_close_list')
spx_active = True
for r in res:
    close_data = api.yahoo_api_current(r['yahoo_symbol'])
    #close_data = api.yahoo_api_hist(r['yahoo_symbol'], today.strftime('%Y-%m-%d'))
    if close_data is None:
        if r['symbol']=='SPX':
            spx_active = False
    else:
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

    # Update previous trading days volume if necessary
    if r['symbol']!='VIX':
        get_volume = db.read_single('pyquant', 'previous_volume', symbol = r['symbol'], date = str(today)[:10])
        if int(get_volume['volume'])==0 or float(get_volume['adj_close'])==0.00:
            vol_data = api.yahoo_api_hist(r['yahoo_symbol'], str(get_volume['close_date'])[:10])
            db.write('pyquant', 'update_prevous_volume',
                volume = vol_data['volume'],
                symbol = r['symbol'],
                close_date = get_volume['close_date'],
                adj_close = vol_data['adj_close']
                )

# If it wasn't a trading day for SPX, then let's not pull the options chain
if spx_active==False:
    sys.exit()

# insert options chain prices
for r in db.read('pyquant', 'get_update_options_list'):
    for rec in api.options_chain_all(r['symbol'], r['include_all_roots']):
        db.write('pyquant', 'update_historical_options_price',
            symbol = r['symbol'],
            option_symbol = rec['option_symbol'],
            trade_date = today.strftime('%Y-%m-%d'),
            description = rec['description'],
            option_type = rec['option_type'],
            strike = rec['strike'],
            bid = rec['bid'],
            ask = rec['ask'],
            open_interest = rec['open_interest'],
            expiration_date = rec['expiration_date']
            )

