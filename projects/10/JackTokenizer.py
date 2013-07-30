from sys import argv


def tokenize(text):
    global lexicon
    newtext = ["<tokens>"]
    loc = 0
    while loc < len(text):
        token = []
        if text[loc] in lexicon['symbols']:
            newtext.append("<symbol> %s </symbol>" % text[loc])
            loc += 1
        elif text[loc] in lexicon['numbers']:
            while text[loc] in lexicon['numbers']:
                token.append(text[loc])
                loc += 1
            newtext.append("<integerConstant> %s </integerConstant>" % 
                           ''.join(token))      
        elif text[loc] == '"':
            loc += 1
            while text[loc] != '"':
                token.append(text[loc])
                loc += 1
            newtext.append("<StringConstant> %s </StringConstant>" % 
                           ''.join(token))
            loc += 1
        else: # Must be keyword or identifier
            token_found = False
            while token_found == False:
                token.append(text[loc])
                if ''.join(token) in lexicon['keywords']:
                    newtext.append("<keyword> %s </keyword>" % ''.join(token))
                    token_found = True
                loc += 1
                if text[loc] in lexicon['symbols'] or text[loc] == '"':
                    newtext.append("<identifier> %s </identifier>" % 
                                   ''.join(token))
                    token_found = True
    print newtext
    return newtext

def cleanup(jack_file):
    jacktext = []
    ignore_on = False
    for line in jack_file:
        if '//' in line:
            line = line[:line.index('//')]
        if ignore_on == True and '*/' in line:
            line = line[line.index('*/') + 2:]
            ignore_on = False
        for chari in range(len(line)):
            if line[chari] == '/' and chari != len(line)-1:
                if line[chari + 1] == '*':
                    ignore_on = True
            if line[chari] == ' ' or '\\' in ('%r'%line[chari]) or ignore_on:
                continue
            jacktext.append(line[chari])
    jacktext = ''.join(jacktext)
    return jacktext 


def process_file(jack_file):
    xml_file = open((jack_file[:-5] + 'T.xml'), 'w')
    jacktext = cleanup(open(jack_file))
    xml_file.write('\n'.join(tokenize(jacktext)))
    xml_file.close()
    return

def process_directory(jack_directory):
    for filename in os.listdir('%s' % jack_directory):
        if filename[-5:] == '.jack':
             process_file(filename)


lexicon = {'keywords':['class', 'constructor', 'function', 'method', 'field', 
                       'static', 'var', 'int', 'char', 'boolean', 'void', 
                       'true', 'false', 'null', 'this', 'let', 'do', 'if', 
                       'else', 'while', 'return'], 
           'symbols':['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', 
                      '*', '/', '&', '|', '<', '>', '=', '~'], 
           'numbers':['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']}


if __name__ == '__main__':
    script, to_be_tokenized = argv

    if to_be_tokenized[-1] == '/':
        to_be_tokenized = to_be_tokenized[:-1]

    if '/' not in to_be_tokenized:
        slash_index = 0
    else:
        slash_index = to_be_tokenized.rfind('/')
    if '.' in to_be_tokenized[slash_index:]:
        if to_be_tokenized[-5:] == '.jack':
            process_file(to_be_tokenized)
        else:
            print "\nArgument must be .jack file or directory."
            raise NameError
    else:
        process_directory(to_be_tokenized)
