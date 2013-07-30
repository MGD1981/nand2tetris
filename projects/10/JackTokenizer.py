from sys import argv


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
    print jacktext
    return jacktext 


def process_file(jack_file):
    xml_file = open((jack_file[:-5] + 'T.xml'), 'w')
    jacktext = cleanup(open(jack_file))
    xml_file.write(jacktext)
    xml_file.close()
    return

def process_directory(jack_directory):
    for filename in os.listdir('%s' % jack_directory):
        if filename[-5:] == '.jack':
             process_file(filename)


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
