from pprint import pprint
from itertools import count
import logging
from datetime import datetime
from lxml import html

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.load.fetch import _html

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

WEBTV_BASE = 'http://webtv.bundestag.de/iptv/player/macros/bttv/list.html?pageOffset=0&pageLength=20000&sort=2&lastName=&firstName=&fraction=&meetingNumber=%s&period=%s&startDay=&endDay=&topic=&submit=Suchen'
WEBTV_SPEECHES = 'http://webtv.bundestag.de/player/macros/bttv/contribution_list.html?meetingPeriod=%s&meetingNumber=%s&agendaItemId=%s'


def load_speeches(engine, data):
    url = WEBTV_SPEECHES % (data['wp'], data['session'], data['item_id'])
    doc = _html(url)
    rows = doc.findall('//tr')
    table = sl.get_table(engine, 'webtv')
    for i, row in enumerate(rows):
        if i % 4 != 0:
            continue
        data['speaker'] = row.xpath('string()').strip()
        if isinstance(data['speaker'], str):
            data['speaker'] = data['speaker'].encode('latin-1').decode('utf-8')
        data['speech_id'] = rows[i + 2].find('.//a').get('href').split('=')[-1]
        sl.upsert(engine, table, data, ['speech_id'])
        pprint(data)


def load_agenda(engine, wp, session):
    url = WEBTV_BASE % (session, wp)
    doc = _html(url, timeout=4.0)
    if doc is None:
        return False
    table = doc.find('//div[@class="meetingTable"]/table')
    if table is None:
        return False
    data = {'wp': wp, 'session': session}
    rows = table.findall('.//tr')
    for i, row in enumerate(rows):
        tds = row.findall('td')
        session_name = tds[0].xpath('string()').strip()
        if len(session_name):
            data['session_name'] = session_name
            bla, date = session_name.rsplit(' ', 1)
            data['session_url'] = url
            data['session_date'] = datetime.strptime(date,
                    "%d.%m.%Y").isoformat()
        anchor = tds[0].find('a')
        if anchor is not None:
            data['item_id'] = anchor.get('name')
            key, label = tds[1].xpath('string()').strip().split('\n', 1)
            data['item_key'] = key.strip().replace('TOP:', '').strip()
            data['item_label'] = label.strip()

            text = rows[i + 1].find('.//span[@class="hiddenTopText"]')
            data['item_description'] = text.xpath('string()').strip()
            load_speeches(engine, data.copy())
    return True


def load_sessions(engine, wp='17'):
    table = sl.get_table(engine, 'webtv')
    for i in count(1):
        i = str(i)
        if sl.find_one(engine, table, wp=wp, session=i):
            continue
        if not load_agenda(engine, wp, i):
            return
