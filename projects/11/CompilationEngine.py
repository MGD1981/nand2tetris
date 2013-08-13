from sys import argv
import os
import JackTokenizer
import pdb


class TokenizedText:

    def __init__(self, textfile):
        self.tokens = []
        self.cursor = 0

        self.class_table = {}
        self.subroutine_table = {}

        i = 0
        for line in textfile:
            if line[-1] != '\n':
                self.tokens.append(TokenizedLine(line + '\n', i, self))
            else:
                self.tokens.append(TokenizedLine(line, i, self))
            i += 1
        return

    def startSubroutine(self):
        self.subroutine_table = {}
        return

    def define(self, name, id_type, kind):
        assert kind in ['static', 'field', 'arg', 'var']
        index = self.varCount(kind)
        if kind in ['static', 'field']:
            self.class_table[name] = (kind, id_type, index)
        else:
            self.subroutine_table[name] = (kind, id_type, index)
        return

    def varCount(self, kind):
        assert kind in ['static', 'field', 'arg', 'var']
        if kind in ['static', 'field']:
            return sum(x[0] == kind for x in self.class_table.values())
        else:
            return sum(x[0] == kind for x in self.subroutine_table.values())

    def kindOf(self, name):
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name][0]
        elif name in self.class_table.keys():
            return self.class_table[name][0]
        else:
            return None

    def typeOf(self, name):
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name][1]
        elif name in self.class_table.keys():
            return self.class_table[name][1]
        else:
            return None

    def indexOf(self, name):
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name][2]
        elif name in self.class_table.keys():
            return self.class_table[name][2]
        else:
            return None


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


def process_tokens(text, filename, directory=''):
    newtext = []
    segmentdict = {'const':'constant', 'arg':'argument', 'local':'local',
                   'var':'local', 'static':'static', 'field':'static', 
                   'this':'this', 'that':'that', 'pointer':'pointer', 
                   'temp':'temp'}
    segmentlist = ['constant', 'argument', 'local', 'static', 'this', 'that', 
                   'pointer', 'temp']
    commandlist = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
    oplist = {'+':'add', '-':'sub', '*':None, '/':None, '&amp;':'and', '|':'or',              '&lt;':'lt', '&gt;':'gt', '=':'eq'}
    unoplist = {'-':'neg', '~':'not'}
    keyconstlist = ['true', 'false', 'null', 'this']
    ind = '   '
    vm_file = None

    def newVM(classname, directory):
        process_tokens.vm_file = open(directory + '/' + classname + '.vm', 'w')

    def writePush(segment, index=''):
        assert segment in segmentlist
        if index != '':
            assert type(index) == int
        process_tokens.vm_file.write(ind + "push " + segment + " " + 
                                     str(index) + '\n')

    def writePop(segment, index=''):
        assert segment in segmentlist
        if index != '':
            assert type(index) == int
        process_tokens.vm_file.write(ind + "pop " + segment + " " + 
                                     str(index) + '\n')

    def writeArithmetic(command):
        assert command in commandlist
        process_tokens.vm_file.write(ind + command + '\n')

    def writeLabel(label):
        assert type(label) == str
        process_tokens.vm_file.write("label " + label + '\n')

    def writeGoto(label):
        assert type(label) == str
        process_tokens.vm_file.write(ind + "goto " + label + '\n')

    def writeIf(label):
        assert type(label) == str
        process_tokens.vm_file.write(ind + "if-goto " + label + '\n')

    def writeCall(name, nArgs):
        assert type(name) == str
        assert type(nArgs) == int
        process_tokens.vm_file.write(ind + "call " + name + " " + 
                                     str(nArgs) + '\n')

    def writeFunction(name, nLocals):
        assert type(name) == str
        assert type(nLocals) == int
        process_tokens.vm_file.write("function " + filename + 
                                     '.' + name + " " + str(nLocals) + '\n')

    def writeReturn():
        process_tokens.vm_file.write(ind + 'return\n')

    def closeVM():
        process_tokens.vm_file.close()
        

    def compileClass(token, depth):
        """Compiles a complete class."""
        print "compileClass"
        token = token.next()
        assert token.kind in ['identifier', 'keyword']
        newVM(token.name, directory)
        token = token.next()
        assert token.kind == 'symbol' and token.name == '{'
        token = token.next()
        if token.kind == 'keyword' and token.name in ['static', 'field']:
            compileClassVarDec(token, depth+1)
            token = token.reset()
        while token.kind == 'keyword' and token.name in ['constructor', 
                            'function', 'method']:
            compileSubroutine(token, depth+1)
            token = token.next()
        assert token.kind == 'symbol' and token.name == '}'
        closeVM()
        return 'xxx' 

    def compileClassVarDec(token, depth):
        """Compiles a static declaration or a field declaration."""
        print "compileClassVarDec"
        while token.kind == 'keyword' and token.name in ['static', 'field']:
            kind = token.name
            token = token.next()
            assert token.kind in ['keyword', 'identifier']
            id_type = token.name
            token = token.next()
            if token.kind != 'symbol' or token.name != ';':
                assert token.kind in ['keyword', 'identifier']
                name = token.name
                token.text.define(name, id_type, kind)
                token = token.next()
                while token.kind == 'symbol' and token.name == ',':
                    token = token.next()
                    assert token.kind in ['keyword', 'identifier']
                    name = token.name
                    token.text.define(name, id_type, kind)
                    token = token.next()
            assert token.kind == 'symbol' and token.name == ';'
            token = token.next()
        print "Class Table: %r" % token.text.class_table
        return 'xxx'
        
    def compileSubroutine(token, depth):
        """Compiles a complete method, function, or constructor."""
        print "compileSubroutine"
        token.text.startSubroutine()
        #kind = token.name
        token = token.next()
        assert token.kind in ['keyword', 'identifier']
        #id_type = token.name
        token = token.next()
        assert token.kind == 'identifier'
        name = token.name
        token = token.next()
        assert token.kind == 'symbol' and token.name == '('
        token = token.next()
        compileParameterList(token, depth+1)
        nArgs = 0
        for arg in token.text.subroutine_table:
            if token.text.subroutine_table[arg][0] == 'arg':
                nArgs += 1
        writeFunction(name, nArgs)   
        for arg in range(0, nArgs):
            writePush('argument', arg)
        token = token.reset()
        assert token.kind == 'symbol' and token.name == ')'
        token = token.next()
        assert token.kind == 'symbol' and token.name == '{'
        token = token.next()
        while token.kind == 'keyword' and token.name == 'var':
            compileVarDec(token, depth+2)
            token = token.reset()
        compileStatements(token, depth + 2)
        token = token.reset()
        assert token.kind == 'symbol' and token.name == '}'
        print "Subroutine Table: %r" % token.text.subroutine_table
        return 'xxx'
        
    def compileParameterList(token, depth):
        """Compiles a (possibly empty) parameter list, not including the 
           enclosing \"()\"."""
        print "compileParameterList"
        kind = 'arg'
        run_through_once = False
        while run_through_once == False or (
                token.kind == 'symbol' and token.name == ','):
            if token.kind == 'symbol' and token.name == ')':
                break
            if token.kind == 'symbol' and token.name == ',':
                token = token.next()
            assert token.kind in ['keyword', 'identifier']
            id_type = token.name
            token = token.next()
            assert token.kind == 'identifier'
            name = token.name
            token.text.define(name, id_type, kind)
            token = token.next()
            run_through_once = True
        return 'xxx'

    def compileVarDec(token, depth):
        """Compiles a var declaration."""
        print "compileVarDec"
        run_through_once = False
        kind = token.name
        token = token.next()
        assert token.kind in ['keyword', 'identifier']
        id_type = token.name
        token = token.next()
        if token.kind != 'symbol' or token.name != ';':
            assert token.kind in ['keyword', 'identifier']
            name = token.name
            token.text.define(name, id_type, kind)
            token = token.next()
            while token.kind == 'symbol' and token.name == ',':
                token = token.next()
                assert token.kind == 'identifier'
                name = token.name
                token.text.define(name, id_type, kind)
                token = token.next()
        assert token.kind == 'symbol' and token.name == ';'
        token = token.next()
        return 'xxx'

    def compileStatements(token, depth):
        """
        Compiles a sequence of statements, not including the enclosing \"{}\".
        """
        while token.kind != 'symbol' or token.name != '}':
            print "compileStatements"
            assert token.kind == 'keyword' and token.name in [
                                    'let', 'if', 'while', 'do', 'return']
            if token.name == 'let':
                compileLet(token, depth+1) 
            elif token.name == 'if':
                compileIf(token, depth+1) 
            elif token.name == 'while':
                compileWhile(token, depth+1) 
            elif token.name == 'do':
                compileDo(token, depth+1) 
            elif token.name == 'return':
                compileReturn(token, depth+1) 
            token = token.reset()
        return 'xxx'

    def compileDo(token, depth):
        """Compiles a do statement."""
        print "compileDo"
        token = token.next()
        assert token.kind == 'identifier'
        name = token.name
        token = token.next()
        assert token.kind == 'symbol' and token.name in ['(', '.']
        if token.name == '.':
            token = token.next()
            assert token.kind == 'identifier'
            name = name + '.' + token.name
            token = token.next()
            assert token.kind == 'symbol' and token.name == '('
        token = token.next()
        nArgs = compileExpressionList(token, depth + 1)
        writeCall(name, nArgs)
        token = token.reset()
        assert token.kind == 'symbol' and token.name == ')'
        token = token.next()
        assert token.kind == 'symbol' and token.name == ';'
        token = token.next()
        return 'xxx'

    def compileLet(token, depth):
        """Compiles a let statement."""
        print "compileLet"
        token = token.next()
        assert token.kind == 'identifier'
        var_to_define = token.name
        token = token.next()
        if token.kind == 'symbol' and token.name == '[':
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
            if token.kind != 'symbol' or token.name != ']':
                lines_to_add.extend(compileExpression(token, depth + 1))
                token = token.reset()
            assert token.kind == 'symbol' and token.name == ']'
            lines_to_add.append('  '*(depth+1) + token.line)
            token = token.next()
        assert token.kind == 'symbol' and token.name == '='
        lines_to_add = []
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
        lines_to_add.extend(compileExpression(token, depth + 1))
        token = token.reset()
        assert token.kind == 'symbol' and token.name == ';'
        #writePush(segment, indexOf(var_to_define))
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
        token = token.reset()
        assert token.kind == 'symbol' and token.name == ')'
        lines_to_add.append('  '*(depth+1) + token.line)
        token = token.next()
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
        writeReturn()
        token = token.next()
        if token.kind != 'symbol' or token.name != ';':
            compileExpression(token, depth)
        token = token.reset()
        assert token.kind == 'symbol' and token.name == ';'
        token = token.next()
        return 'xxx'
        
    def compileIf(token, depth):
        """Compiles an if statement, possibly with a trailing else clause."""
        print "compileIf"
        token = token.next()
        assert token.kind == 'symbol' and token.name == '('
        token = token.next()
        compileExpression(token, depth + 1)
        token = token.reset()
        assert token.kind == 'symbol' and token.name == ')'
        token = token.next()
        assert token.kind == 'symbol' and token.name == '{'
        token = token.next()
        compileStatements(token, depth + 1)
        token = token.reset()
        assert token.kind == 'symbol' and token.name == '}'
        if (token.peekahead()).kind == 'keyword' and (
                token.peekahead()).name == 'else':
            token = token.next()
            token = token.next()
            #TODO: write code for else
            assert token.kind == 'symbol' and token.name == '{'
            token = token.next()
            compileStatements(token, depth + 1)
            token = token.reset()
            assert token.kind == 'symbol' and token.name == '}'
        token = token.next()
        return 'xxx'

    def compileExpression(token, depth):
        """Compiles an expression."""
        print "compileExpression"
        compileTerm(token, depth + 1)
        token = token.reset()
        if token.kind == 'symbol' and token.name in oplist:
            operation = token.name
            token = token.next()
            compileTerm(token, depth + 1)
            if operation in ['+', '-', '=', '&gt;', '&lt;', '&amp;', '|']:
                writeArithmetic(oplist[operation])
            elif operation == '*':
                writeCall('Math.multiply', 2)
        return 'xxx'
            
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
        if token.kind == 'symbol':
            if token.name in unoplist:
                operation = token.name
                token = token.next()
                compileTerm(token, depth + 1)
                writeArithmetic(unoplist[operation])
            elif token.name == '(':
                token = token.next()
                compileExpression(token, depth + 1)
                token = token.reset()
                assert token.kind == 'symbol' and token.name == ")"
                token = token.next()
        elif token.kind == 'keyword':
            assert token.name in keyconstlist
            if token.name == 'true':
                index = -1
                segment = 'constant'
            elif token.name in ['false', 'null']:
                index = 0
                segment = 'constant'
            else:
                index = 0
                segment = 'this'
            writePush(segment, index)
            token = token.next()
        elif token.kind in ['identifier', 'integerConstant', 'stringConstant']:
            name = token.name
            if token.kind == 'integerConstant':
                segment = 'constant'
                writePush(segment, int(name))
            elif token.kind == 'stringConstant':
                print "Need to handle stringConstant"
                #TODO
            else:
                if token.text.kindOf(token.name) == None:
                    segment = 0
                else:
                    segment = segmentdict[token.text.kindOf(token.name)]
            nexttoken = token.peekahead()
            if nexttoken.kind == 'symbol':
                if nexttoken.name == '[':
                    token = token.next()
                    token = token.next()
                    if token.kind != 'symbol' or token.name != ']':
                        compileExpression(token, depth + 1)
                        token = token.reset()
                    assert token.kind == 'symbol' and token.name == ']'
                elif nexttoken.name in ['(', '.']:
                    token = token.next()
                    if token.name == '.':
                        token = token.next()
                        assert token.kind == 'identifier'
                        name = name + '.' + token.name
                        token = token.next()
                        assert token.kind=='symbol' and token.name=='('
                    token = token.next()
                    nLocals = compileExpressionList(token, depth + 1)
                    token = token.reset()
                    assert token.kind == 'symbol' and token.name == ')'
            token = token.next()
        return 'xxx'
                                
    def compileExpressionList(token, depth):
        """Compiles a (possibly empty) comma-separated list of expressions."""
        print "compileExpressionList"
        params = 0
        run_through_once = False
        lines_to_add = ['  '*depth + "<expressionList>\n"]
        while run_through_once == False or (token.kind == 'symbol' and 
                                            token.name == ','): 
            if token.kind == 'symbol' and token.name == ')':
                break
            if token.kind == 'symbol' and token.name == ',':
                lines_to_add.append('  '*(depth+1) + token.line)
                token = token.next()
            params += 1
            lines_to_add.extend(compileExpression(token, depth + 1))
            token = token.reset()
            run_through_once = True
        lines_to_add.append('  '*depth + "</expressionList>\n")
        return params

    depth = 0
    for token in text.tokens:
        if token.name == 'class' and token.kind == 'keyword':
            print "Class compile"
            newtext.extend(compileClass(token, depth))
        text.cursor += 1
    return ''.join(newtext)


def process_file(jack_file, jack_directory=''):
    if jack_directory == '':
        x = ''
    else:
        x = '/'
    print "Compiling file: %s" % (jack_directory + x + jack_file)
    #print JackTokenizer.process_file(jack_file, jack_directory)
    tokenized_file = JackTokenizer.process_file(jack_file, jack_directory)
    tokenized_text = TokenizedText(tokenized_file)
    print "Wrote to: %s" % (jack_file[:-5] + '.xml')
    return

def process_directory(xml_directory):
    for filename in os.listdir('%s' % xml_directory):
        if filename[-5:] == '.jack':
            process_file(filename, xml_directory)

if __name__ == '__main__':
    script, to_be_compiled = argv

   # pdb.set_trace()

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
