from StupidDB.stupiddb import StupidDB
from lib.api_stuff import API_Stuff
import json
import sys

def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

api = API_Stuff()

db = StupidDB()
res = db.read('pyquant', 'get_symbols_to_update')
for r in res:
    print json.dumps(api.yahoo_api_current(r['yahoo_symbol']), indent=2)
