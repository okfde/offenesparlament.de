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
        fraktion = texts[0].xpath("string()").replace(u"ÜNDNIS`", "")
        columns = [c.xpath("string()") for c in texts[1:6]]
        texts = texts[7:]
        for i, t in enumerate(texts[::6]):
            if t.xpath('string()').strip() == 'Summe':
                break
            person = t.xpath("string()") + ' ' + fraktion
            ts = [c.xpath("string()") for c in texts[i*6+1:i*6+6]]
            for col, val in zip(columns, ts):
                if val == 'X':
                    data = {'subject': subject, 
                            'person': person, 
                            'vote': col}
                    Vote.writerow(data, unique_columns=['subject', 'person'],
                                  bufferlen=2000)

    for page in doc.findall(".//page"):
        if page.get('number') == "1":
            for t in page.findall('text'):
                if int(t.get('left')) < 120:
                    subject += t.xpath("string()") + "\n"
            subject = subject.strip()
            if u'Es entfielen auf die Gesetzentwürfe' in subject:
                log.error("Mehrfachabstimmung WTF. Bailing...")
                return
            log.info("Abstimmung: %s", subject)
        else:
            handle_list(page)

    Vote.flush()

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

