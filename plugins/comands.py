# plugins fields to add plugins command info
TITLE = 'commands'
def get_description():
    return 'commands'

# require libraries pyobidl | pyobigram
import time

import ui_template
import database
import markup_parser

from pyobigram.client import ObigramClient
from models.user import User


def on_load(bot:ObigramClient):pass

def on_handle(update,bot:ObigramClient,user:User=None,args={}):
    message = update.message
    text = ''
    try:
        text = message.text
    except:pass

    if '/start' in text:
        parse_mode,ui_text,markups = ui_template.load('start_cmd',args)
        reply_markup = markup_parser.parse(markups)
        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)
        pass

    if '/my' in text:
        parse_mode,ui_text = ui_template.load('user_info',args)
        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        pass

    if '/perm' in text: # add user permision
        text = str(text).replace('/perm ','')
        if user.is_admin:
            users = str(text).split(' ')
            for perm in users:
                args['perm_user'] = perm
                user_exist = database.get_user_from(username=perm)
                if user_exist:
                    parse_mode,ui_text = ui_template.load('perm_user',section='exist',args=args)
                    bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                else:
                    newuser = User(tg_id=str(int(time.time())),username=perm)
                    newuser.create_config()
                    newuser.set_admin(lvl=(user.admin_lvl-1))
                    saved = database.save_user(newuser)
                    if saved:
                        parse_mode,ui_text = ui_template.load('perm_user',section='permed',args=args)
                        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                    else:
                        parse_mode,ui_text = ui_template.load('perm_user',section='error',args=args)
                        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        pass

    if '/ban' in text:
        text = str(text).replace('/ban ','')
        if user.is_admin:
            users = str(text).split(' ')
            for ban in users:
                args['ban_user'] = ban
                args['ban_lvl'] = user.admin_lvl
                user_exist = database.get_user_from(username=ban)
                if user_exist:
                    args['ban_lvl'] = user_exist.admin_lvl
                    if user.admin_lvl>user_exist.admin_lvl:
                        if database.delete_user(username=user_exist.username):
                           parse_mode,ui_text = ui_template.load('ban_user',section='baned',args=args)
                           bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                        else:
                            parse_mode,ui_text = ui_template.load('ban_user',section='error',args=args)
                            bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                    else:
                        parse_mode,ui_text = ui_template.load('ban_user',section='error_lvl',args=args)
                        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                else:
                    parse_mode,ui_text = ui_template.load('ban_user',section='error',args=args)
                    bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        pass

    pass