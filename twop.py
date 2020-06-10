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
EOF = 'EOF'

# Variable registers
REGS = {}

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
            if self.curr_char.isalpha():
                curr = self.curr_char
                self.advance()
                return Token(ID, curr)

            raise Exception("Invalid character")
        return Token(EOF, None)

# Abstract parent class for AST classes
class AST(object):
    def visit(self):
        pass

# Program AST head
class Program(AST):
    def __init__(self, statements):
        self.statements = statements

    def visit(self):
        for stat in self.statements:
            stat.visit()
        return "done"

# Binary operator AST node
class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.token = op
        self.right = right

    def visit(self):
        if self.token.type == PLUS:
            return self.left.visit() + self.right.visit()
        elif self.token.type == MINUS:
            return self.left.visit() - self.right.visit()
        elif self.token.type == MUL:
            return self.left.visit() * self.right.visit()
        elif self.token.type == DIV:
            return self.left.visit() / self.right.visit()
        elif self.token.type == MOD:
            return self.left.visit() % self.right.visit()

# Numerical AST node
class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def visit(self):
        return self.value

# Variable ID AST node
class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

    def visit(self):
        return REGS[self.value]

# Assignment statement AST node
class Assign(AST):
    def __init__(self, left, token, right):
        self.left = left
        self.token = token
        self.right = right

    def visit(self):
        REGS[self.left.value] = self.right.visit()

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
        result = []
        while self.curr_token.type != EOF:
            result.append(self.statement())
        return Program(result)

    # statement: (expr | assignment | def) NEWLINE
    def statement(self):
        tok = self.curr_token
        if tok.type == LBRAC:
            self.eat(LBRAC)
            node = self.assignment()
            self.eat(RBRAC)
            return node
        else:
            node = self.expr()
            return node

    # assignment : LBRAC variable ASSIGN expr RBRAC
    def assignment(self):
        left = self.variable()
        tok = self.curr_token
        self.eat(ASSIGN)
        right = self.expr()
        return Assign(left, tok, right)

    # expr : term ((PLUS | MINUS) term)*
    def expr(self):
        self.eat(LCURL)
        node = self.term()

        while self.curr_token.type in (PLUS, MINUS):
            tok = self.curr_token
            if tok.type == PLUS:
                self.eat(PLUS)
            elif tok.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=tok, right=self.term())

        self.eat(RCURL)

        return node

    # term : factor ((MUL | DIV | MOD) factor)*
    def term(self):
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

    # factor : (LPAREN expr RPAREN) | NUM | variable
    def factor(self):
        tok = self.curr_token
        if tok.type == LPAREN:
            self.eat(LPAREN)
            result = self.expr()
            self.eat(RPAREN)
            return result
        if tok.type == NUM:
            self.eat(NUM)
            return Num(tok)
        else:
            node = self.variable()
            return node

    # variable: ID
    def variable(self):
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
        result = interpreter.interpret()
        print(result)

if __name__ == '__main__':
    main()
