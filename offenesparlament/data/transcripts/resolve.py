#coding: utf-8
import sys
import logging

import sqlaload as sl

from offenesparlament.data.lib.reference import resolve_person, \
    BadReference, InvalidReference
from offenesparlament.data.lib.text import speaker_name_transform

log = logging.getLogger(__name__)


def speakers_webtv(engine, wp, session):
    table = sl.get_table(engine, 'webtv')
    for speech in sl.distinct(engine, table, 'speaker',
            wp=wp, session=session):
        if speech['speaker'] is None:
            continue
        speaker = speaker_name_transform(speech['speaker'])
        matched = True
        try:
            fp = resolve_person(speaker)
        except InvalidReference:
            fp = None
        except BadReference:
            fp = None
            matched = False
        sl.upsert(engine, table, {'fingerprint': fp,
                                  'matched': matched,
                                  'speaker': speech['speaker']},
                    unique=['speaker'])


