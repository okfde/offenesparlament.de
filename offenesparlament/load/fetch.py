from lxml import etree, html
from StringIO import StringIO
import requests
import logging
import uuid, time

log = logging.getLogger(__name__)

def fetch(url):
    url = url.replace('http://', 'https://')
    for x in range(10):
        try:
            body = requests.get(url, 
                headers={'user-agent': str(uuid.uuid4())},
                timeout=2.0,
                config={'max_retries': 10},
                verify=False)
            return body.content
        except requests.exceptions.Timeout:
            time.sleep(1)
        except Exception, e:
            logging.exception(e)
            time.sleep(1)

def _xml(url):
    body = StringIO(fetch(url))
    return etree.parse(body)

def _html(url):
    body = StringIO(fetch(url))
    return html.parse(body)


