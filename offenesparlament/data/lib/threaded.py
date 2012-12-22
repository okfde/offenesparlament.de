from Queue import Queue
from threading import Thread
import logging

log = logging.getLogger(__name__)

def unthreaded(items, func):
    """ Debug placeholder. """
    for item in items:
        func(item)

def _threaded(items, func, num_threads=5, max_queue=200):
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

def process(engine, indexer, proc, force=False, threaded=False):
    func = lambda url: proc['handler'](engine, indexer, url, \
            force=force)
    processor = _threaded if threaded else unthreaded
    processor(proc['generator'](), func)

