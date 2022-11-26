# plugins fields to add plugins command info
TITLE = 'termux'
def get_description():
    return 'termux'

# require libraries pyobidl | pyobigram
import os
import shutil
import ui_template

from pyobigram.client import ObigramClient
from models.user import User

def on_load(bot:ObigramClient):
    pass

def on_handle(update,bot:ObigramClient,user:User=None,args={}):
    message = update.message
    text = ''
    try:
        text = message.text
    except:pass
    user_root_path = f'root/{user.username}/'

    if user.config.cd == '/':
        user.config.cd = ''

    if not os.path.isdir(user_root_path):
       os.mkdir(user_root_path)

    
    user_root_path = f'{user_root_path}{user.config.cd}'

    if not os.path.isdir(user_root_path):
       user.config.cd = ''

    user_root_path = f'{user_root_path}{user.config.cd}'

    args['files'] = os.listdir(user_root_path)
    args['len_files'] = len(args['files'])
    args['cd_set'] = f'{user.config.cd}'

    if '/rm' in text:
        text = str(text).replace('/rm ','')
        text = str(text).replace('/rm','')
        if text!='':
            index = int(text)
            files = os.listdir(user_root_path)
            text = files[index]
            rmdirpath = user_root_path+'/'+text
            if os.path.exists(rmdirpath):
                if not os.path.isdir(rmdirpath):
                   os.unlink(rmdirpath)
                else:
                   shutil.rmtree(rmdirpath)
                args['files'] = os.listdir(user_root_path)
                args['len_files'] = len(args['files'])
                parse_mode,ui_text = ui_template.load('termux_info',section='list_files',args=args)
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
            else:
                parse_mode,ui_text = ui_template.load('termux_info',section='mkdir_error',args=args)
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        else:
            parse_mode,ui_text = ui_template.load('termux_info',section='mkdir_error',args=args)
            bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        pass

    if '/ren' in text:
        text = str(text).replace('/ren ','')
        text = str(text).replace('/ren','')
        if text!='':
            parts = str(text).split(' ')
            text = parts[0]
            bren = parts[1]
            
            index = int(text)
            files = os.listdir(user_root_path)
            text = files[index]

            rmdirpath = user_root_path+'/'+text
            if os.path.exists(rmdirpath):
                os.rename(rmdirpath,str(rmdirpath).replace(text,bren))
                args['files'] = os.listdir(user_root_path)
                args['len_files'] = len(args['files'])
                parse_mode,ui_text = ui_template.load('termux_info',section='list_files',args=args)
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
            else:
                parse_mode,ui_text = ui_template.load('termux_info',section='mkdir_error',args=args)
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        else:
            parse_mode,ui_text = ui_template.load('termux_info',section='mkdir_error',args=args)
            bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        pass

    if '/mkdir' in text:
        text = str(text).replace('/mkdir ','')
        text = str(text).replace('/mkdir','')
        args['mkdir_path'] = text
        if text!='':
            mkdirpath = user_root_path+'/'+text
            if not os.path.exists(mkdirpath):
                os.mkdir(mkdirpath)
                args['files'] = os.listdir(user_root_path)
                args['len_files'] = len(args['files'])
                parse_mode,ui_text = ui_template.load('termux_info',section='mkdir',args=args)
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
            else:
                parse_mode,ui_text = ui_template.load('termux_info',section='mkdir_exist',args=args)
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        else:
            parse_mode,ui_text = ui_template.load('termux_info',section='mkdir_error',args=args)
            bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)

    if '/cd' in text:
        text = str(text).replace('/cd ','')
        text = str(text).replace('/cd','')
        if '..' in text:
            cd = ''
            try:
                tokens = str(user.config.cd).split('/')
                tokens.pop(len(tokens)-1)
                tokens.pop(len(tokens)-2)
                for t in tokens:
                    cd += t + '/'
            except:pass
            user.config.cd = cd
            text = '/ls'
        else:
            index = int(text)
            files = os.listdir(user_root_path)
            text = files[index]
            args['user_root_path'] = user_root_path
            args['cd_set'] = text
            valid = os.path.isdir(f'{user_root_path}{user.config.cd}{text}')
            if valid:
               user.config.cd = f'{user.config.cd}{text}/'
               args['files'] = os.listdir(f'{user_root_path}{user.config.cd}')
               args['len_files'] = len(args['files'])
               parse_mode,ui_text = ui_template.load('termux_info',section='list_files',args=args)
               bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
            else:
                parse_mode,ui_text = ui_template.load('termux_info',section='dir_invalid',args=args)
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        pass

    if '/ls' in text:
        try:
            user_root_path = f'{user_root_path}{user.config.cd}'
            args['files'] = os.listdir(user_root_path)
            args['len_files'] = len(args['files'])
            args['cd_set'] = f'{user.config.cd}'
        except:pass
        parse_mode,ui_text = ui_template.load('termux_info',section='list_files',args=args)
        bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
        pass

    pass
