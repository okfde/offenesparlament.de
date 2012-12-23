import logging
from threading import Lock

from offenesparlament.model.util import convert_data_to_index
from offenesparlament.core import solr

log = logging.getLogger(__name__)

_indexer = None

def get_indexer():
    global _indexer
    if _indexer is None:
        _indexer = BufferedIndexer()
    return _indexer

class BufferedIndexer(object):
    
    def __init__(self, buffer_size=1000):
        self._buffer_size = buffer_size
        self._lock = Lock()
        self._buffer = []
        self._solr = solr()

    def add(self, obj):
        self.add_many([obj])

    def add_many(self, objs):
        temp = []
        for obj in objs:
            data = convert_data_to_index(obj.to_index())
            temp.append(data)
        
        self._lock.acquire()
        try:
            self._buffer.extend(temp)
        finally:
            self._lock.release()

        self.flush(check_overflow=True)       

    def flush(self, check_overflow=False):
        self._lock.acquire()
        try:
            if check_overflow and \
                len(self._buffer) < self._buffer_size:
                return
            if not len(self._buffer):
                return
            log.info("Flushing indexer....")
            self._solr.add_many(self._buffer)
            self._buffer = []
            self._solr.commit()
        finally:
            self._lock.release()

