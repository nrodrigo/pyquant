import requests
import pprint
import json
import sys
from lib.config import Config

pp = pprint.PrettyPrinter(indent=4)
cfg = Config()

headers = {
    'Content-Type': 'application/xml'
}
r = requests.post(
    "https://www.trademonster.com/j_acegi_security_check",
    data={'j_username': cfg.oh_username, 'j_password': cfg.oh_password},
    headers=headers
    )

response = json.loads(r.text)
status_code = r.status_code
reason = r.reason

token = response['token']
print json.dumps(response, indent=4)
print json.dumps(r.cookies['monster'], indent=4)

account_id = response['userId']
print "account_id: %s" % account_id

sys.exit()

headers = {
    'Content-Type': 'application/xml',
    'token': response['token'],
    'JSESSIONID': response['sessionId']
}
xml = """<getPositionsDetailNew>
<accountIds>%s</accountIds>
<accountId>%s</accountId>
<loadSimulated>true</loadSimulated>
<requireStrategy>false</requireStrategy>
<suppressOpenPnL>true</suppressOpenPnL>
<suppressDefaults>true</suppressDefaults>
<filter />
</getPositionsDetailNew>""" % (account_id, account_id)

r = requests.post(
    "https://www.trademonster.com/services/clientPositionService",
    data = xml,
    headers = headers)

#r = requests.post(
#    "https://www.trademonster.com/services/customerWidgetService",
#    data = {
#        'accountIds': account_id,
#        'accountId': account_id,
#        'loadSimulated': 'true',
#        'requireStrategy': 'false',
#        'suppressOpenPnL': 'true',
#        'suppressDefaults': 'true'
#        }
#    )

print json.dumps(r.text, indent=4)
