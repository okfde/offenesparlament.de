import sys, re
import logging
from pprint import pprint

from offenesparlament.core import db, solr
from offenesparlament.model import Gremium, Person, Rolle, \
        Wahlkreis, Ablauf, \
        Position, Beschluss, Beitrag, Zuweisung, Referenz, Dokument, \
        Schlagwort, Sitzung, Debatte, Zitat

from offenesparlament.model.util import convert_data_to_index
from offenesparlament.model.indexer import get_indexer

log = logging.getLogger(__name__)

def index_class(cls, step=1000):
    indexer = get_indexer()
    log.info("Indexing %s", cls.__name__)
    for obj in cls.query.yield_per(step):
        indexer.add(obj)
    indexer.flush()

def index():
    _solr = solr()
    #_solr.delete_query("*:*")
    index_class(Person)
    #index_class(Gremium)
    #index_class(Position)
    #index_class(Dokument)
    index_class(Ablauf)
    index_class(Sitzung)
    index_class(Debatte)
    index_class(Zitat)

if __name__ == '__main__':
    index()
