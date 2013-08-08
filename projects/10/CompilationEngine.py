from sys import argv
import os



class TokenizedText:

    def __init__(self, textfile):
        self.tokens = []
        self.cursor = 0
        i = 0
        for line in textfile:
            self.tokens.append(TokenizedLine(line, i, self))
            i += 1

class TokenizedLine():

    def __init__(self, line, index, text):
        self.kind = self._getType(line)
        self.name = self._getName(line)
        self.index = index
        self.line = line
        self.text = text

    def peekahead(self, iterations=1):
        return self.text.tokens[self.index + iterations]

    def peekback(self, iterations=1):
        return self.text.tokens[self.index - iterations]

    def next(self):
        self.text.cursor += 1
        return self.text.tokens[self.text.cursor]

    def reset(self):
        return self.text.tokens[self.text.cursor]

    def _getType(self, line):
        """Returns the token type of the xml line."""
        return line[line.find('<')+1:line.find('>')]

    def _getName(self, line):
        """Returns the word/symbol of the xml token."""
        return line[line.find('>')+2:line.find('<',2)-1]


def process_tokens(text):
    newtext = []
    oplist = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    unoplist = ['-', '~']
    keyconstlist = ['true', 'false', 'null', 'this']

    def compileClass(token, depth):
        """Compiles a complete class."""
        print "compileClass"
        lines_to_add = ['  '*depth + "<class>\n", 
                        '  '*(depth+1) + token.line]
        token = token.next()
        assert token.kind in ['identifier', 'keyword']
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        assert token.kind == 'symbol' and token.name == '{'
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        while token.name in ['field', 'static']:
            lines_to_add.extend(compileClassVarDec(token, depth+1))
            token = token.next()
        while token.kind == 'keyword' and token.name in ['constructor', 
                            'function', 'method']:
            lines_to_add.extend(compileSubroutine(token, depth+1))
            token = token.next()
        assert token.kind == 'symbol' and token.name == '}'
        lines_to_add.extend(['  '*(depth+1) + token.line,
                             '  '*(depth) + "</class>\n"])
        return lines_to_add

    def compileClassVarDec(token, depth):
        """Compiles a static declaration or a field declaration."""
        print "compileClassVarDec"
        lines_to_add = ['  '*depth + "<classVarDec>\n",
                        '  '*(depth+1) + token.line]
        token = token.next()
        assert token.kind in ['keyword', 'identifier']
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        assert token.kind in ['keyword', 'identifier']
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        while token.kind == 'symbol' and token.name == ',':
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
            assert token.kind in ['keyword', 'identifier']
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
        assert token.kind == 'symbol' and token.name == ';'
        lines_to_add.extend(['  '*(depth+1) + token.line,
                             '  '*depth + "</classVarDec>\n"])
        return lines_to_add
        
    def compileSubroutine(token, depth):
        """Compiles a complete method, function, or constructor."""
        print "compileSubroutine"
        lines_to_add = ['  '*depth + "<subroutineDec>\n",
                        '  '*(depth+1) + token.line]
        token = token.next()
        assert token.kind in ['keyword', 'identifier']
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        assert token.kind == 'identifier'
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        assert token.kind == 'symbol' and token.name == '('
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        if token.kind != 'symbol' and token.name != ')':
            lines_to_add.extend(compileParameterList(token, depth+1))
        lines_to_add.append('  '*(depth+1) + "<symbol> ) </symbol>\n")
        token = token.next()
        assert token.kind == 'symbol' and token.name == '{'
        lines_to_add.extend(['  '*(depth+1) + "<subroutineBody>\n",
                             '  '*(depth+2) + token.line])
        token = token.next()
        while token.kind == 'keyword' and token.name == 'var':
            lines_to_add.extend(compileVarDec(token, depth+2))
            token = token.next()
        lines_to_add.extend(compileStatements(token, depth + 2))
        lines_to_add.append('  '*(depth+2) + "<symbol> } </symbol>\n")
        lines_to_add.extend(['  '*(depth+1) + "</subroutineBody>\n",
                             '  '*depth + "</subroutineDec>\n"])
        return lines_to_add
        
    def compileParameterList(token, depth):
        """Compiles a (possibly empty) parameter list, not including the 
           enclosing \"()\"."""
        print "compileParameterList"
        run_through_once = False
        lines_to_add = ['  '*depth + "<parameterList>\n"]
        while run_through_once == False or (token.kind == 'symbol' and
                                            token.name == ','):
            if token.kind == 'symbol' and token.name == ',':
                lines_to_add.append('  '*(depth) + token.line)
                token = token.next()
            assert token.kind in ['keyword', 'identifier']
            lines_to_add.append('  '*(depth) + token.line)
            token = token.next()
            assert token.kind == 'identifier'
            lines_to_add.append('  '*(depth) + token.line)
            token = token.next()
            run_through_once = True
        lines_to_add.append('  '*depth + "</parameterList>\n")
        return lines_to_add

    def compileVarDec(token, depth):
        """Compiles a var declaration."""
        print "compileVarDec"
        run_through_once = False
        lines_to_add = ['  '*depth + "<varDec>\n",
                        '  '*(depth+1) + token.line]
        token = token.next()
        while run_through_once == False or (token.kind == 'symbol' and 
                                            token.name == ','):
            if token.kind == 'symbol' and token.name == ',':
                lines_to_add.append('  '*(depth+1) + token.line)
                token = token.next()
            assert token.kind in ['keyword', 'identifier']
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
            assert token.kind == 'identifier'
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
            run_through_once = True
        assert token.kind == 'symbol' and token.name == ';'
        lines_to_add.extend(['  '*(depth+1) + token.line,
                             '  '*depth + "</varDec>\n"])
        return lines_to_add

    def compileStatements(token, depth):
        """
        Compiles a sequence of statements, not including the enclosing \"{}\".
        """
        lines_to_add = ['  '*depth + "<statements>\n"]
        while token.kind != 'symbol' or token.name != '}':
            print "compileStatements"
            print "Token name, index: %s, %d" % (token.name, token.index)
            assert token.kind == 'keyword' and token.name in [
                                    'let', 'if', 'while', 'do', 'return']
            if token.name == 'let':
                lines_to_add.extend(compileLet(token, depth)) 
            elif token.name == 'if':
                lines_to_add.extend(compileIf(token, depth)) 
            elif token.name == 'while':
                lines_to_add.extend(compileWhile(token, depth)) 
            elif token.name == 'do':
                lines_to_add.extend(compileDo(token, depth)) 
            elif token.name == 'return':
                lines_to_add.extend(compileReturn(token, depth)) 
            token = token.reset()
        lines_to_add.append('  '*depth + "</statements>\n")
        return lines_to_add

    def compileDo(token, depth):
        """Compiles a do statement."""
        print "compileDo"
        lines_to_add = ['  '*depth + "<doStatement>\n",
                        '  '*(depth+1) + token.line]
        token = token.next()
        assert token.kind == 'identifier'
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        assert token.kind == 'symbol' and token.name in ['(', '.']
        lines_to_add.append('  '*(depth+1) + token.line)
        if token.name == '.':
            token = token.next()
            assert token.kind == 'identifier'
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
            assert token.kind == 'symbol' and token.name == '('
            lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        lines_to_add.extend(compileExpressionList(token, depth + 1))
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        assert token.kind == 'symbol' and token.name == ';'
        lines_to_add.extend(['  '*(depth+1) + token.line,
                             '  '*depth + "</doStatement>\n",])
        token = token.next()
        return lines_to_add

    def compileLet(token, depth):
        """Compiles a let statement."""
        print "compileLet"
        lines_to_add = ['  '*depth + "<letStatement>\n",
                        '  '*(depth+1) + token.line]
        print token.name
        token = token.next()
        assert token.kind == 'identifier'
        lines_to_add.append('  '*(depth+1) + token.line)
        print token.name
        token = token.next()
        if token.kind == 'symbol' and token.name == '[':
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
            if token.kind != 'symbol' or token.name != ']':
                lines_to_add.extend(compileExpression(token, depth + 1))
                line = token.next()
            assert token.kind == 'symbol' and token.name == ']'
            lines_to_add.append('  '*(depth+1) + token.line)
        print token.name
        assert token.kind == 'symbol' and token.name == '='
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        lines_to_add.extend(compileExpression(token, depth + 1))
        token = token.reset()
        assert token.kind == 'symbol' and token.name == ';'
        lines_to_add.extend(['  '*(depth+1) + token.line,
                             '  '*depth + "</letStatement>\n"])
        token = token.next()
        return lines_to_add        

    def compileWhile(token, depth):
        """Compiles a while statement."""
        print "compileWhile"
        lines_to_add = ['  '*depth + "<whileStatement>\n",
                        '  '*(depth+1) + token.line]
        token = token.next()
        assert token.kind == 'symbol' and token.name == '('
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        lines_to_add.extend(compileExpression(token, depth + 1))
        token = token.next()
        lines_to_add.append('  '*(depth+1) + "<symbol> ) </symbol>\n")
        assert token.kind == 'symbol' and token.name == '{'
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        lines_to_add.extend(compileStatements(token, depth + 1))
        token = token.reset()
        assert token.kind == 'symbol' and token.name == '}'
        lines_to_add.extend(['  '*(depth+1) + token.line,
                             '  '*depth + "</whileStatement>\n"])
        token = token.next()
        return lines_to_add

    def compileReturn(token, depth):
        """Compiles a return statement."""
        print "compileReturn"
        lines_to_add = ['  '*depth + "<returnStatement>\n",
                        '  '*(depth+1) + token.line]
        token = token.next()
        if token.kind != 'symbol' or token.name != ';':
            lines_to_add.extend(compileExpression(token, depth))
        token = token.reset()
        assert token.kind == 'symbol' and token.name == ';'
        lines_to_add.extend(['  '*(depth+1) + token.line,
                             '  '*depth + "</returnStatement>\n"])
        token = token.next()
        return lines_to_add
        
    def compileIf(token, depth):
        """Compiles an if statement, possibly with a trailing else clause."""
        print "compileIf"
        lines_to_add = ['  '*depth + "<ifStatement>\n",
                        '  '*(depth+1) + token.line]
        token = token.next()
        assert token.kind == 'symbol' and token.name == '('
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        lines_to_add.extend(compileExpression(token, depth + 1))
        token = token.next()
        lines_to_add.append('  '*(depth+1) + "<symbol> ) </symbol>\n")
        assert token.kind == 'symbol' and token.name == '{'
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        lines_to_add.extend(compileStatements(token, depth + 1))
        lines_to_add.append('  '*(depth+1) + "<symbol> } </symbol>\n")
        if (token.peekahead()).kind == 'keyword' and (
                token.peekahead()).name == 'else':
            token = token.next()
            lines_to_add.append('  '*(depth+1) + token.line)
            assert token.kind == 'symbol' and token.name == '{'
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
            lines_to_add.extend(compileStatements(token, depth + 1))
            lines_to_add.append('  '*(depth+1) + "<symbol> } </symbol>\n")
        lines_to_add.append('  '*depth + "</ifStatement>\n")
        token = token.next()
        return lines_to_add

    def compileExpression(token, depth):
        """Compiles an expression."""
        print "compileExpression"
        lines_to_add = ['  '*depth + "<expression>\n"]
        lines_to_add.extend(compileTerm(token, depth + 1))
        if (token.peekahead()).kind == 'symbol' and (
                token.peekahead()).name in oplist:
            token = token.next()
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
            lines_to_add.extend(compileTerm(token, depth + 1))
        lines_to_add.append('  '*depth + "</expression>\n")
        return lines_to_add
            
    def compileTerm(token, depth):
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
        if token.kind == 'symbol':
            if token.name in unoplist:
                lines_to_add.append('  '*(depth+1) + token.line)
                token = token.next()
                lines_to_add.extend(compileTerm(line, depth + 1))
            elif token.name == '(':
                lines_to_add.append('  '*(depth+1) + token.line)
                token = token.next()
                lines_to_add.extend(compileExpression(token, depth + 1))
                lines_to_add.append('  '*(depth+1) + "<symbol> ) </symbol>\n")
        elif token.kind == 'keyword':
            assert token.name in keyconstlist
            lines_to_add.append('  '*(depth+1) + token.line)
        elif token.kind == 'identifier':
            lines_to_add.append('  '*(depth+1) + token.line)
            nexttoken = token.peekahead()
            if nexttoken.kind == 'symbol':
                if nexttoken.name == '[':
                    token = token.next()
                    lines_to_add.append('  '*(depth+1) + token.line)
                    token = token.next()
                    if token.kind != 'symbol' or token.name != ']':
                        lines_to_add.extend(compileExpression(token, depth + 1))
                    lines_to_add.append('  '*(depth+1)+"<symbol> ] </symbol>\n")
                elif token.name in ['(', '.']:
                    token = token.next()
                    lines_to_add.append('  '*(depth+1) + token.line)
                    if token.name == '.':
                        token = token.next()
                        assert token.kind == 'identifier'
                        lines_to_add.append('  '*(depth+1) + token.line)
                        token = token.next()
                        assert token.kind=='symbol' and token.name=='('
                        lines_to_add.append('  '*(depth+1) + token.line)
                    token = token.next()
                    lines_to_add.extend(compileExpressionList(token, depth + 1))
                    lines_to_add.append('  '*(depth+1)+"<symbol> ) </symbol>\n")
        lines_to_add.append('  '*depth + "</term>\n")
        token = token.next()
        return lines_to_add
                                
    def compileExpressionList(token, depth):
        """Compiles a (possibly empty) comma-separated list of expressions."""
        print "compileExpressionList"
        run_through_once = False
        lines_to_add = ['  '*depth + "<expressionList>\n"]
        if token.kind != 'symbol' and token.name != ')':
            while run_through_once == False or (token.kind == 'symbol' and 
                                                token.name == ','): 
                if token.kind == 'symbol' and token.name == ',':
                    lines_to_add.append('  '*(depth+1) + token.line)
                    token = token.next()
                lines_to_add.extend(compileExpression(token, depth + 1))
                token = token.reset()
                run_through_once = True
        lines_to_add.append('  '*depth + "</expressionList>\n")
        return lines_to_add

    print "Testing:"
    print "Token = %s" % text.tokens[1]
    print "Token.line = %s" % text.tokens[1].line
    print "Token.kind = %s" % text.tokens[1].kind
    print "Token.name = %s" % text.tokens[1].name
    print "Token.index = %s" % text.tokens[1].index

    depth = 0
    for token in text.tokens:
        if token.name == 'class' and token.kind == 'keyword':
            print "Class compile"
            newtext.extend(compileClass(token, depth))
        text.cursor += 1
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
