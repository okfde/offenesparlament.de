#coding: utf-8
from pprint import pprint
from datetime import datetime
import urlparse
import subprocess
import logging
import re
import tempfile
from lxml import etree

import sqlaload as sl
from offenesparlament.load.fetch import fetch, _html
from offenesparlament.core import etl_engine

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

INDEX = "http://www.bundestag.de/bundestag/plenum/abstimmung/%s/index.html"
DATE_RE = re.compile(r"Berlin.*den.*(\d{2})[^\d]*(\w{3,4}).*(\d{2})[^\d]*")

MONTHS = {
    'Jan': 1,
    'Feb': 2,
    'Mrz': 3,
    'Apr': 4,
    'Mai': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9, 
    'Okt': 10,
    'Nov': 11,
    'Dez': 12
    }

def pdftoxml(file_path):
    process = subprocess.Popen(['pdftohtml', '-xml', '-noframes', '-stdout',
            file_path], shell=False, stdout=subprocess.PIPE)
    return process.stdout.read()

def handle_xml(xml, engine, source_url):
    doc = etree.fromstring(xml)
    Vote = sl.get_table(engine, 'abstimmung')
    subject = ''
    date = None
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
        #print columns
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
                field = field.strip().strip('.').strip()
                data = {'subject': unicode(subject), 
                        'person': name.strip() + ' ' + fraktion,
                        'date': unicode(date),
                        'vote': unicode(field),
                        'source_url': source_url}
                sl.upsert(engine, Vote, data, unique=['subject', 'person'])
                #pprint({'person': name.strip() + ' ' + fraktion, 
                #        'vote': field})
                name = u''

    for page in doc.findall(".//page"):
        if page.get('number') == "1":
            for t in page.findall('text'):
                text = t.xpath("string()")
                if int(t.get('left')) < 120:
                    subject += text + "\n"
                m = DATE_RE.match(text)
                if m:
                    dstr = "%s.%s.%s" % (m.group(1),
                                         MONTHS[m.group(2)],
                                         m.group(3))
                    date = datetime.strptime(dstr, '%d.%m.%y').isoformat()
            subject = subject.strip()
            if u'Es entfielen auf die Gesetzentwürfe' in subject:
                log.error("Mehrfachabstimmung WTF. Bailing...")
                return
            log.info("Abstimmung: %s", subject)
        else:
            handle_list(page)

def load_vote(url, engine, incremental=True):
    Vote = sl.get_table(engine, 'abstimmung')
    if incremental and sl.find_one(engine, Vote, source_url=url):
        log.info("%s is done, skipping.", url)
        return
    fh, path = tempfile.mkstemp('.pdf')
    fo = open(path, 'wb')
    fo.write(fetch(url))
    fo.close()
    xml = pdftoxml(path)
    handle_xml(xml, engine, url)

def load_index(engine, incremental=True):
    for year in range(2009, datetime.now().year):
        index_url = INDEX % year
        doc = _html(index_url)
        for a in doc.findall('//a'):
            url = urlparse.urljoin(index_url , a.get('href'))
            if url.endswith('.pdf'):
                load_vote(url, engine, incremental=incremental)

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    load_index(engine)

