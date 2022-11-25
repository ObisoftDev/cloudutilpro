# plugins fields to add plugins command info
TITLE = 'youtube'
def get_description():
    return 'youtube'

# require libraries pyobidl | pyobigram | pytube
from pyobigram.client import ObigramClient

def on_load(bot:ObigramClient):
    pass

def on_handle(update,bot:ObigramClient,user=None,args={}):
    pass