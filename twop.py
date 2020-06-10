# twop.py - an interpreter for the Twop language
# Inspired by and structured based on https://ruslanspivak.com/lsbasi-part1/

# Token type definitions
NUM = 'NUM'
PLUS = 'PLUS'
MUL = 'MUL'
DIV = 'DIV'
MOD = 'MOD'
MINUS = 'MINUS'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
LBRAC = 'LBRAC'
RBRAC = 'RBRAC'
LCURL = 'LCURL'
RCURL = 'RCURL'
ID = 'ID'
ASSIGN = 'ASSIGN'
ARG_X = 'X'
ARG_Y = 'Y'
DEF = 'DEF'
OP = 'OP'
COLON = 'COLON'
EOF = 'EOF'

# Variable and operator defintions
REGS = {}
OPS = {}

# Reserved operators
RESERVED_CHARS = '+-*/=()[]\{\}:%'

# Token class for parsing
class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type, value=repr(self.value))

    def __repr__(self):
        return self.__str__()

# Lexer class for getting tokens
class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.curr_char = self.text[self.pos]

    # Advances the pointer to the next character, or sets to none at EOF
    def advance(self):
        self.pos += 1
        if self.pos >= len(self.text):
            self.curr_char = None
        else:
            self.curr_char = self.text[self.pos]

    # Skips whitespace characters
    def skip_whitespace(self):
        while self.curr_char is not None and self.curr_char.isspace():
            self.advance()

    # Parses numbers (all numbers are parsed as floats)
    def num(self):
        result = self.curr_char
        self.advance()
        while self.curr_char is not None and self.curr_char.isdigit():
            result += self.curr_char
            self.advance()
        if self.curr_char == '.':
            result += self.curr_char
            self.advance()
            while self.curr_char is not None and self.curr_char.isdigit():
                result += self.curr_char
                self.advance()
        return Token(NUM, float(result))

    # Checks to see if characters following x are a valid operator definition
    def check_def(self):
        self.advance()
        if self.curr_char in RESERVED_CHARS:
            return Token(ARG_X, 'X')
        op_char = self.curr_char
        if op_char.isspace() or op_char.isdigit() or op_char.isalpha():
            return Token(ARG_X, 'X')
        if self.text[self.pos + 1] == 'y':
            self.advance()
            self.advance()
            return Token(DEF, op_char)
        else:
            return Token(ARG_X, 'X')

    # Gets the next token for the parser
    def get_next_token(self):
        while self.curr_char is not None:
            if self.curr_char.isspace():
                self.skip_whitespace()
                continue
            if self.curr_char.isdigit():
                return self.num()
            if self.curr_char == '+':
                self.advance()
                return Token(PLUS, '+')
            if self.curr_char == '-':
                self.advance()
                return Token(MINUS, '-')
            if self.curr_char == '*':
                self.advance()
                return Token(MUL, '*')
            if self.curr_char == '/':
                self.advance()
                return Token(DIV, '/')
            if self.curr_char == '%':
                self.advance()
                return Token(MOD, '%')
            if self.curr_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.curr_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            if self.curr_char == '[':
                self.advance()
                return Token(LBRAC, '[')
            if self.curr_char == ']':
                self.advance()
                return Token(RBRAC, ']')
            if self.curr_char == '{':
                self.advance()
                return Token(LCURL, '{')
            if self.curr_char == '}':
                self.advance()
                return Token(RCURL, '}')
            if self.curr_char == '=':
                self.advance()
                return Token(ASSIGN, '=')
            if self.curr_char == ':':
                self.advance()
                return Token(COLON, ':')
            if self.curr_char == 'x':
                return self.check_def()
            if self.curr_char == 'y':
                self.advance()
                return Token(ARG_Y, 'Y')
            if self.curr_char.isalpha():
                curr = self.curr_char
                if curr == 'y':
                    raise Exception("Invalid ID: y is a reserved character")
                self.advance()
                return Token(ID, curr)
            else:
                curr = self.curr_char
                self.advance()
                return Token(OP, curr)
        return Token(EOF, None)

# Abstract parent class for AST classes
class AST(object):
    def visit(self):
        pass

# Program AST head
class Program(AST):
    def __init__(self, statements):
        self.statements = statements

    def visit(self,x=None,y=None):
        for stat in self.statements:
            stat.visit()

# Binary operator AST node
class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.token = op
        self.right = right

    def visit(self, x=None, y=None):
        if self.token.type == PLUS:
            return self.left.visit(x,y) + self.right.visit(x,y)
        elif self.token.type == MINUS:
            return self.left.visit(x,y) - self.right.visit(x,y)
        elif self.token.type == MUL:
            return self.left.visit(x,y) * self.right.visit(x,y)
        elif self.token.type == DIV:
            return self.left.visit(x,y) / self.right.visit(x,y)
        elif self.token.type == MOD:
            return self.left.visit(x,y) % self.right.visit(x,y)

# Numerical AST node
class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def visit(self, x=None, y=None):
        return self.value

# Variable ID AST node
class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def visit(self,x=None,y=None):
        return REGS.get(self.value)

# Assignment statement AST node
class Assign(AST):
    def __init__(self, left, token, right):
        self.left = left
        self.token = token
        self.right = right

    def visit(self,x=None,y=None):
        REGS[self.left.value] = self.right.visit()

# Math expression AST node
class Math_Expr(AST):
    def __init__(self, head):
        self.head = head

    def visit(self,x=None,y=None):
        print(self.head.visit())

# Operator defintion AST node
class OpDef(AST):
    def __init__(self, op, content):
        self.token = op
        self.op = op
        self.content = content

    def visit(self,x=None,y=None):
        OPS[self.token.value] = self.content

# Operator call AST node
class OpCall(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

    def visit(self,x=None,y=None):
        if self.op.value in OPS.keys():
            return OPS[self.token.value].visit(self.left.visit(), self.right.visit())
        else:
            raise Exception("Operator not found: " + self.token.value)

class X(AST):
    def visit(self,x=None,y=None):
        return x

class Y(AST):
    def visit(self,x=None,y=None):
        return y

# Parser class; runs through the CFG heirarchy and produces an AST
class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.curr_token = self.lexer.get_next_token()

    # Consumes the current token if it's the expected type
    def eat(self, type):
        if self.curr_token.type == type:
            self.curr_token = self.lexer.get_next_token()
        else:
            raise Exception("Invalid token: expected " + type + ", got " + self.curr_token.type)

    # program: statement*
    def program(self):
        #print("program")
        result = []
        while self.curr_token.type != EOF:
            result.append(self.statement())
        return Program(result)

    # statement: (math_expr | assignment | def) NEWLINE
    def statement(self):
        #print("statement")
        tok = self.curr_token
        if tok.type == LBRAC:
            self.eat(LBRAC)
            if self.curr_token.type == DEF:
                node = self.op_def()
            else:
                node = self.assignment()
            self.eat(RBRAC)
            return node
        else:
            node = self.math_expr()
            return node

    # op_def : LBRAC X OP Y COLON expr RBRAC
    def op_def(self):
        #print("opdef")
        tok = self.curr_token
        self.eat(DEF)
        self.eat(COLON)
        definition = self.expr()
        return OpDef(tok, definition)

    # assignment : LBRAC variable ASSIGN expr RBRAC
    def assignment(self):
        #print("assignment")
        left = self.variable()
        tok = self.curr_token
        self.eat(ASSIGN)
        right = self.expr()
        return Assign(left, tok, right)

    # math_expr: LCURL expr RCURL
    def math_expr(self):
        #print("math_expr")
        self.eat(LCURL)
        node = self.expr()
        self.eat(RCURL)
        return Math_Expr(node)

    # expr : term ((PLUS | MINUS) term)*
    def expr(self):
        #print("expr")
        node = self.term()

        while self.curr_token.type in (PLUS, MINUS):
            tok = self.curr_token
            if tok.type == PLUS:
                self.eat(PLUS)
            elif tok.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=tok, right=self.term())

        return node

    # term : factor ((MUL | DIV | MOD) factor)*
    def term(self):
        #print("term")
        node = self.factor()

        while self.curr_token.type in (MUL, DIV, MOD):
            tok = self.curr_token
            if tok.type == MUL:
                self.eat(MUL)
            elif tok.type == DIV:
                self.eat(DIV)
            elif tok.type == MOD:
                self.eat(MOD)

            node = BinOp(left=node, op=tok, right=self.factor())

        return node

    def factor(self):
        #print("factor")
        node = self.op_arg()

        while self.curr_token.type == OP:
            tok = self.curr_token
            self.eat(OP)
            node = OpCall(left=node, op=tok, right=self.op_arg())

        return node

    # op_arg : (LPAREN expr RPAREN) | NUM | variable
    def op_arg(self):
        #print("op_arg")
        tok = self.curr_token
        if tok.type == LPAREN:
            self.eat(LPAREN)
            result = self.expr()
            self.eat(RPAREN)
            return result
        if tok.type == NUM:
            self.eat(NUM)
            return Num(tok)
        if tok.type == ARG_X:
            self.eat(ARG_X)
            return X()
        if tok.type == ARG_Y:
            self.eat(ARG_Y)
            return Y()
        else:
            node = self.variable()
            return node

    # variable: ID
    def variable(self):
        #print("var")
        var = Var(self.curr_token)
        self.eat(ID)
        return var

    def parse(self):
        node = self.program()
        if self.curr_token.type != EOF:
            raise Exception("Expected EOF")
        return node

class Interpreter(object):
    def __init__(self, parser):
        self.parser = parser

    def interpret(self):
        tree = self.parser.parse()
        if tree is None:
            return ''
        return tree.visit()

def main():
    while True:
        try:
            text = input('calc> ')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        interpreter.interpret()

if __name__ == '__main__':
    main()
