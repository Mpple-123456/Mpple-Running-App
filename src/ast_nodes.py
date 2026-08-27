class StringLiteral:
    def __init__(self, value):
        self.value = value

class NumberLiteral:
    def __init__(self, value):
        self.value = value

class Identifier:
    def __init__(self, name):
        self.name = name

class FunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Assignment:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class TypedAssignment:
    def __init__(self, name, var_type, expr):
        self.name = name
        self.var_type = var_type
        self.expr = expr

class ForLoop:
    def __init__(self, init_stmt, condition, update_expr, body):
        self.init_stmt = init_stmt
        self.condition = condition
        self.update_expr = update_expr
        self.body = body

class WhileLoop:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body