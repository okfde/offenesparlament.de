#coding: utf-8
from pprint import pprint
from datetime import datetime
import urlparse
import logging
import re
from lxml import etree

import sqlaload as sl

from offenesparlament.data.lib.retrieval import fetch, _html
from offenesparlament.data.lib.constants import GERMAN_MONTHS
from offenesparlament.data.lib.refresh import check_tags
from offenesparlament.data.lib.pdftoxml import pdftoxml
from offenesparlament.core import etl_engine

log = logging.getLogger(__name__)

INDEX = "http://www.bundestag.de/bundestag/plenum/abstimmung/%s/index.html"
DATE_RE = re.compile(r"Berlin.*den.*(\d{2})[^\d]*(\w{3,4}).*(\d{2})[^\d]*")


def handle_xml(engine, base_data, data):
    doc = etree.fromstring(pdftoxml(data))
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
                        'vote': unicode(field)}
                data.update(base_data)
                sl.upsert(engine, Vote, data, unique=['subject', 'person'])
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
                                         GERMAN_MONTHS[m.group(2)],
                                         m.group(3))
                    date = datetime.strptime(dstr, '%d.%m.%y').isoformat()
            subject = subject.strip()
            if u'Es entfielen auf die Gesetzentwürfe' in subject:
                log.error("Mehrfachabstimmung WTF. Bailing...")
                return
            log.info("Abstimmung: %s", subject)
        else:
            handle_list(page)

def scrape_abstimmung(engine, url, force=False):
    abstimmung = sl.get_table(engine, 'abstimmung')
    sample = sl.find_one(engine, abstimmung, source_url=url)
    response = fetch(url)
    sample = check_tags(sample or {}, response, force)
    
    base_data = {'source_url': url, 
                 'source_etag': sample['source_etag']}
    handle_xml(engine, base_data, response.content)
    return base_data

def scrape_index():
    for year in range(2009, datetime.now().year):
        index_url = INDEX % year
        response, doc = _html(index_url)
        for a in doc.findall('//a'):
            url = urlparse.urljoin(index_url , a.get('href'))
            if url.endswith('.pdf'):
                yield url

