DEBUG = True
SECRET_KEY = 'no'


SQLALCHEMY_DATABASE_URI = 'sqlite:///parlament.db'

# Network = 193.17.224.0/19
# Usable IPs = 193.17.224.1 to 193.17.255.254 for 8190
# Broadcast = 193.17.255.255
# Netmask = 255.255.224.0
# Wildcard Mask = 0.0.31.255

SOLR_URL = 'http://127.0.0.1:8983/solr/parlament'
ETL_URL = 'sqlite:///etl.db'
STAGING_URL = 'http://pudo:bla@localhost:5000/pudo/parlament'
MASTER_URL = 'http://821e7b69-669b-4bd3-aa13-99b93f3a8ddf@webstore.thedatahub.org/pudo/parlamaster'
FLATPAGES_ROOT = 'pages'
