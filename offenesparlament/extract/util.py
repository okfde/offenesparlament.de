import logging
from Queue import Queue
from threading import Thread
from lxml import etree, html
from StringIO import StringIO
import requests
import time

log = logging.getLogger(__name__)
UA = 'OPA // Neuer Scraper; weniger Zugriffe - bitte nicht blocken! <friedrich.lindenberg@okfn.org>'

def threaded(items, func, num_threads=5, max_queue=200):
    def queue_consumer():
        while True:
            item = queue.get(True)
            try:
                func(item)
            except Exception, e:
                log.exception(e)
            queue.task_done()

    queue = Queue(maxsize=max_queue)

    for i in range(num_threads):
        t = Thread(target=queue_consumer)
        t.daemon = True
        t.start()

    for item in items:
        queue.put(item, True)

    queue.join()


def fetch(url, timeout=2.0, keep_alive=True):
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
                headers={'user-agent': UA},
                timeout=timeout,
                config={'max_retries': 2,
                        'keep_alive': keep_alive},
                proxies=proxies,
                verify=False)
            return body.content
        except requests.exceptions.Timeout:
            #keep_alive = False
            time.sleep(1)
        except Exception, e:
            #keep_alive = False
            logging.exception(e)
            time.sleep(1)


def fetch_stream(url, timeout=2.0):
    data = fetch(url, timeout=timeout)
    if data is None:
        return None
    return StringIO(data)


def _xml(url, timeout=2.0):
    d = fetch_stream(url, timeout=timeout)
    return etree.parse(d) if d is not None else d


def _html(url, timeout=2.0):
    d = fetch_stream(url, timeout=timeout)
    return html.parse(d) if d is not None else d

