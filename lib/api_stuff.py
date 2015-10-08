import datetime
import json
import requests

class API_Stuff:
    def __init__(self):
        pass

    def google_api_current(self, symbol):
        r = requests.get("http://www.google.com/finance/info?q=NSE:%s" % symbol)
        return json.loads(''.join([x for x in r.text.splitlines() if x not in ('// [', ']')]))

    def yahoo_api_current(self, symbol):
        r = requests.get("http://finance.yahoo.com/webservice/v1/symbols/%s/quote?format=json&view=detail"
            % symbol)
        close_data = json.loads(r.text)
        return {
            'open': round(float(close_data['list']['resources'][0]['resource']['fields']['price']) -
                float(close_data['list']['resources'][0]['resource']['fields']['change']), 2),
            'high': round(float(close_data['list']['resources'][0]['resource']['fields']['day_high']), 2),
            'low': round(float(close_data['list']['resources'][0]['resource']['fields']['day_low']), 2),
            'close': round(float(close_data['list']['resources'][0]['resource']['fields']['price']), 2),
            'volume': int(close_data['list']['resources'][0]['resource']['fields']['volume'])
            }

    def yahoo_api_hist(self, symbol, date):
        date_args = date.split('-')
        year = date_args[0]
        month = "%02d" % (int(date_args[1]) - 1)
        day = date_args[2]
        r = requests.get("http://ichart.finance.yahoo.com/table.csv?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s&g=d&ignore=.csv"
            % (symbol, month, day, year, month, day, year))
        if r.status_code==404:
            return None
        else: # Assume 200??
            close_data = [s for s in r.text.splitlines() if s and not s.isspace()][1].split(",")
            return {
                'open': round(float(close_data[1]), 2),
                'high': round(float(close_data[2]), 2),
                'low': round(float(close_data[3]), 2),
                'close': round(float(close_data[4]), 2),
                'volume': int(close_data[5]),
                'adj_close': round(float(close_data[6]), 2)
                }

    #def option_chain_current(self, symbol):

