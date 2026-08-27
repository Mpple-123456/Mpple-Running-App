from src.ast_nodes import *

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
            raise SyntaxError(f"期望 {expected_type}，实际得到 {token[0]} ({token[1]})")
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
            else:
                statements.append(self.parse_expression())
        return statements

    def parse_assignment(self):
        """解析 let name = expr"""
        self.consume('LET')
        name = self.consume('IDENTIFIER')[1]
        self.consume('EQUALS')
        expr = self.parse_expression()
        return Assignment(name, expr)

    def parse_typed_assignment(self):
        """解析 set type name = expr"""
        self.consume('SET')
        type_token = self.peek()
        if type_token[0] not in ('TYPE_NUM', 'TYPE_CHAR', 'TYPE_STRING'):
            raise SyntaxError(f"未知类型: {type_token[1]}")
        self.consume(type_token[0])
        var_type = type_token[1]   # 'num', 'char', 'string'
        name = self.consume('IDENTIFIER')[1]
        self.consume('EQUALS')
        expr = self.parse_expression()
        return TypedAssignment(name, var_type, expr)

    def parse_expression(self):
        left = self.parse_binary_op()
        while self.peek()[0] in ('LT', 'GT', 'LTE', 'GTE', 'EQEQ', 'NEQ'):
            op = self.consume()[1]
            right = self.parse_binary_op()
            left = BinaryOp(left, op, right)
        return left

    def parse_binary_op(self):
        left = self.parse_primary()
        # 支持 + - * /
        while self.peek()[0] in ('PLUS', 'MINUS', 'MUL', 'DIV'):
            op = self.consume()[1]
            right = self.parse_primary()
            left = BinaryOp(left, op, right)
        return left

    def parse_primary(self):
        token = self.peek()
        if token[0] == 'STRING':
            self.consume('STRING')
            return StringLiteral(token[1])
        elif token[0] == 'CHAR':
            self.consume('CHAR')
            return StringLiteral(token[1])      # 字符也当作字符串，长度为1
        elif token[0] in ('INTEGER', 'FLOAT'):
            self.consume(token[0])
            return NumberLiteral(token[1])
        elif token[0] == 'IDENTIFIER':
            self.consume('IDENTIFIER')
            # 消息类型关键字视为字符串字面量
            if token[1] in self.MESSAGE_TYPES:
                return StringLiteral(token[1])
            # 函数调用
            if self.peek()[0] == 'LPAREN':
                return self.parse_function_call(token[1])
            # 普通变量
            return Identifier(token[1])
        elif token[0] == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        else:
            raise SyntaxError(f"无法解析的 token: {token}")

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
        # 解析初始化语句：只允许 set 或 let
        init_stmt = None
        if self.peek()[0] == 'SET':
            init_stmt = self.parse_typed_assignment()
        elif self.peek()[0] == 'LET':
            init_stmt = self.parse_assignment()
        else:
            raise SyntaxError("for 循环的初始化部分必须是 set 或 let 语句")
        self.consume('SEMICOLON')
        # 解析条件表达式
        condition = self.parse_expression()
        self.consume('SEMICOLON')
        # 解析更新表达式
        update_expr = self.parse_update() # 可以是 i += 1 或 i = i + 1
        self.consume('RPAREN')
        self.consume('LBRACE')
        # 解析循环体，直到 RBRACE
        body = []
        while self.peek()[0] != 'RBRACE':
            if self.peek()[0] == 'EOF':
                raise SyntaxError("未闭合的 for 循环体")
            if self.peek()[0] == 'LET':
                body.append(self.parse_assignment())
            elif self.peek()[0] == 'SET':
                body.append(self.parse_typed_assignment())
            elif self.peek()[0] == 'FOR':
                body.append(self.parse_for())
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
            if self.peek()[0] == 'LET':
                body.append(self.parse_assignment())
            elif self.peek()[0] == 'SET':
                body.append(self.parse_typed_assignment())
            elif self.peek()[0] == 'FOR':
                body.append(self.parse_for())
            elif self.peek()[0] == 'WHILE':
                body.append(self.parse_while())
            elif self.peek()[0] == 'IDENTIFIER':
                # 检查下一个 token 是否为 EQUALS，是则解析为普通赋值语句
                if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1][0] == 'EQUALS':
                    # 普通赋值： name = expr
                    name = self.consume('IDENTIFIER')[1]
                    self.consume('EQUALS')
                    expr = self.parse_expression()
                    body.append(Assignment(name, expr))
                else:
                    body.append(self.parse_expression())
            else:
                body.append(self.parse_expression())
        self.consume('RBRACE')
        return WhileLoop(condition, body)
    def parse_update(self):
        """
        解析 for 循环的更新部分，支持：
        - i = i + 1   (普通赋值)
        - i += 1      (复合赋值)
        """
        # 更新部分必须是赋值语句，否则报错更合适
        if self.peek()[0] != 'IDENTIFIER':
            raise SyntaxError(f"for 更新部分应以标识符开头，实际得到 {self.peek()}")

        name = self.consume('IDENTIFIER')[1]
        op_token = self.consume()   # 必须是 EQUALS 或复合赋值运算符
        op_type = op_token[0]
        op_value = op_token[1]

        if op_type not in ('EQUALS', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN'):
            raise SyntaxError(f"不支持的更新运算符: {op_value}")

        # 解析右值表达式
        right = self.parse_expression()

        if op_type == 'EQUALS':
            return Assignment(name, right)
        else:
            # 复合赋值：i += right  ->  i = i + right
            operator = op_value[0]   # '+', '-', '*', '/'
            left = Identifier(name)
            binary = BinaryOp(left, operator, right)
            return Assignment(name, binary)