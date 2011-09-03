# coding: utf-8
from itertools import count
from urllib2 import urlopen, HTTPError
from pprint import pprint
import re
import sys

from webstore.client import URL as WebStore

from offenesparlament.core import master_data
from offenesparlament.transform.namematch import match_speaker, make_prints

TEST_URL = "http://www.bundestag.de/dokumente/protokolle/plenarprotokolle/plenarprotokolle/17121.txt"

URL = "http://www.bundestag.de/dokumente/protokolle/plenarprotokolle/plenarprotokolle/%s%03.d.txt"

CHAIRS = [u'Vizepräsidentin', u'Vizepräsident', u'Präsident']

BEGIN_MARK = re.compile('Beginn: \d{1,2}.\d{1,2} Uhr')
END_MARK = re.compile('\(Schluss: \d{1,2}.\d{1,2} Uhr\).*')
SPEAKER_MARK = re.compile('  (.{5,140}):\s*$')
TOP_MARK = re.compile('  Ich rufe (den|die) (Tagesordnungs|Zusatzpunkte).*auf.*:\s$')
POI_MARK = re.compile('\((.*)\)\s*$')

class SpeechParser(object):

    def __init__(self, master, db, fh):
        self.db = db
        self.master = master
        self.fh = fh
        self.prints = make_prints(db)

    def identify_speaker(self, match):
        return match_speaker(self.master, match, self.prints)
    
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
                fingerprint = self.identify_speaker(speaker)
            yield (speaker_name, fingerprint, text)

    def __iter__(self):
        self.in_session = False
        sequence = [0]
        speaker = None
        fingerprint = None
        chair_ = [False]
        text = []
        def emit():
            data = {
                'speaker': speaker,
                'type': 'chair' if chair_[0] else 'speech',
                'fingerprint': fingerprint,
                'sequence': sequence[0],
                'text': "\n\n".join(text).strip()
                }
            sequence[0] += 1
            chair_[0] = False
            _ = [text.pop() for i in xrange(len(text))]
            return data

        for line in self.fh:
            line = line.decode('latin-1')
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
            
            m = SPEAKER_MARK.match(line)
            if is_top is False and m is not None:
                if speaker is not None:
                    data = emit()
                    if len(data['text'].strip()):
                        yield data
                speaker = m.group(1)
                fingerprint = self.identify_speaker(speaker)
                role = line.strip().split(' ')[0]
                chair_[0] = role in CHAIRS
                continue
            
            m = POI_MARK.match(line)
            if m is not None:
                data = emit()
                if len(data['text'].strip()):
                    yield data
                for _speaker, _fingerprint, _text in self.parse_pois(m.group(1)):
                    yield {
                        'speaker': _speaker,
                        'type': 'poi',
                        'fingerprint': _fingerprint,
                        'sequence': sequence[0],
                        'text': _text
                            }
                    sequence[0] += 1
                continue
            
            text.append(line)
        yield emit()

def load_transcript(db, master, wp, session):
    url = URL % (wp, session)
    fh = urlopen(url)
    print "URL", url
    Speech = db['speech']
    for contrib in SpeechParser(master_data(), db, fp):
        contrib['sitzung'] = session
        contrib['wahlperiode'] = wp
        contrib['source_url'] = url
        Speech.writerow(contrib, 
                unique_columns=['source_url', 'sequence'])
    fh.close()

def load_transcripts(db, master):
    for i in count(33):
        try:
            load_transcript(db, master, 17, i)
        except HTTPError:
            pass

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    fp = urlopen(TEST_URL)

    load_transcripts(db, master_data())

    #sp = SpeechParser(master_data(), db, fp)
    #for l in sp:
    #    pprint(l)
        #pass
