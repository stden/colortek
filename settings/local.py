#ADMINS = (
#    ('Someone', 'someone@gmail.notification.change.it.com'),
#)
#EMAIL_HOST='smtp.mail.ru'
#EMAIL_HOST_USER='uzevezu'
#EMAIL_HOST_PASSWORD='Jol480b170'
#EMAIL_PORT = 25
SERVER_EMAIL='uzevezu@uzevezu.ru'
#EMAIL_USE_TLS = True
EMAIL_FROM='Uzevezu <uzevezu@uzevezu.ru>'
DI_SMS_PASSWORD = '1233123'
SMS_DIRECT_PASSWORD = '123'
SMS_TWO_PASSWORD = '123'
DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'colortek',                      # Or path to database file if using sqlite3.
        'USER': 'colortek',                      # Not used with sqlite3.
        'PASSWORD': 'a8b6083d4f',
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}
DEBUG=False
APACHE=True # apache is shit
DEFAULT_TEMPLATE='base_web.html'
DO_SECRET='bf43f9283a1211e2a7a9002608f6ce38'
DI_SMS_PASSWORD='9yqe6e'
SITE_URL='http://uzevezu.ru'
SITE_SHORT_URL='uzevezu.ru'
RESOURCE_NAME='Uzevezu'
SERVICE_NAME=RESOURCE_NAME
VK_API_KEY=3359713
ITEMS_ON_PAGE=21
ALLOW_SUPERUSER_VOTE=True

# COMPRESS_ENABLED = DEBUG


# THUMBNAIL_DEBUG=False
# THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'