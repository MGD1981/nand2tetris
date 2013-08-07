from sys import argv
import os



class TokenizedText:

    def __init__(self, textfile):
        self.tokens = []
        for line in textfile:
            self.tokens.append(TokenizedLine(line))

class TokenizedLine:

    def __init__(self, line):
        self.kind = self.getType(line)
        self.name = self.getName(line)
        self.line = line

    def getType(self, line):
        """Returns the token type of the xml line."""
        return line[line.find('<')+1:line.find('>')]

    def getName(self, line):
        """Returns the word/symbol of the xml token."""
        return line[line.find('>')+2:line.find('<',2)-1]


def process_tokens(text):
    newtext = []
    oplist = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    unoplist = ['-', '~']
    keyconstlist = ['true', 'false', 'null', 'this']

    def compileClass(line, depth):
        """Compiles a complete class."""
        print "compileClass"
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
        while getType(line) == 'keyword' and getName(line) in ['constructor', 
                            'function', 'method']:
            lines_to_add.extend(compileSubroutine(line, depth+1))
            line = text.next()
        print lines_to_add
        print len(lines_to_add)
        print line
        assert getType(line) == 'symbol' and getName(line) == '}'
        lines_to_add.extend(['  '*(depth+1) + line,
                             '  '*(depth) + "</class>\n"])
        return lines_to_add

    def compileClassVarDec(line, depth):
        """Compiles a static declaration or a field declaration."""
        print "compileClassVarDec"
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
        print "compileSubroutine"
        lines_to_add = ['  '*depth + "<subroutineDec>\n",
                        '  '*(depth+1) + line]
        line = text.next()
        assert getType(line) in ['keyword', 'identifier']
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        assert getType(line) == 'identifier'
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        assert getType(line) == 'symbol' and getName(line) == '('
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        if getType(line) != 'symbol' and getName(line) != ')':
            lines_to_add.extend(compileParameterList(line, depth+1))
        lines_to_add.append('  '*(depth+1) + "<symbol> ) </symbol>\n")
        line = text.next()
        assert getType(line) == 'symbol' and getName(line) == '{'
        lines_to_add.extend(['  '*(depth+1) + "<subroutineBody>\n",
                             '  '*(depth+2) + line])
        line = text.next()
        if getType(line) == 'keyword' and getName(line) == 'var':
            lines_to_add.extend(compileVarDec(line, depth+2))
            line = text.next()
        lines_to_add.extend(compileStatements(line, depth + 2))
        lines_to_add.append('  '*(depth+2) + "<symbol> } </symbol>\n")
        lines_to_add.extend(['  '*(depth+1) + "</subroutineBody>\n",
                             '  '*depth + "</subroutineDec>\n"])
        return lines_to_add
        
    def compileParameterList(line, depth):
        """Compiles a (possibly empty) parameter list, not including the 
           enclosing \"()\"."""
        print "compileParameterList"
        run_through_once = False
        lines_to_add = ['  '*depth + "<parameterList>\n"]
        while run_through_once == False or (getType(line) == 'symbol' and
                                            getName(line) == ','):
            if getType(line) == 'symbol' and getName(line) == ',':
                lines_to_add.append('  '*(depth) + line)
                line = text.next()
            assert getType(line) in ['keyword', 'identifier']
            lines_to_add.append('  '*(depth) + line)
            line = text.next()
            assert getType(line) == 'identifier'
            lines_to_add.append('  '*(depth) + line)
            line = text.next()
            run_through_once = True
        lines_to_add.append('  '*depth + "</parameterList>\n")
        return lines_to_add

    def compileVarDec(line, depth):
        """Compiles a var declaration."""
        print "compileVarDec"
        run_through_once = False
        lines_to_add = ['  '*depth + "<varDec>\n",
                        '  '*(depth+1) + line]
        line = text.next()
        while run_through_once == False or (getType(line) == 'symbol' and 
                                            getName(line) == ','):
            if getType(line) == 'symbol' and getName(line) == ',':
                lines_to_add.append('  '*(depth+1) + line)
                line = text.next()
            assert getType(line) in ['keyword', 'symbol']
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
            assert getType(line) == 'identifier'
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
            run_through_once = True
        lines_to_add.append('  '*depth + "</varDec>\n")
        return lines_to_add

    def compileStatements(line, depth):
        """
        Compiles a sequence of statements, not including the enclosing \"{}\".
        """
        lines_to_add = ['  '*depth + "<statements>\n"]
        while getType(line) != 'symbol' or getName(line) != '}':
            print "compileStatements"
            linename = getName(line)
            print "Linename: %s" % linename
            assert getType(line) == 'keyword' and linename in [
                                    'let', 'if', 'while', 'do', 'return']
            if linename == 'let':
                lines_to_add.extend(compileLet(line, depth)) 
            if linename == 'if':
                lines_to_add.extend(compileIf(line, depth)) 
            if linename == 'while':
                lines_to_add.extend(compileWhile(line, depth)) 
            if linename == 'do':
                lines_to_add.extend(compileDo(line, depth)) 
            if linename == 'return':
                lines_to_add.extend(compileReturn(line, depth)) 
            line = lines_to_add.pop()
            print "Next line: %s" % line
        lines_to_add.append('  '*depth + "</statements>\n")
        return lines_to_add

    def compileDo(line, depth):
        """Compiles a do statement."""
        print "compileDo"
        lines_to_add = ['  '*depth + "<doStatement>\n",
                        '  '*(depth+1) + line]
        line = text.next()
        assert getType(line) == 'identifier'
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        assert getType(line) == 'symbol' and getName(line) in ['(', '.']
        lines_to_add.append('  '*(depth+1) + line)
        if getName(line) == '.':
            line = text.next()
            assert getType(line) == 'identifier'
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
            assert getType(line) == 'symbol' and getName(line) == '('
            lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        lines_to_add.extend(compileExpressionList(line, depth + 1))
        line = lines_to_add.pop()
        print "line: %s" % line
        lines_to_add.append('  '*(depth+1) + "<symbol> ) </symbol>\n")
        print lines_to_add
        assert getType(line) == 'symbol' and getName(line) == ';'
        lines_to_add.extend(['  '*(depth+1) + line,
                             '  '*depth + "</doStatement>\n",])
        line = text.next()
        lines_to_add.append(line)
        return lines_to_add

    def compileLet(line, depth):
        """Compiles a let statement."""
        print "compileLet"
        lines_to_add = ['  '*depth + "<letStatement>\n",
                        '  '*(depth+1) + line]
        print line
        line = text.next()
        assert getType(line) == 'identifier'
        lines_to_add.append('  '*(depth+1) + line)
        print line
        line = text.next()
        if getType(line) == 'symbol' and getName(line) == '[':
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
            if getType(line) != 'symbol' or getName(line) != ']':
                lines_to_add.extend(compileExpression(line, depth + 1))
                prev_line = lines_to_add.pop()
                line = text.next()
            lines_to_add.append('  '*(depth+1) + "<symbol> ] </symbol>\n")
        print line
        assert getType(line) == 'symbol' and getName(line) == '='
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        lines_to_add.extend(compileExpression(line, depth + 1))
        prev_line = lines_to_add.pop()
        lines_to_add.extend(['  '*(depth+1) + "<symbol> ; </symbol>\n",
                             '  '*depth + "</letStatement>\n",
                             prev_line])
        return lines_to_add        

    def compileWhile(line, depth):
        """Compiles a while statement."""
        print "compileWhile"
        lines_to_add = ['  '*depth + "<whileStatement>\n",
                        '  '*(depth+1) + line]
        line = text.next()
        assert getType(line) == 'symbol' and getName(line) == '('
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        lines_to_add.extend(compileExpression(line, depth + 1))
        prev_line = lines_to_add.pop()
        line = text.next()
        lines_to_add.append('  '*(depth+1) + "<symbol> ) </symbol>\n")
        assert getType(line) == 'symbol' and getName(line) == '{'
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        lines_to_add.extend(compileStatements(line, depth + 1))
        line = text.next()
        lines_to_add.extend(['  '*(depth+1) + "<symbol> } </symbol>\n",
                             '  '*depth + "</whileStatement>\n"])
        line = text.next()
        lines_to_add.append(line)
        return lines_to_add
        

    def compileReturn(line, depth):
        """Compiles a return statement."""
        print "compileReturn"
        lines_to_add = ['  '*depth + "<returnStatement>\n",
                        '  '*(depth+1) + line]
        line = text.next()
        if getType(line) != 'symbol' or getName(line) != ';':
            lines_to_add.extend(compileExpression(line, depth))
            line = lines_to_add.pop()
        lines_to_add.extend(['  '*(depth+1) + line,
                             '  '*(depth+1) + "<symbol> ; </symbol>\n",
                             '  '*depth + "</returnStatement>\n"])
        print "Return last line: %s" % line
        return lines_to_add
        
    def compileIf(line, depth):
        """Compiles an if statement, possibly with a trailing else clause."""
        print "compileIf"
        lines_to_add = ['  '*depth + "<ifStatement>\n",
                        '  '*(depth+1) + line]
        line = text.next()
        assert getType(line) == 'symbol' and getName(line) == '('
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        lines_to_add.extend(compileExpression(line, depth + 1))
        prev_line = lines_to_add.pop()
        line = text.next()
        lines_to_add.append('  '*(depth+1) + "<symbol> ) </symbol>\n")
        assert getType(line) == 'symbol' and getName(line) == '{'
        lines_to_add.append('  '*(depth+1) + line)
        line = text.next()
        lines_to_add.extend(compileStatements(line, depth + 1))
        line = text.next()
        lines_to_add.append('  '*(depth+1) + "<symbol> } </symbol>\n")
        if getType(line) == 'keyword' and getName(line) == 'else':
            lines_to_add.append('  '*(depth+1) + line)
            assert getType(line) == 'symbol' and getName(line) == '{'
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
            lines_to_add.extend(compileStatements(line, depth + 1))
            line = text.next()
            lines_to_add.append('  '*(depth+1) + "<symbol> } </symbol>\n")
        lines_to_add.append('  '*depth + "</ifStatement>\n")
        line = text.next()
        lines_to_add.append(line)
        return lines_to_add

    def compileExpression(line, depth):
        """Compiles an expression."""
        print "compileExpression"
        lines_to_add = ['  '*depth + "<expression>\n"]
        new_lines = compileTerm(line, depth + 1)
        prev_line = new_lines.pop()
        lines_to_add.append(new_lines)
        line = text.next()
        if getType(line) == 'symbol' and getName(line) in oplist:
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
            new_lines = compileTerm(line, depth + 1)
            line = new_lines.pop()
            lines_to_add.append(new_lines)
        lines_to_add.extend(['  '*depth + "</expression>\n", line])
        return lines_to_add
            
    def compileTerm(line, depth):
        """
        Compiles a term.  This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routine must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of \"[\", \"(\", or \".\" 
        suffices to distinguish between the three possibilities.  Any other 
        token is not part of this term and should not be advanced over.
        """
        print "compileTerm"
        lines_to_add = ['  '*depth + "<term>\n"]
        if getType(line) == 'symbol':
            if getName(line) in unoplist:
                lines_to_add.append('  '*(depth+1) + line)
                line = text.next()
                new_lines = compileTerm(line, depth + 1)
                prev_line = new_lines.pop()
                lines_to_add.append(new_lines)
                line = text.next()
            elif getName(line) == '(':
                lines_to_add.append('  '*(depth+1) + line)
                line = text.next()
                lines_to_add.extend(compileExpression(line, depth + 1))
                prev_line = lines_to_add.pop()
                line = text.next()
                lines_to_add.append('  '*(depth+1) + "<symbol> ) </symbol>\n")
        elif getType(line) == 'keyword':
            assert getName(line) in keyconstlist
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
        elif getType(line) == 'identifier':
            print "Term identifier: %s" % line
            lines_to_add.append('  '*(depth+1) + line)
            line = text.next()
            if getType(line) == 'symbol':
                if getName(line) == '[':
                    lines_to_add.append('  '*(depth+1) + line)
                    line = text.next()
                    if getType(line) != 'symbol' or getName(line) != ']':
                        lines_to_add.extend(compileExpression(line, depth + 1))
                        line = text.next()
                        prev_line = lines_to_add.pop()
                    lines_to_add.append('  '*(depth+1)+"<symbol> ] </symbol>\n")
                elif getName(line) in ['(', '.']:
                    lines_to_add.append('  '*(depth+1) + line)
                    if getName(line) == '.':
                        line = text.next()
                        assert getType(line) == 'identifier'
                        lines_to_add.append('  '*(depth+1) + line)
                        line = text.next()
                        assert getType(line)=='symbol' and getName(line)=='('
                        lines_to_add.append('  '*(depth+1) + line)
                    line = text.next()
                    lines_to_add.extend(compileExpressionList(line, depth + 1))
                    line = text.next()
                    lines_to_add.append('  '*(depth+1)+"<symbol> ) </symbol>\n")
        lines_to_add.extend(['  '*depth + "</term>\n", line])
        return lines_to_add
                                
    def compileExpressionList(line, depth):
        """Compiles a (possibly empty) comma-separated list of expressions."""
        print "compileExpressionList"
        run_through_once = False
        lines_to_add = ['  '*depth + "<expressionList>\n"]
        if getType(line) != 'symbol' and getName(line) != ')':
            while run_through_once == False or (getType(line) == 'symbol' and 
                                                getName(line) == ','): 
                if getType(line) == 'symbol' and getName(line) == ',':
                    lines_to_add.append('  '*(depth+1) + line)
                    line = text.next()
                lines_to_add.extend(compileExpression(line, depth + 1))
                line = lines_to_add[-1]
                run_through_once = True
        else:
            line = text.next()
        lines_to_add.extend(['  '*depth + "</expressionList>\n", line])
        return lines_to_add

    print "Testing:"
    print text.tokens[1]
    print text.tokens[1].line
    print text.tokens[1].kind
    print text.tokens[1].name

    depth = 0
    for token in text.tokens:
        if token.name == 'class' and token.kind == 'keyword':
            print "Class compile"
            newtext.extend(compileClass(token, depth))
    print newtext
    return ''.join(newtext)


def process_file(xml_file, xml_directory=''):
    if xml_directory == '':
        x = ''
    else:
        x = '/'
    print "Compiling file: %s" % (xml_directory + x + xml_file)
    compiled_file = open((xml_directory + x + xml_file[:-5] + '.xml'), 'w')
    tokenized_text = TokenizedText(open(xml_directory + x + xml_file))
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
