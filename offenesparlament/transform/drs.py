import sys
import logging
from pprint import pprint

from webstore.client import URL as WebStore

from offenesparlament.core import master_data
from offenesparlament.transform.namematch import match_speaker, make_prints

log = logging.getLogger(__name__)

import re

def drucksachen(text, wahlperiode=17):
    pat = r"(%s/\d{1,6}(\s*\(.{1,10}\))?)" % wahlperiode
    for drs, sufx in re.findall(pat, text):
        yield drs

def _foo(db, master):
    for subj in db['abstimmung'].distinct('subject'):
        print list(drucksachen(subj['subject']))

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    _foo(db, master_data())


