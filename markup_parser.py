from pyobigram.inline import inlineKeyboardMarkupArray,inlineKeyboardButton

def parse(markups):
    result = []
    for markup in markups:
        newarray = []
        for item in markup:
            if item['type'] == 'button':
               text = ''
               url = ''
               callback = ''
               if 'text' in item:
                   text = item['text']
               if 'url' in item:
                   url = item['url']
               if 'callback' in item:
                   callback = item['callback']
               button = inlineKeyboardButton(text,url,callback)
               newarray.append(button)
        result.append(newarray)
    if len(result)>0:
       return inlineKeyboardMarkupArray(result)
    else:
        return None