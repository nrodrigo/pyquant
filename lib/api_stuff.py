import requests
import json

class API_Stuff:
    def __init__(self):
        pass

    def google_api_current(self, symbol):
        r = requests.get("http://www.google.com/finance/info?q=NSE:%s" % symbol)
        return json.loads(''.join([x for x in r.text.splitlines() if x not in ('// [', ']')]))

    def yahoo_api_current(self, symbol):
        r = requests.get("http://finance.yahoo.com/webservice/v1/symbols/%s/quote?format=json&view=detail"
            % symbol)
        return json.loads(r.text)

