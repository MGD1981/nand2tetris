from sys import argv
import os


def tokenize(text):
    global lexicon
    newtext = ["<tokens>"]
    loc = 0
    token = []
    while loc < len(text):
        token = []
        if text[loc] == ' ':
            loc += 1
        elif text[loc] in lexicon['symbols']:
            if text[loc] == '<':
                sym = '&lt;'
            elif text[loc] == '>':
                sym = '&gt;'
            elif text[loc] == '&':
                sym = '&amp;'
            else:
                sym = text[loc]
            newtext.append("<symbol> %s </symbol>" % sym)
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
            newtext.append("<stringConstant> %s </stringConstant>" % 
                           ''.join(token))
            loc += 1
        else: # Must be keyword or identifier
            token_found = False
            while token_found == False:
                token.append(text[loc])
                loc += 1
                if text[loc] in lexicon['symbols'] or text[loc] in ['"', ' ']:
                    if ''.join(token) in lexicon['keywords']:
                        newtext.append("<keyword> %s </keyword>" % 
                                       ''.join(token))
                        token_found = True
                    else: 
                        newtext.append("<identifier> %s </identifier>" % 
                                       ''.join(token))
                        token_found = True
    newtext.append("</tokens>")
    return newtext

def cleanup(jack_file):
    jacktext = []
    ignore_on = False
    for line in jack_file:
        if '//' in line:
            line = line[:line.index('//')]
        for chari in range(len(line)):
            if line[chari] == '/' and chari != len(line)-1:
                if line[chari + 1] == '*':
                    ignore_on = True
            if '\\' in ('%r'%line[chari]):
                jacktext.append(' ')
                continue
            if ignore_on:
                continue
            jacktext.append(line[chari])
        if ignore_on == True and '*/' in line:
            line = line[line.index('*/') + 2:]
            ignore_on = False
    jacktext = ''.join(jacktext)
    return jacktext 


def process_file(jack_file, jack_directory=''):
    if jack_directory == '':
        x = ''
    else:
        x = '/'
    print "Tokenizing file: %s" % (jack_directory + x + jack_file)
    jacktext = cleanup(open(jack_directory + x + jack_file))
    print "Tokenized %s" % (jack_file)
    return tokenize(jacktext)

def process_directory(jack_directory):
    global lexicon
    print "Tokenizing directory: %s" % jack_directory
    for filename in os.listdir('%s' % jack_directory):
        if filename[-5:] == '.jack':
            xml_file = process_file(filename, jack_directory)
            xml_file.close()
    return

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
            xml_file = process_file(to_be_tokenized)
            xml_file.close()
        else:
            print "\nArgument must be .jack file or directory."
            raise NameError
    else:
        process_directory(to_be_tokenized)
