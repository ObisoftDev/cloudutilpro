# import system
import os
import imp

# import code
import config
import database
import ui_template
import markup_parser

# from libraries
from pyobigram.client import ObigramClient
from models.user import User

PLUGINS = {}

def load_exec_plugins(update,bot,user,args):
    global PLUGINS
    plugins = os.listdir('plugins')
    pluglen = len(plugins)
    if 'ui_text' in plugins:
        pluglen-=1
    if '__pycache__' in plugins:
        pluglen-=1
    if pluglen > len(PLUGINS):
        for p in plugins:
            if p in PLUGINS:continue
            try:
                if not '.' in p:continue
                name = str(p).split('.')[0]
                plug = imp.load_source(name,f'plugins/{p}')
                plug.on_load(bot)
                print(f'{name} plugin load!')
                PLUGINS[p] = plug
            except Exception as ex:
                print(str(ex))
    #handle plugins
    for plug in PLUGINS:
        PLUGINS[plug].on_handle(update,bot,user,args)
    return len(PLUGINS),PLUGINS


ACCES_FREE = False

def message_handle(update,bot:ObigramClient):
    global ACCES_FREE

    message = update.message
    text = ''
    try:
        text = message.text
    except:pass
    username = message.chat.username

    user:User = database.get_user_from(username=username)
    access = True

    if user:
        pass
    else:
        if ACCES_FREE:
            user = User(tg_id=str(message.sender.id),username=username)
            user.create_config()
        elif username == config.TG_ADMIN:
            user = User(tg_id=str(message.sender.id),username=username)
            user.set_admin(lvl=999)
            user.create_config()
        else:
            access = False

    args = {}
    if user:
        user.tg_id = str(message.sender.id)
        args['username'] = user.username
        args['tg_id'] = user.tg_id
        args['is_admin'] = user.is_admin
        args['admin_lvl'] = user.admin_lvl

        args['cloud_host'] = user.config.cloud_host
        args['cloud_username'] = user.config.cloud_username
        args['cloud_password'] = user.config.cloud_password
        args['cloud_repo_id'] = user.config.cloud_repo_id
        args['user_zips'] = user.config.zips
                                                                                    
    if not access:
        parse_mode,ui_text,markups = ui_template.load('not_acces',args)
        reply_markup = markup_parser.parse(markups)
        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)
        return

    len,plugins = load_exec_plugins(update,bot,user,args)

    if '/free' in text:
        if user.is_admin and user.admin_lvl==user.admin_lvl_max:
           if ACCES_FREE:
              ACCES_FREE = False
           else:
               ACCES_FREE = True

    if '/plugins' in text:
        args = {}
        args['len'] = len
        parser = []
        for plug in plugins:
            try:
                title = plugins[plug].TITLE
                desc = plugins[plug].get_description()
                parser.append({'title':title,'desc':desc})
            except:pass
        args['plugins'] = parser
        parse_mode,ui_text,markups = ui_template.load('plugins',args)
        reply_markup = markup_parser.parse(markups)
        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)

    if user:
       database.save_user(user)
    pass

if __name__ == '__main__':
    bot = ObigramClient(config.BOT_TOKEN,config.TG_API_ID,config.TG_API_HASH)

    #load plugins if PLUGINS empty
    if len(PLUGINS)<=0:
        plugins = os.listdir('plugins')
        for p in plugins:
            try:
                if not '.' in p:continue
                name = str(p).split('.')[0]
                plug = imp.load_source(name,f'plugins/{p}')
                plug.on_load(bot)
                print(f'{name} plugin load!')
                PLUGINS[p] = plug
            except Exception as ex:
                print(str(ex))

    bot.onMessage(message_handle)
    print('bot is started!')
    bot.run()