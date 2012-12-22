import logging
import urllib
import os

import sqlaload as sl

from offenesparlament.core import archive_path

log = logging.getLogger(__name__)

def load_document(link):
    log.info("Fetching %s...", link)
    destination = archive_path('documents', link.split('/dip21/')[-1])
    try:
        if os.path.isfile(destination):
            return
        temp = destination + '.tmp'
        urllib.urlretrieve(link, temp)
        os.rename(temp, destination)
    except Exception, ex:
        log.exception(ex)

def load_documents(engine):
    refs = sl.get_table(engine, 'referenz')
    for ref in sl.distinct(engine, refs, 'link'):
        link = ref.get('link')
        if link is None:
            continue
        load_document(link)

