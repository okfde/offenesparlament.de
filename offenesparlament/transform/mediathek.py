from pprint import pprint
import sys

from offenesparlament.core import master_data

from webstore.client import URL as WebStore

def extend_speeches(db, master):
    Speech = db['mediathek']
    for speech in Speech:
        for k, v in speech.items():
            if not k.endswith('pdf_url') or v is None:
                continue
            parts = v.split('#P.')
            if len(parts) > 1:
                url, fragment = parts
            else:
                url = v
                fragment = ''
            speech[k + '_plain'] = url
            speech[k + '_pages'] = fragment
        ctx = speech['speech_context']
        if ctx is not None:
            speech['meeting_nr'], text = ctx.split('.', 1)
            text, speech['meeting_date'] = ctx.rsplit('vom ', 1)
        ctx = speech['meeting_context']
        if ctx is not None:
            speech['wahlperiode'], text = ctx.split('.', 1)
    
        if speech['speech_title']:
            print "Speaker", speech['speech_title'].encode('utf-8')
        Speech.writerow(speech, unique_columns=['speech_source_url'])
        #pprint(speech)

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    extend_speeches(db, master_data())
