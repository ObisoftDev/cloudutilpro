# plugins fields to add plugins command info
TITLE = 'descargas'
def get_description():
    return 'descargas'

# require libraries pyobidl | pyobigram
from pyobigram.client import ObigramClient
from pyobidl.downloader import Downloader
from pyobidl.utils import sizeof_fmt,createID

import os
import config
import ui_template
import markup_parser
import threading

from flask import Flask, request, Response, send_from_directory,make_response,redirect


flask = Flask(__name__)

def redirect_file_stream(path,read_size=1024):
        try:
            with open(path,'rb') as f:
                len = os.stat(path).st_size
                read = 0
                while read<len:
                    chunk = f.read(read_size)
                    read += read_size
                    yield chunk
        except Exception as ex:
            pass
        return b''

@flask.route('/<path:path>')
def download_file_with_path(path=''):
    fullpath = f'root/{path}'
    filename = str(fullpath).split('/')[-1]
    if os.path.isfile(fullpath):
        headers = {
            "Content-Type": 'application/octet-stream',
            "Content-Disposition": "attachment;filename={}".format(filename),
            }
        return Response(redirect_file_stream(fullpath), 200, headers)
    else:
        return '<h1 style="color:red">FILE NOT FOUND</h1>',404
#run flask in thread
threading.Thread(target=lambda: flask.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG, use_reloader=False)).start()

def on_load(bot:ObigramClient):
    bot.onCallbackData('/cancel',cancel_download)
    pass

DOWNLOADERS = {}
BOT_DOWNLOADERS = {}

def cancel_download(update,bot:ObigramClient):
    global DOWNLOADERS
    global BOT_DOWNLOADERS
    dl_id = str(update.data).replace('_','')
    if dl_id in DOWNLOADERS:
        DOWNLOADERS[dl_id].stop()
    if dl_id in BOT_DOWNLOADERS:
        BOT_DOWNLOADERS[dl_id]['stoping'] = True
    pass

def progress_downloader(dl:Downloader,filename,index,total,speed,time,args):
    try:
        bot:ObigramClient = args[0]
        message = args[1]
        args = {}
        args['task_id'] = dl.id
        args['filename'] = filename
        args['index'] = sizeof_fmt(index)
        args['total'] = sizeof_fmt(total)
        args['speed'] = sizeof_fmt(speed)
        args['time'] = sizeof_fmt(time)
        parse_mode,ui_text,markups = ui_template.load('dl',section='downloading',args=args)
        reply_markup = markup_parser.parse(markups)
        bot.edit_message(message,ui_text,parse_mode=parse_mode,reply_markup=reply_markup)
    except:pass
    pass

def progress_download_bot(bot:ObigramClient,filename,index,total,speed,time,args):
    global BOT_DOWNLOADERS
    try:
        message = None
        dl_id = ''
        try:
            message = args[0]
            dl_id = args[1]
        except:pass
        if dl_id in BOT_DOWNLOADERS:
            BOT_DOWNLOADERS[dl_id]['filename'] = filename
        args = {}
        args['task_id'] = dl_id
        args['filename'] = filename
        args['index'] = sizeof_fmt(index)
        args['total'] = sizeof_fmt(total)
        args['speed'] = sizeof_fmt(speed)
        args['time'] = sizeof_fmt(time)
        parse_mode,ui_text,markups = ui_template.load('dl',section='downloading',args=args)
        reply_markup = markup_parser.parse(markups)
        bot.edit_message(message,ui_text,parse_mode=parse_mode,reply_markup=reply_markup)
    except:pass
    if dl_id in BOT_DOWNLOADERS:
       if BOT_DOWNLOADERS[dl_id]['stoping']:
           stop.append(1)
    pass

def on_handle(update,bot:ObigramClient,user=None,args={}):
    global DOWNLOADERS
    global BOT_DOWNLOADERS
    message = update.message
    text = ''
    try:
        text = message.text
    except:pass
    user_root_path = f'root/{user.username}/'
    user_root_path = f'{user_root_path}{user.config.cd}'

    try:
        reply_to_message = message.reply_to_message
        if '/share' in text:
            return
        if '/download' in text:
            if bot.contain_file(reply_to_message):
               dl_id = createID()
               args = {'task_id':dl_id}
               BOT_DOWNLOADERS[dl_id] = {'filename':'','stoping':False}
               parse_mode,ui_text,markups = ui_template.load('dl',section='starting_file',args=args)
               reply_markup = markup_parser.parse(markups)
               message_to_edit = bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=reply_to_message.message_id)
               
               output = None
               try:
                  output = bot.mtp_download_file(reply_to_message,user_root_path,progress_download_bot,(message_to_edit,dl_id))
               except Exception as ex:
                   pass

               filename = BOT_DOWNLOADERS[dl_id]['filename']
               stoping = BOT_DOWNLOADERS[dl_id]['stoping']
               if not stoping:
                   if output:
                      args['files'] = os.listdir(user_root_path)
                      args['len_files'] = len(args['files'])
                      args['cd_set'] = f'{user.config.cd}'
                      parse_mode,ui_text = ui_template.load('termux_info',section='list_files',args=args)
                      bot.delete_message(message_to_edit)
                      bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=reply_to_message.message_id)
                   else:
                      parse_mode,ui_text,markups = ui_template.load('dl',section='error')
                      bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode)
               else:
                   args={}
                   args['down_url'] = ''
                   args['down_filename'] = filename
                   parse_mode,ui_text,markups = ui_template.load('dl',section='cancel',args=args)
                   bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode)
            else:
                parse_mode,ui_text,markups = ui_template.load('dl',section='error_nofile')
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=reply_to_message.message_id)
    except:pass

    if '/share' in text:
        text = str(text).replace('/share ','')
        text = str(text).replace('/share','')
        if text!='':
            index = int(text)
            files = os.listdir(user_root_path)
            filename = files[index]
            args = {}
            args['share_filename'] = filename
            args['share_url'] = config.HOST_SERVER + str(user_root_path).replace('root/','') + filename
            parse_mode,ui_text,markups = ui_template.load('share',section='shared',args=args)
            reply_markup = markup_parser.parse(markups)
            messate_send = bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)
            pass
        else:
            parse_mode,ui_text,markups = ui_template.load('share',section='error',args=args)
            reply_markup = None
            bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)

    if 'http' in text and 'youtube' not in text:

        dl = Downloader(user_root_path)
        DOWNLOADERS[dl.id] = dl

        args = {'task_id':dl.id}
        parse_mode,ui_text,markups = ui_template.load('dl',section='starting',args=args)
        reply_markup = markup_parser.parse(markups)
        message_to_edit = bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_markup=reply_markup,reply_to_message_id=message.message_id)

        output = None
        try:
            output = dl.download_url(text,progressfunc=progress_downloader,args=(bot,message_to_edit))
        except:pass

        if not dl.stoping:
            if output:
                args['files'] = os.listdir(user_root_path)
                args['len_files'] = len(args['files'])
                args['cd_set'] = f'{user.config.cd}'
                parse_mode,ui_text = ui_template.load('termux_info',section='list_files',args=args)
                bot.delete_message(message_to_edit)
                bot.send_message(message.chat.id,ui_text,parse_mode=parse_mode,reply_to_message_id=message.message_id)
                pass
            else:
                parse_mode,ui_text,markups = ui_template.load('dl',section='error')
                bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode)
        else:
            args={}
            args['down_url'] = text
            args['down_filename'] = ''
            if dl.filename:
                args['down_filename'] = dl.filename
            parse_mode,ui_text,markups = ui_template.load('dl',section='cancel',args=args)
            bot.edit_message(message_to_edit,ui_text,parse_mode=parse_mode)
        DOWNLOADERS.pop(dl.id)
        pass

    pass