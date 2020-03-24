import requests
import json
import logging
from creds import SLACK_WEBHOOKURL

HEADERS = {
    'Content-type': 'application/json'
}


def slacker(webhook_url=SLACK_WEBHOOKURL):
    def slackit(msg):
        logging.info('Sending {msg} to slack'.format(msg=msg))
        payload = { 'text': msg }
        return requests.post(webhook_url, headers=HEADERS, data=json.dumps(payload))
    return slackit