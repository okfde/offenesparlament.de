# coding: utf-8
import logging
from itertools import count
from pprint import pprint
import re

import sqlaload as sl

from offenesparlament.data.lib.constants import SPEAKER_STOPWORDS, CHAIRS
from offenesparlament.data.lib.retrieval import fetch, fetch_stream
from offenesparlament.data.lib.refresh import check_tags
from offenesparlament.data.lib.reference import resolve_person, \
    BadReference, InvalidReference

log = logging.getLogger(__name__)

URL = "http://www.bundestag.de/dokumente/protokolle/plenarprotokolle/plenarprotokolle/%s%03.d.txt"
BEGIN_MARK = re.compile('Beginn: [X\d]{1,2}.\d{1,2} Uhr')
END_MARK = re.compile('\(Schluss: \d{1,2}.\d{1,2} Uhr\).*')
SPEAKER_MARK = re.compile('  (.{5,140}):\s*$')
TOP_MARK = re.compile('.*(rufe.*die Frage|zur Frage|Tagesordnungspunkt|Zusatzpunkt).*')
POI_MARK = re.compile('\((.*)\)\s*$', re.M)


class SpeechParser(object):

    def __init__(self, fh):
        self.fh = fh
        self.missing_recon = False

    def parse_pois(self, group):
        for poi in group.split(' - '):
            text = poi
            speaker_name = None
            fingerprint = None
            sinfo = poi.split(': ', 1)
            if len(sinfo) > 1:
                speaker_name = sinfo[0]
                text = sinfo[1]
                speaker = speaker_name.replace('Gegenruf des Abg. ', '')
                try:
                    fingerprint = resolve_person(speaker)
                except InvalidReference:
                    pass
                except BadReference:
                    self.missing_recon = True
            yield (speaker_name, fingerprint, text)

    def __iter__(self):
        self.in_session = False
        speaker = None
        fingerprint = None
        chair_ = [False]
        text = []

        def emit(reset_chair=True):
            data = {
                'speaker': speaker,
                'type': 'chair' if chair_[0] else 'speech',
                'fingerprint': fingerprint,
                'text': "\n\n".join(text).strip()
                }
            if reset_chair:
                chair_[0] = False
            [text.pop() for i in xrange(len(text))]
            return data

        for line in self.fh:
            line = line.decode('latin-1')
            line = line.replace(u'\u2014', '-')
            line = line.replace(u'\x96', '-')
            if not self.in_session and BEGIN_MARK.match(line):
                self.in_session = True
                continue
            elif not self.in_session:
                continue

            if END_MARK.match(line):
                return

            if not len(line.strip()):
                continue

            is_top = False
            if TOP_MARK.match(line):
                is_top = True

            has_stopword = False
            for sw in SPEAKER_STOPWORDS:
                if sw.lower() in line.lower():
                    has_stopword = True

            m = SPEAKER_MARK.match(line)
            if m is not None and not is_top and not has_stopword:
                if speaker is not None:
                    yield emit()
                _speaker = m.group(1)
                role = line.strip().split(' ')[0]
                try:
                    fingerprint = resolve_person(_speaker)
                    speaker = _speaker
                    chair_[0] = role in CHAIRS
                    continue
                except InvalidReference:
                    pass
                except BadReference:
                    self.missing_recon = True

            m = POI_MARK.match(line)
            if m is not None:
                if not m.group(1).lower().strip().startswith('siehe'):
                    yield emit(reset_chair=False)
                    for _speaker, _fingerprint, _text in self.parse_pois(m.group(1)):
                        yield {
                            'speaker': _speaker,
                            'type': 'poi',
                            'fingerprint': _fingerprint,
                            'text': _text
                                }
                    continue

            text.append(line)
        yield emit()

def url_metadata(url):
    fname = url.rsplit('/')[-1]
    return int(fname[:2]), int(fname[2:5])

def scrape_transcript(engine, url, force=False):
    wp, session = url_metadata(url)
    table = sl.get_table(engine, 'speech')
    sample = sl.find_one(engine, table, source_url=url, matched=True)
    response, sio = fetch_stream(url)
    sample = check_tags(sample or {}, response, force)
    base_data = {'source_url': url, 
                 'sitzung': session,
                 'wahlperiode': wp,
                 'matched': False,
                 'loaded': False,
                 'source_etag': sample['source_etag']}
    log.info("Loading transcript: %s/%s, from %s" , wp, session, url)
    seq = 0
    parser = SpeechParser(sio)
    for contrib in parser:
        if not len(contrib['text'].strip()):
            continue
        contrib.update(base_data)
        contrib['sequence'] = seq
        sl.upsert(engine, table, contrib, 
                  unique=['source_url', 'sequence'])
        seq += 1
    if not parser.missing_recon:
        sl.upsert(engine, table, {
                    'matched': True,
                    'source_url': url,
            }, unique=['source_url'])
    else:
        raise InvalidReference()
    return base_data


def scrape_index(wp=17):
    for i in count(33):
        url = URL % (wp, i)
        response = fetch(url)
        if response.status_code != 200: 
            if i > 180:
                return
            continue
        yield url
