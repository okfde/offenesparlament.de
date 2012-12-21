
class Unmodified(Exception):
    pass

def check_tags(data, response, force):
    if not isinstance(data, dict):
        return data
    source_etag = data.get('source_etag')
    etag = response.headers.get('etag')
    if not force and \
        source_etag and source_etag == etag:
        raise Unmodified()
    data['source_etag'] = etag
    return data




