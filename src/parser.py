from src.ast_nodes import *
from src.errors import get_error_message

class Parser:
    MESSAGE_TYPES = {'info', 'warning', 'error', 'success', 'debug'}

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', '')

    def consume(self, expected_type=None):
        token = self.peek()
        if expected_type and token[0] != expected_type:
            raise SyntaxError(get_error_message("expected_token", expected=expected_type, actual=token[0]))
        self.pos += 1
        return token

    def parse_program(self):
        statements = []
        while self.pos < len(self.tokens):
            if self.peek()[0] == 'LET':
                statements.append(self.parse_assignment())
            elif self.peek()[0] == 'SET':
                statements.append(self.parse_typed_assignment())
            elif self.peek()[0] == 'FOR':
                statements.append(self.parse_for())
            elif self.peek()[0] == 'WHILE':
                statements.append(self.parse_while())
            elif self.peek()[0] == 'IDENTIFIER':
                # 处理普通赋值语句
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1][0] == 'EQUALS':
                    statements.append(self.parse_update())
                else:
                    statements.append(self.parse_expression())
            else:
                statements.append(self.parse_expression())
        return statements

    def parse_assignment(self):
        self.consume('LET')
        name = self.consume('IDENTIFIER')[1]
        self.consume('EQUALS')
        expr = self.parse_expression()
        return Assignment(name, expr)

    def parse_typed_assignment(self):
        self.consume('SET')
        type_token = self.peek()
        if type_token[0] not in ('TYPE_NUM', 'TYPE_CHAR', 'TYPE_STRING'):
            raise SyntaxError(get_error_message("unknown_type", type=type_token[1]))
        self.consume(type_token[0])
        var_type = type_token[1]
        name = self.consume('IDENTIFIER')[1]
        self.consume('EQUALS')
        expr = self.parse_expression()
        return TypedAssignment(name, var_type, expr)

    def parse_expression(self):
        return self.parse_binary_op()

    def parse_binary_op(self):
        left = self.parse_primary()
        while self.peek()[0] in ('PLUS', 'MINUS', 'MUL', 'DIV'):
            op = self.consume()[1]
            right = self.parse_primary()
            left = BinaryOp(left, op, right)
        if self.peek()[0] in ('LT', 'GT', 'LTE', 'GTE', 'EQEQ', 'NEQ'):
            op = self.consume()[1]
            right = self.parse_binary_op()
            left = BinaryOp(left, op, right)
        return left

    def parse_primary(self):
        token = self.peek()
        if token[0] == 'STRING':
            self.consume('STRING')
            return StringLiteral(token[1])
        elif token[0] == 'CHAR':
            self.consume('CHAR')
            return StringLiteral(token[1])
        elif token[0] in ('INTEGER', 'FLOAT'):
            self.consume(token[0])
            return NumberLiteral(token[1])
        elif token[0] == 'IDENTIFIER':
            self.consume('IDENTIFIER')
            if token[1] in self.MESSAGE_TYPES:
                return StringLiteral(token[1])
            if self.peek()[0] == 'LPAREN':
                return self.parse_function_call(token[1])
            return Identifier(token[1])
        elif token[0] == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        else:
            raise SyntaxError(get_error_message("parse_error", token=token))

    def parse_function_call(self, name):
        self.consume('LPAREN')
        args = []
        if self.peek()[0] != 'RPAREN':
            args.append(self.parse_expression())
            while self.peek()[0] == 'COMMA':
                self.consume('COMMA')
                args.append(self.parse_expression())
        self.consume('RPAREN')
        return FunctionCall(name, args)

    def parse_for(self):
        self.consume('FOR')
        self.consume('LPAREN')
        if self.peek()[0] == 'SET':
            init_stmt = self.parse_typed_assignment()
        elif self.peek()[0] == 'LET':
            init_stmt = self.parse_assignment()
        else:
            raise SyntaxError(get_error_message("for_init_error"))
        self.consume('SEMICOLON')
        condition = self.parse_expression()
        self.consume('SEMICOLON')
        update_expr = self.parse_update()
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while self.peek()[0] != 'RBRACE':
            if self.peek()[0] == 'EOF':
                raise SyntaxError(get_error_message("expected_token", expected='RBRACE', actual='EOF'))
            if self.peek()[0] == 'LET':
                body.append(self.parse_assignment())
            elif self.peek()[0] == 'SET':
                body.append(self.parse_typed_assignment())
            elif self.peek()[0] == 'FOR':
                body.append(self.parse_for())
            elif self.peek()[0] == 'WHILE':
                body.append(self.parse_while())
            elif self.peek()[0] == 'IDENTIFIER':
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1][0] in ('EQUALS', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN'):
                    body.append(self.parse_update())
                else:
                    body.append(self.parse_expression())
            else:
                body.append(self.parse_expression())
        self.consume('RBRACE')
        return ForLoop(init_stmt, condition, update_expr, body)

    def parse_while(self):
        self.consume('WHILE')
        self.consume('LPAREN')
        condition = self.parse_expression()
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while self.peek()[0] != 'RBRACE':
            if self.peek()[0] == 'EOF':
                raise SyntaxError(get_error_message("expected_token", expected='RBRACE', actual='EOF'))
            if self.peek()[0] == 'LET':
                body.append(self.parse_assignment())
            elif self.peek()[0] == 'SET':
                body.append(self.parse_typed_assignment())
            elif self.peek()[0] == 'FOR':
                body.append(self.parse_for())
            elif self.peek()[0] == 'WHILE':
                body.append(self.parse_while())
            elif self.peek()[0] == 'IDENTIFIER':
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1][0] in ('EQUALS', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN'):
                    body.append(self.parse_update())
                else:
                    body.append(self.parse_expression())
            else:
                body.append(self.parse_expression())
        self.consume('RBRACE')
        return WhileLoop(condition, body)

    def parse_update(self):
        if self.peek()[0] != 'IDENTIFIER':
            raise SyntaxError(get_error_message("parse_error", token=self.peek()))
        name = self.consume('IDENTIFIER')[1]
        op_token = self.consume()
        op_type = op_token[0]
        if op_type not in ('EQUALS', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN'):
            raise SyntaxError(get_error_message("unsupported_update_operator", op=op_token[1]))
        right = self.parse_expression()
        if op_type == 'EQUALS':
            return Assignment(name, right)
        else:
            operator = op_token[1][0]
            left = Identifier(name)
            binary = BinaryOp(left, operator, right)
            return Assignment(name, binary)