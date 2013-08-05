from sys import argv
import os


def _ignore():

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


def process_tokens(text):
    newtext = []

    def getType(line):
        """Returns the token type of the xml line."""
        return line[line.find('<')+1:line.find('>')]

    def getName(line):
        """Returns the word/symbol of the xml token."""
        return line[line.find('>')+2:line.find('<',2)-1]

    def compileClass(line, depth):
        """Compiles a complete class."""
        lines_to_add = [(('  '*depth) + "<class>\n"), ('  '*(depth+1) + line)]
        line = text.next()
        assert getType(line) in ['identifier', 'keyword']
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        assert getType(line) == 'symbol' and getName(line) == '{'
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        assert (getType(line) == 'keyword' and getName(line) in ['field',
            'static']) or (getType(line) == 'symbol' and getName(line) == '}')
        while getName(line) in ['field', 'static']:
            lines_to_add.extend(compileClassVarDec(line, depth+1))
            line = text.next()
        if getType(line) == 'keyword' and getName(line) in ['constructor', 
                            'function', 'method']:
            lines_to_add.extend(compileSubroutine(line, depth+1))
            line = text.next()
        assert getType(line) == 'symbol' and getName(line) == '}'
        lines_to_add.extend(['  '*(depth+1) + line,
                             '  '*(depth) + "</class>\n"])
        return lines_to_add

    def compileClassVarDec(line, depth):
        """Compiles a static declaration or a field declaration."""
        lines_to_add = ['  '*depth + "<classVarDec>\n",
                        '  '*(depth+1) + line]
        line = text.next()
        assert getType(line) in ['keyword', 'identifier']
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        assert getType(line) in ['keyword', 'identifier']
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        while getType(line) == 'symbol' and getName(line) == ',':
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
            assert getType(line) in ['keyword', 'identifier']
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
        assert getType(line) == 'symbol' and getName(line) == ';'
        lines_to_add.extend(['  '*(depth+1) + line,
                             '  '*depth + "</classVarDec>\n"])
        return lines_to_add
        

    def compileSubroutine(line, depth):
        """Compiles a complete method, function, or constructor."""
        pass

    def compileParameterList():
        """Compiles a (possibly empty) parameter list, not including the 
           enclosing \"()\"."""
        pass

    def compileVarDec():
        """Compiles a var declaration."""
        pass

    def compileStatements():
        """
        Compiles a sequence of statements, not including the enclosing \"{}\".
        """
        pass

    def compileDo():
        """Compiles a do statement."""
        pass

    def compileLet():
        """Compiles a let statement."""
        pass

    def compileWhile():
        """Compiles a while statement."""
        pass

    def compileReturn():
        """Compiles a return statement."""
        pass

    def compileIf():
        """Compiles an if statement, possibly with a trailing else clause."""
        pass

    def compileExpression():
        """Compiles an expression."""
        pass

    def compileTerm():
        """
        Compiles a term.  This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routine must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of \"[\", \"(\", or \".\" 
        suffices to distinguish between the three possibilities.  Any other 
        token is not part of this term and should not be advanced over.
        """
        pass

    def compileExpressionList():
        """Compiles a (possibly empty) comma-separated list of expressions."""
        pass

    depth = 0
    for line in text:
        if getName(line) == 'class' and getType(line) == 'keyword':
            print "Class compile"
            newtext.extend(compileClass(line, depth))
    print newtext
    return ''.join(newtext)


def process_file(xml_file, xml_directory=''):
    if xml_directory == '':
        x = ''
    else:
        x = '/'
    print "Compiling file: %s" % (xml_directory + x + xml_file)
    compiled_file = open((xml_directory + x + xml_file[:-5] + '.xml'), 'w')
    tokenized_text = open(xml_directory + x + xml_file)
    compiled_file.write(process_tokens(tokenized_text))
    print "Wrote to: %s" % (xml_file[:-5] + '.xml')
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
