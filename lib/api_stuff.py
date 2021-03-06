from config import Config
import datetime
import json
import requests
import os
import sys
import xmltodict

"""
Looks like the Tradier API call for /v1/markets/options/chains (sandbox version) is up-to-date by 1:50pm'ish PT
"""

class API_Stuff:
    def __init__(self):
        # Let's get the app's config
        config_file = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'/config.txt'
        self.cfg = Config(config_file)

        # Trademonster authorization object
        self.tm_auth = None
        self.tm_headers = None

    def google_api_current(self, symbol):
        r = requests.get("http://www.google.com/finance/info?q=NSE:%s" % symbol)
        return json.loads(''.join([x for x in r.text.splitlines() if x not in ('// [', ']')]))

    # All values (including volume) are present by at least 3:30pm
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

    # Would like to use tradier, but for some reason they don't have volume and adj_close
    def quote_hist(self, symbol, date):
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

    # Retrieve all options chains for all available expiration dates
    def options_chain_all(self, symbol, include_all_roots='N'):
        headers = {
            'Authorization': 'Bearer %s' % self.cfg.tradier_token,
            'Content-type': 'application/json'
            }
        if include_all_roots == 'Y':
            r = requests.get(
                'https://%s/v1/markets/options/expirations?symbol=%s&includeAllRoots=true' % (self.cfg.tradier_api, symbol),
                headers=headers
                )
        else:
            r = requests.get(
                'https://%s/v1/markets/options/expirations?symbol=%s' % (self.cfg.tradier_api, symbol),
                headers=headers
                )
        option_exp = xmltodict.parse(r.text)
        options_chain = list()
        for exp_date in option_exp['expirations']['date']:
            r = requests.get(
                'https://%s/v1/markets/options/chains?symbol=%s&expiration=%s' % (self.cfg.tradier_api, symbol, exp_date),
                headers=headers
                )
            chain_data = xmltodict.parse(r.text)
            for strike in chain_data['options']['option']:
                options_chain.append({
                    'symbol': symbol,
                    'option_symbol': strike['symbol'],
                    'description': strike['description'],
                    'option_type': strike['option_type'],
                    'strike': strike['strike'],
                    'bid': strike['bid'],
                    'ask': strike['ask'],
                    'open_interest': strike['open_interest'],
                    'expiration_date': strike['expiration_date']
                    })
        return options_chain
            
    def options_chain(self, symbol, exp_date):
        headers = {
            'Authorization': 'Bearer %s' % self.cfg.tradier_token,
            'Content-type': 'application/json'
            }
        r = requests.get(
            'https://%s/v1/markets/options/chains?symbol=%s&expiration=%s' % (self.cfg.tradier_api, symbol, exp_date),
            headers=headers
            )
        res = xmltodict.parse(r.text)
        options_chain = list()
        for strike in res['options']['option']:
            options_chain.append({
                'symbol': symbol,
                'option_symbol': strike['symbol'],
                'description': strike['description'],
                'option_type': strike['option_type'],
                'strike': strike['strike'],
                'bid': strike['bid'],
                'ask': strike['ask'],
                'open_interest': strike['open_interest'],
                'expiration_date': strike['expiration_date']
                })
        return options_chain

    def quote(self, symbol):
        headers = {
            'Authorization': 'Bearer %s' % self.cfg.tradier_token,
            'Content-type': 'application/json'
            }
        r = requests.get(
            #'https://%s/v1/markets/timesales?symbol=%s' % (self.cfg.tradier_api, symbol),
            'https://%s/v1/markets/quotes?symbols=%s' % (self.cfg.tradier_api, symbol),
            #'https://%s/v1/markets/history?symbol=%s' % (self.cfg.tradier_api, symbol),
            #'https://%s/v1/markets/timesales?symbol=%s' % (self.cfg.tradier_api, symbol),
            headers=headers
            )
        res = xmltodict.parse(r.text)
        quote = res['quotes']['quote']
        if quote['open'] is None:
            return None
        else:
            return {
                'open': float(quote['open']),
                'high': float(quote['high']),
                'low': float(quote['low']),
                'close': float(quote['last']),
                'volume': int(quote['volume'])
                }

    def get_positions(self):
        #headers = {
        #    #'Authorization': 'Bearer %s' % self.cfg.tradier_token,
        #    'Content-type': 'application/xml'
        #    }
        if self.tm_auth is None:
            self._trademonster_auth()

        payload = """<getPositionsDetailNew>
<accountIds>%s</accountIds>
<accountId>%s</accountId>
<loadSimulated>true</loadSimulated>
<requireStrategy>false</requireStrategy>
<suppressOpenPnL>true</suppressOpenPnL>
<suppressDefaults>true</suppressDefaults>
<filter />
</getPositionsDetailNew>""" % (self.tm_auth['userId'], self.tm_auth['userId'])
        print "...lbah..."
        print payload
        print "...lbah..."
        self.tm_headers['Content-Length'] = len(payload)
        print json.dumps(self.tm_headers, indent=2)
        print "...lbah..."
        r = requests.post(
            'https://%s/services/clientPositionService' % (self.cfg.trademonster_api),
            data=payload,
            headers=self.tm_headers
            )
        from pprint import pprint
        pprint (vars(r))
        print "...lbah..."
        print json.dumps(self.tm_auth, indent=2)
        print "...lbah..."
        print r.text

    def _trademonster_auth(self):
        self.tm_auth = dict()
        headers = {
            'Host': self.cfg.public_ip,
            'Authorization': 'Bearer %s' % self.cfg.tradier_token,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8 Accept-Encoding: gzip,deflate,sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'alphatradr-pyquant/0.0.1'
            }
        r = requests.post(
            'https://%s/j_acegi_security_check' % (self.cfg.trademonster_api),
            data='j_username=%s&j_password=%s' % (self.cfg.oh_username, self.cfg.oh_password),
            headers=headers
            )
        if r.status_code==200:
            response = json.loads(r.text)
            self.tm_auth['session_id'] = response['sessionId']
            self.tm_auth['token'] = response['token']
            self.tm_auth['userId'] = response['userId']
            self.tm_auth['userPermission'] = response['userPermission']
            self.tm_auth['userResources'] = response['userResources']
            self.tm_headers = headers
            self.tm_headers['Cookie'] = 'JSESSIONID=%s' % self.tm_auth['session_id']
