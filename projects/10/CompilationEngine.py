from sys import argv
import os


def process_tokens(text):
    newtext = []
    stack = []

    def get_element(line):
        return line[line.find('<')+1:line.find('>')]

    def get_name(line):
        return line[line.find('>')+2:line.find('<',2)-1]

    def write_class(depth, line):
        lines_to_append = []
        lines_to_append.append((' ' * depth) + '<class>\n')
        for _ in range(3):
            lines_to_append.append((' ' * (depth + 1)) + line)
            line = text.next()
        return lines_to_append

    def write_classVarDec(depth, line):
        lines_to_append = []
        lines_to_append.append((' ' * depth) + '<classVarDec>\n')
        while (get_element(line) != 'symbol' and
               get_name(line) != ';'):
            lines_to_append.append((' ' * (depth + 1)) + line)
            line = text.next()
        lines_to_append.append((' ' * (depth + 1)) + line)
        return lines_to_append

    def write_subroutineBody(depth, line):
        pass

    for line in text:
        depth = len(stack)
        element = get_element(line)
        name = get_name(line)

        if element == 'symbol':
            if name == '}':
                newtext.append((' ' * (depth - 1)) + stack.pop())
            elif name == ')':
                if stack[-1] == '</parameterList>\n':
                    newtext.append((' ' * (depth - 1)) + stack.pop())
                    newtext.append((' ' * (depth - 1)) + line)
                    newtext.append(''.join(write_subroutineBody(depth, line)))
                else:
                    newtext.append((' ' * (depth - 1)) + line)
                continue

        elif element == 'keyword':
            if name == 'class':
                stack.append('</class>\n') 
                newtext.append(''.join(write_class(depth, line)))
            elif name in ['static', 'field']:
                stack.append('</classVarDec>\n')
                newtext.append(''.join(write_classVarDec(depth, line)))
                newtext.append((' ' * depth) + stack.pop())
            elif name in ['constructor', 'function', 'method']:
                stack.append('</subroutineDec>\n')
                newtext.append((' ' * depth) + '<subroutineDec>\n')
                while (get_element(line) != 'symbol' and
                       get_name(line) != '('):
                    newtext.append((' ' * (depth + 1)) + line)
                    line = text.next()
                newtext.append((' ' * (depth + 1)) + line)
                stack.append('</parameterList>\n')
                
        newtext.append((' ' * depth) + line)
    print ''.join(newtext)
    return ''.join(newtext)


def process_file(xml_file, xml_directory=''):
    compiled_file = open((xml_file[:-5] + '.xml'), 'w')
    tokenized_text = open(xml_directory + '/' + xml_file)
    compiled_file.write(process_tokens(tokenized_text))
    compiled_file.close()
    return

def process_directory(xml_directory):
    for filename in os.listdir('%s' % xml_directory):
        if filename[-4:] == '.xml':
            if '<tokens>' not in (
                    open(xml_directory + '/' + filename).readline()):
                continue
            process_file(filename, xml_directory)

if __name__ == '__main__':
    script, to_be_compiled = argv

    if to_be_compiled[-1] == '/':
        to_be_compiled = to_be_compiled[:-1]

    if '/' not in to_be_compiled:
        slash_index = 0
    else:
        slash_index = to_be_compiled.rfind('/')
    if '.' in to_be_compiled[slash_index:]:
        if to_be_compiled[-4:] == '.xml':
            process_file(to_be_compiled)
        else:
            print "\nArgument must be .xml file or directory."
            raise NameError
    else:
        process_directory(to_be_compiled)
