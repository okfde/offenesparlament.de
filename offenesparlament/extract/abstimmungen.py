#coding: utf-8
from lxml import etree, html
from pprint import pprint
import urllib, urlparse
import subprocess
import logging
import sys
import tempfile

from webstore.client import URL as WebStore

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

INDEX = "http://www.bundestag.de/bundestag/plenum/abstimmung/index.html"

def pdftoxml(file_path):
    process = subprocess.Popen(['pdftohtml', '-xml', '-noframes', '-stdout',
            file_path], shell=False, stdout=subprocess.PIPE)
    return process.stdout.read()

def handle_xml(xml, db):
    doc = etree.fromstring(xml)
    Vote = db['abstimmung']
    subject = ''
    def handle_list(page):
        texts = page.findall('text')[2:]
        fraktion = texts[0].text.replace(u"ÜNDNIS`", "")
        columns = texts[1:6]
        columns = [(int(c.get('left')), c.text) for c in columns]
        texts = texts[7:]
        for i, t in enumerate(texts[::2]):
            if t.text.strip() == 'Summe':
                break
            person = t.text + ' ' + fraktion
            vote = texts[i*2+1]
            l, match = min(columns, key=lambda (l, t): abs(l-int(vote.get('left'))))
            data = {'subject': subject, 
                    'person': person, 
                    'vote': match}
            Vote.writerow(data, unique_columns=['subject', 'person'])

    for page in doc.findall(".//page"):
        if page.get('number') == "1":
            for t in page.findall('text'):
                if int(t.get('left')) < 120:
                    subject += t.text + "\n"
            subject = subject.strip()
            if u'Es entfielen auf die Gesetzentwürfe' in subject:
                log.error("Mehrfachabstimmung WTF. Bailing...")
                return
            log.info("Abstimmung: %s", subject)
        else:
            handle_list(page)

def load_vote(url, db):
    fh, path = tempfile.mkstemp('.pdf')
    urllib.urlretrieve(url, path)
    xml = pdftoxml(path)
    handle_xml(xml, db)

def load_index(db):
    doc = html.parse(INDEX)
    for a in doc.findall('//ul[@class="standardLinkliste"]//a'):
        url = urlparse.urljoin(INDEX, a.get('href'))
        load_vote(url, db)

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    load_index(db)

