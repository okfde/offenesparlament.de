import sys
import logging

from webstore.client import URL as WebStore

from offenesparlament.core import master_data

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

def extend_ablaeufe(db, master):
    log.info("Amending ablaeufe ...")
    Ablauf = db['ablauf']
    typen = [(t.get('typ'), t.get('class')) for t in master['ablauf_typ']]
    typen = dict(typen)
    for data in Ablauf.distinct('typ'):
        klass = typen.get(data.get('typ'))
        Ablauf.writerow({'typ': data.get('typ'),
                         'class': klass}, 
                         unique_columns=['typ'])

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    extend_ablaeufe(db, master_data())
