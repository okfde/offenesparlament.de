from pprint import pprint
import re
import logging

import sqlaload as sl

log = logging.getLogger(__name__)


def get_agenda(engine, wp, session):
    return list(sl.find(engine, sl.get_table(engine, 'webtv'),
            wp=wp, session=session, order_by='speech_id'))


def get_transcript(engine, wp, session):
    speeches = []
    for speech in sl.find(engine, sl.get_table(engine, 'speech'),
        order_by='sequence', wahlperiode=wp, sitzung=session,
        matched=True):
        if speech['type'] == 'poi':
            continue
        seg = (speech['sequence'], speech['fingerprint'])
        speeches.append(seg)
    return speeches


def score_alignment(aligned):
    if not len(aligned):
        return 0
    score = len([a for a in aligned if \
        a.get('transcript_fp')==a.get('agenda_fp')])
    return float(score) / len(aligned)


def align_section(transcript, agenda):
    aligned = []
    index = 0
    for sequence, tr_fp in transcript:
        if len(agenda) > index+1 and \
            tr_fp == agenda[index+1].get('fingerprint'):
            index += 1
        speech = agenda[index]
        aligned.append({
            'item_id': speech.get('item_id'),
            'speech_id': speech.get('speech_id'),
            'agenda_fp': speech.get('fingerprint'),
            'sequence': sequence,
            'transcript_fp': tr_fp
            })
    return aligned


def agenda_seek(agenda, cut, offset):
    end = offset
    while True:
        if end >= len(agenda):
            break
        speech = agenda[end]
        if speech.get('speech_id') == cut.get('speech_id'):
            break
        end += 1
    return agenda[offset:end+1]

def transcript_seek(transcript, cut, offset):
    end = offset
    while True:
        if transcript[end][0] >= cut.get('sequence'):
            break
        end += 1
    return transcript[offset:end-1]

def get_alignment(engine, wp, session):
    agenda_speeches = get_agenda(engine, wp, session)
    transcript_speeches = get_transcript(engine, wp, session)
    
    try:
        cuts = list(sl.find(engine, sl.get_table(engine, 'alignments'),
                wp=str(wp), session=str(session), order_by='sequence'))
    except KeyError:
        cuts = []
    
    alignment = []
    tr_offset = 0
    ag_offset = 0
    for cut in cuts:
        tr_speeches = transcript_seek(transcript_speeches, 
                cut, tr_offset)
        tr_current = len(tr_speeches) + 1
        tr_offset = tr_offset + tr_current

        ag_speeches = agenda_seek(agenda_speeches, cut, ag_offset)
        ag_offset = ag_offset + len(ag_speeches) - 1
        
        section = align_section(tr_speeches, ag_speeches)
        alignment.extend(section)

        data = {
                'item_id': cut.get('item_id'),
                'speech_id': cut.get('speech_id'),
                'sequence': cut.get('sequence'),
                'agenda_fp': ag_speeches[-1].get('fingerprint'),
                'transcript_fp': transcript_speeches[tr_current][1]
                }
        alignment.append(data)

    section = align_section(transcript_speeches[tr_offset:],
                            agenda_speeches[ag_offset:])
    alignment.extend(section)
    return score_alignment(alignment), alignment

def merge_speech(engine, wp, session):
    log.info("Merging media + transcript: %s/%s" % (wp, session))
    score, alignment = get_alignment(engine, wp, session)
    log.info("Matching score: %s", score)
    agenda = get_agenda(engine, wp, session)
    agenda = dict([(a['item_id'], a) for a in agenda])
    alignment = dict([(a['sequence'], a) for a in alignment])
    item = None
    table = sl.get_table(engine, 'webtv_speech')
    for speech in sl.find(engine, sl.get_table(engine, 'speech'),
        order_by='sequence', wahlperiode=wp, sitzung=session,
        matched=True):
        sequence = speech['sequence']
        item = alignment.get(sequence, item)
        data = agenda.get(item['item_id']).copy()
        del data['id']
        data['sequence'] = sequence
        sl.upsert(engine, table, data,
                  unique=['wp', 'session', 'sequence'])

