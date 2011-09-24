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
        texts = page.findall('text')
        header = [c.xpath("string()") for c in texts[:20]]
        if header[1].strip() == 'Seite:':
            col_offset = 3
        else:
            for i, h in enumerate(header):
                if 'Name' in h:
                    col_offset = i
                    break
        fraktion = texts[col_offset-1].xpath("string()")
        fraktion = fraktion.replace(u"ÜNDNIS`", "")
        fraktion = fraktion.replace(u"ÜNDNIS'", "")
        columns = [(int(c.get('left')), c.xpath("string()")) for c in \
                   texts[col_offset:col_offset+6]]
        texts = texts[col_offset+6:]
        name = u''
        print columns
        for i, t in enumerate(texts):
            txt = t.xpath('string()').strip()
            if txt == 'Summe':
                break
            if not len(txt):
                continue
            left, field = min(columns, key=lambda c: abs(int(t.get('left')) - c[0]))
            if 'Name' in field:
                name += ' ' + txt
            if txt == 'X':
                data = {'subject': subject, 
                        'person': name.strip() + ' ' + fraktion, 
                        'vote': field}
                Vote.writerow(data, unique_columns=['subject', 'person'],
                              bufferlen=2000)
                pprint({'person': name.strip() + ' ' + fraktion, 
                        'vote': field})
                name = u''

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
    #xml = open('/Users/fl/20091203_isaf.xml', 'r').read()
    #handle_xml(xml, db)
    #xml = open('/Users/fl/20100617_unifil.xml', 'r').read()
    ##handle_xml(xml, db)

