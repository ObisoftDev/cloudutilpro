import os
# Bot
BOT_TOKEN = '5729824730:AAEByN_q5jonFiWzFaH4pyt0_F9ootPdx1I'
TG_API_ID = '18641760'
TG_API_HASH = 'b7b026ce9d1d36400c02dc21d8df53a3'
TG_ADMIN = 'obisoftt'
HOST_SERVER = os.environ.get('host_server','https://host-server.example.com/')

#Web Flask
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 443
ENV_PORT = os.environ.get('PORT',None)
if ENV_PORT:
   FLASK_PORT = ENV_PORT
FLASK_PORT = 443
FLASK_DEBUG = True

# Database
DB_LOCAL = False
DB_HOST = 'db4free.net'
DB_HOST_USERNAME = 'clutilprobot'
DB_HOST_PASSWORD = 'SdmxZw5Hqy3RvYE'
DB_NAME = 'clutilprodb'

if DB_LOCAL:
    # Database Local
    DB_HOST = ''
    DB_HOST_USERNAME = 'root'
    DB_HOST_PASSWORD = ''
    DB_NAME = 'clutilprodb'
