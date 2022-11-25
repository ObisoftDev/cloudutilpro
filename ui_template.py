import os
import codecs

def exec_lines(lines,args={},sections={}):
    result = ''
    recolect = False
    recolect_lines = []
    calle = ''
    for line in lines:
            if '##' in line:continue
            if line=='':continue
            try:
                if '@if' in line and not recolect or '@for' in line and not recolect:
                    calle = line
                    recolect = True
                    continue
                if recolect:
                    if '@endif' in line and '@if' in calle:
                        recolect = False
                        if calle!='':
                            calle = str(calle).replace('@if ','').replace('\r','').replace('\n','')
                            if 'not ' in calle:
                                calle = str(calle).replace('not ','')
                                if not args[calle]:
                                   result += exec_lines(recolect_lines,args)
                            elif args[calle]:
                                result += exec_lines(recolect_lines,args)
                        recolect_lines.clear()
                        continue
                    elif '@endfor' in line and '@for' in calle:
                        recolect = False
                        if calle!='':
                            calle = str(calle).replace('@for ','').replace('\r','').replace('\n','')
                            tokens = str(calle).split(' in ')
                            key = tokens[0]
                            iter = tokens[1]
                            args[key] = None
                            args['for_index'] = 0
                            if iter in args:
                               for item in args[iter]:
                                   try:
                                       for itemin in item:
                                           args[f'{key}.{itemin}'] = item[itemin]
                                       pass
                                   except:pass
                                   args[key] = item
                                   result += exec_lines(recolect_lines,args)
                                   args['for_index'] += 1
                            args.pop(key)
                            args.pop(for_index)
                        recolect_lines.clear()
                        continue
                    recolect_lines.append(line)
                    continue
                if '@>>' in line:
                    keys = []
                    tokens = str(line).split(' ')
                    for t in tokens:
                        if '@>>' in t:
                            tremp = str(t).split('@>>')[1]
                            keys.append(str(tremp).replace('\r','').replace('\n','').replace('@','').replace('>>',''))
                    line_result = line
                    for key in keys:
                        if key in args:
                           line_result = str(line_result).replace(f'@>>{key}',str(args[key]))
                        else:
                           line_result = str(line_result).replace(f'@>>{key}','none')
                    result += line_result + '\n'
                    continue
                if '@onejump' in line:
                    result = str(result).replace('\n\n','\n')
                    continue
                if '@jmpto_sect' in line:
                    section = str(line).replace('@jmpto_sect ','').replace('\n','').replace('\r','')
                    if section in sections:
                       result += exec_lines(sections[section],args=args,sections=sections)
                    continue
                result += line + '\n'
            except:pass
    return result
def parse_markup(line):
    line = str(line).replace('\r','').replace('\n','')
    markup = {}
    if '@' in line:
        line = str(line).replace('@','')
        tokens = str(line).split(' ')
        type = tokens[0]
        markup['type'] = type
        i = 1
        value = ''
        recolect = False
        while i < len(tokens)+1:
            try:
                item = tokens[i]
            except:
                item = '='
                recolect = True
            if '=' in item:
                if recolect:
                   recolect = False
                   tvalues = str(value).replace("'",'').split('=')
                   key = tvalues[0]
                   val = tvalues[1]
                   markup[key] = val
                   value = ''
                else:
                    recolect = True
                value += item
                i+=1
                continue
            if recolect:
                value += item + ' '
                i+=1
                continue
            i+=1
        pass
    return markup

def get_sections_markups(lines):
    sections = {}
    recolect = False
    recolect_lines = []
    markups = []
    calle = ''
    for line in lines:
            if '##' in line:continue
            if line=='':continue
            try:
                if '@section' in line and not recolect or '@markup' in line and not recolect:
                    calle = line
                    recolect = True
                    continue
                if recolect:
                    if '@endsection' in line and '@section' in calle:
                        recolect = False
                        if calle!='':
                           calle = str(calle).replace('@section ','').replace('\r','').replace('\n','')
                           sections[calle] =  []
                           for re in recolect_lines:
                               sections[calle].append(re)
                        recolect_lines.clear()
                        continue
                    if '@endmarkup' in line and '@markup' in calle:
                        recolect = False
                        addmarkups = []
                        if len(recolect_lines)>0:
                           for re in recolect_lines:
                               if '@jmplist' in re:
                                   markups.append(addmarkups)
                                   addmarkups = []
                                   continue
                               addmarkups.append(parse_markup(re))
                               pass
                           markups.append(addmarkups)
                        recolect_lines.clear()
                        continue
                    recolect_lines.append(line)
            except:pass
    return sections,markups

def load(name='',args={},section='__base',path='plugins/ui_text/'):
    result = None
    define = ''
    markups = []
    if name!='':
        tmp = codecs.open(f'{path}{name}.tui','r','utf8')
        result = tmp.read()
        tmp.close()
    if result:
        for arg in args:
            result = str(result).replace(f'@>>{arg}',str(args[arg]))

        lines = str(result).split('\n')
        sections,markups = get_sections_markups(lines)
        
        if section in sections:
            lines = sections[section]
        else:
            lines = []

        if len(lines)>0:
            line0 = lines[0]
            if '@define ' in line0:
                lines.pop(0)
                define = str(line0).replace('@define ','').replace('\n','').replace('\r','')
        result = exec_lines(lines,args=args,sections=sections)
    if len(markups)>0:
       return define,result,markups
    else:
       return define,result