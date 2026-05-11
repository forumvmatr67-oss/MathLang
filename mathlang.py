import sys
import re
import math

# ---------------------------- Токенизатор ----------------------------
def tokenize(code):
    token_specs = [
        ('NUMBER',   r'\d+(?:\.\d+)?'),
        ('NAME',     r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('OP',       r'[+\-*/^]'),
        ('ASSIGN',   r'='),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('COMMA',    r','),
        ('PRINT',    r'print\b'),
        ('FUNC',     r'func\b'),
        ('NEWLINE',  r'\n'),
        ('SKIP',     r'[ \t]+'),
        ('COMMENT',  r'#.*'),
        ('MISMATCH', r'.'),
    ]
    tok_re = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specs)
    line_num = 1
    for mo in re.finditer(tok_re, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NEWLINE':
            line_num += 1
            yield ('NEWLINE', value)
        elif kind == 'SKIP' or kind == 'COMMENT':
            continue
        elif kind == 'NUMBER':
            yield ('NUMBER', float(value) if '.' in value else int(value))
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected character {value!r} at line {line_num}')
        else:
            yield (kind, value)
    yield ('EOF', '')

# ---------------------------- AST узлы ----------------------------
class BinOp:
    __slots__ = ('left', 'op', 'right')
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Number:
    __slots__ = ('value',)
    def __init__(self, value):
        self.value = value

class Variable:
    __slots__ = ('name',)
    def __init__(self, name):
        self.name = name

class FuncCall:
    __slots__ = ('name', 'args')
    def __init__(self, name, args):
        self.name = name
        self.args = args

# ---------------------------- Парсер ----------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '')

    def consume(self, expected_kind=None):
        tok = self.current()
        if expected_kind and tok[0] != expected_kind:
            raise SyntaxError(f'Expected {expected_kind}, got {tok[0]}')
        self.pos += 1
        return tok

    def parse_program(self):
        statements = []
        while self.current()[0] != 'EOF':
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            if self.current()[0] == 'NEWLINE':
                self.consume('NEWLINE')
        return statements

    def parse_statement(self):
        tok = self.current()
        if tok[0] == 'PRINT':
            return self.parse_print()
        elif tok[0] == 'FUNC':
            return self.parse_func_def()
        elif tok[0] == 'NAME' and self.peek_next() == 'ASSIGN':
            return self.parse_assignment()
        else:
            expr = self.parse_expr()
            return ('EVAL', expr)

    def peek_next(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos+1][0]
        return None

    def parse_print(self):
        self.consume('PRINT')
        expr = self.parse_expr()
        return ('PRINT', expr)

    def parse_func_def(self):
        self.consume('FUNC')
        name = self.consume('NAME')[1]
        self.consume('LPAREN')
        param = self.consume('NAME')[1]
        self.consume('RPAREN')
        self.consume('ASSIGN')
        body = self.parse_expr()
        return ('FUNC_DEF', name, param, body)

    def parse_assignment(self):
        name = self.consume('NAME')[1]
        self.consume('ASSIGN')
        expr = self.parse_expr()
        return ('ASSIGN', name, expr)

    def parse_expr(self):
        return self.parse_add_sub()

    def parse_add_sub(self):
        node = self.parse_mul_div()
        while True:
            tok = self.current()
            if tok[0] == 'OP' and tok[1] in ('+', '-'):
                self.consume('OP')
                right = self.parse_mul_div()
                node = BinOp(node, tok[1], right)
            else:
                break
        return node

    def parse_mul_div(self):
        node = self.parse_power()
        while True:
            tok = self.current()
            if tok[0] == 'OP' and tok[1] in ('*', '/'):
                self.consume('OP')
                right = self.parse_power()
                node = BinOp(node, tok[1], right)
            else:
                break
        return node

    def parse_power(self):
        node = self.parse_atom()
        if self.current()[0] == 'OP' and self.current()[1] == '^':
            self.consume('OP')
            right = self.parse_power()
            node = BinOp(node, '^', right)
        return node

    def parse_atom(self):
        tok = self.current()
        if tok[0] == 'NUMBER':
            self.consume('NUMBER')
            return Number(tok[1])
        elif tok[0] == 'NAME':
            name = tok[1]
            self.consume('NAME')
            if self.current()[0] == 'LPAREN':
                self.consume('LPAREN')
                args = []
                if self.current()[0] != 'RPAREN':
                    args.append(self.parse_expr())
                    while self.current()[0] == 'COMMA':
                        self.consume('COMMA')
                        args.append(self.parse_expr())
                self.consume('RPAREN')
                return FuncCall(name, args)
            else:
                return Variable(name)
        elif tok[0] == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_expr()
            self.consume('RPAREN')
            return node
        else:
            raise SyntaxError(f'Unexpected token {tok}')

# ---------------------------- Интерпретатор ----------------------------
class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.builtins = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'sqrt': math.sqrt, 'log': math.log, 'exp': math.exp,
            'abs': abs, 'floor': math.floor, 'ceil': math.ceil,
        }

    def evaluate(self, node):
        if isinstance(node, Number):
            return node.value
        elif isinstance(node, Variable):
            if node.name in self.variables:
                return self.variables[node.name]
            raise NameError(f'Unknown variable {node.name}')
        elif isinstance(node, BinOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == '+': return left + right
            elif node.op == '-': return left - right
            elif node.op == '*': return left * right
            elif node.op == '/': return left / right
            elif node.op == '^': return left ** right
            else: raise ValueError(f'Unknown operator {node.op}')
        elif isinstance(node, FuncCall):
            if node.name in self.builtins:
                if len(node.args) != 1:
                    raise TypeError(f'{node.name} expects 1 argument')
                arg = self.evaluate(node.args[0])
                return self.builtins[node.name](arg)
            elif node.name in self.functions:
                param, body = self.functions[node.name]
                if len(node.args) != 1:
                    raise TypeError(f'Function {node.name} expects 1 argument')
                arg_val = self.evaluate(node.args[0])
                old_vars = self.variables.copy()
                self.variables[param] = arg_val
                result = self.evaluate(body)
                self.variables = old_vars
                return result
            else:
                raise NameError(f'Unknown function {node.name}')
        else:
            raise RuntimeError(f'Unknown AST node {type(node)}')

    def run(self, statements):
        for stmt in statements:
            if stmt[0] == 'ASSIGN':
                _, name, expr = stmt
                self.variables[name] = self.evaluate(expr)
            elif stmt[0] == 'PRINT':
                _, expr = stmt
                print(self.evaluate(expr))
            elif stmt[0] == 'FUNC_DEF':
                _, name, param, body = stmt
                self.functions[name] = (param, body)
            elif stmt[0] == 'EVAL':
                _, expr = stmt
                res = self.evaluate(expr)
                if res is not None:
                    print(res)

# ---------------------------- Запуск файла ----------------------------
def run_math_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    tokens = list(tokenize(code))
    tokens = [t for t in tokens if t[0] != 'NEWLINE' or t[1] != '\n']
    parser = Parser(tokens)
    statements = parser.parse_program()
    interp = Interpreter()
    interp.run(statements)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python mathlang.py file.math')
        sys.exit(1)
    run_math_file(sys.argv[1])
