import sys
import re
from hashlib import sha1
from datetime import datetime
import logging

from webstore.client import URL as WebStore

from offenesparlament.core import master_data

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

UNIQUE = ['__id__']

def extend_ablaeufe(db, master):
    log.info("Amending ablaeufe ...")
    Ablauf = db['ablauf']
    typen = [(t.get('typ'), t.get('class')) for t in master['ablauf_typ']]
    typen = dict(typen)
    for data in Ablauf:
        data['class'] = typen.get(data.get('typ'))
        Ablauf.writerow(data, unique_columns=UNIQUE)

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    extend_ablaeufe(db, master_data())
