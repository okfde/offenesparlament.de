DEBUG = True
SECRET_KEY = 'no'

SOLR_URL = 'http://127.0.0.1:8983/solr/parlament'

SQLALCHEMY_DATABASE_URI = 'sqlite:///parlament.db'
ETL_URI = 'sqlite:///etl.db'

# Network = 193.17.224.0/19
# Usable IPs = 193.17.224.1 to 193.17.255.254 for 8190
# Broadcast = 193.17.255.255
# Netmask = 255.255.224.0
# Wildcard Mask = 0.0.31.255

STAGING_URL = 'http://pudo:bla@localhost:5000/pudo/parlament'
MASTER_URL = 'http://pudo:dsn1v@webstore.thedatahub.org/pudo/parlamaster'
FLATPAGES_ROOT = 'pages'
