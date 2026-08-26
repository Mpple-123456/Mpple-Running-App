# src/ast_nodes.py

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
        self.args = args          # 参数列表（AST 节点列表）

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left          # 左操作数（AST 节点）
        self.op = op              # 运算符字符串，如 '+', '-', '<', '==' 等
        self.right = right        # 右操作数（AST 节点）

class Assignment:                 # let 语句（无类型）
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class TypedAssignment:            # set 语句（带类型）
    def __init__(self, name, var_type, expr):
        self.name = name
        self.var_type = var_type  # 'num', 'char', 'string'
        self.expr = expr

class ForLoop:
    def __init__(self, init_stmt, condition, update_expr, body):
        self.init_stmt = init_stmt      # 初始化语句（Assignment 或 TypedAssignment）
        self.condition = condition      # 条件表达式（AST 节点）
        self.update_expr = update_expr  # 更新表达式（Assignment 或 BinaryOp）
        self.body = body                # 循环体语句列表（list of AST 节点）