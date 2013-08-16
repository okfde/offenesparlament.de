import logging
from lxml import etree, html
from StringIO import StringIO
import requests
import time

log = logging.getLogger(__name__)

req_log = logging.getLogger('requests')
req_log.setLevel(logging.WARN)

UA = 'OffenesParlament.de // <friedrich@pudo.org>'

def fetch(url, timeout=10.0, keep_alive=True):
    #url = url.replace('http://', 'https://')
    for x in range(15):
        try:
            from offenesparlament.core import app
            #print app.config.get('HTTP_PROXY')
            proxies = {
                'http': app.config.get('HTTP_PROXY'),
                'https': app.config.get('HTTP_PROXY')
                }
            body = requests.get(url, 
                headers={'User-Agent': UA},
                timeout=timeout,
                proxies=proxies,
                verify=False)
            return body
        except requests.exceptions.Timeout:
            #keep_alive = False
            time.sleep(1)
        except Exception, e:
            #keep_alive = False
            logging.exception(e)
            time.sleep(1)


def fetch_stream(url, timeout=10.0):
    response = fetch(url, timeout=timeout)
    if response is None:
        return None, None
    return response, StringIO(response.content)


def _xml(url, timeout=2.0):
    response, d = fetch_stream(url, timeout=timeout)
    doc = etree.parse(d) if d is not None else d
    return response, doc


def _html(url, timeout=2.0):
    response, d = fetch_stream(url, timeout=timeout)
    doc = html.parse(d) if d is not None else d
    return response, doc

