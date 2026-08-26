from src.ast_nodes import *

class Environment:
    def __init__(self):
        self.vars = {}      # 变量名 -> 值
        self.types = {}     # 变量名 -> 类型字符串
        self.functions = {} # 函数名 -> Python 可调用对象

    def get_var(self, name):
        if name in self.vars:
            return self.vars[name]
        raise NameError(f"变量未定义: {name}")

    def set_var(self, name, value, var_type=None):
        self.vars[name] = value
        if var_type:
            self.types[name] = var_type

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        raise NameError(f"函数未定义: {name}")

    def set_function(self, name, func):
        self.functions[name] = func

class Interpreter:
    def __init__(self):
        self.env = Environment()
        self._setup_builtins()

    def _setup_builtins(self):
        def builtin_out(text, msg_type="info"):
            text = str(text)   # 允许输出任何类型
            msg_type = str(msg_type).lower()
            prefixes = {
                "warning": "[WARNING] ",
                "error": "[ERROR] ",
                "success": "[SUCCESS] ",
                "debug": "[DEBUG] ",
            }
            prefix = prefixes.get(msg_type, "")
            print(prefix + text)

        def builtin_in(prompt=""):
            return input(str(prompt))

        self.env.set_function("out", builtin_out)
        self.env.set_function("in", builtin_in)

    def evaluate(self, node):
        if isinstance(node, StringLiteral):
            return node.value
        elif isinstance(node, NumberLiteral):
            return node.value
        elif isinstance(node, Identifier):
            return self.env.get_var(node.name)
        elif isinstance(node, BinaryOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            op = node.op
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                if right == 0:
                    raise ZeroDivisionError("除以零")
                return left / right
            elif op in ('<', '>', '<=', '>=', '==', '!='):
                if op == '<': return left < right
                if op == '>': return left > right
                if op == '<=': return left <= right
                if op == '>=': return left >= right
                if op == '==': return left == right
                if op == '!=': return left != right
            else:
                raise RuntimeError(f"不支持的运算符: {node.op}")
        elif isinstance(node, FunctionCall):
            func = self.env.get_function(node.name)
            args = [self.evaluate(arg) for arg in node.args]
            return func(*args)
        elif isinstance(node, Assignment):
            value = self.evaluate(node.expr)
            self.env.set_var(node.name, value)
            return value
        elif isinstance(node, TypedAssignment):
            value = self.evaluate(node.expr)
            # 简单类型检查
            if node.var_type == 'num' and not isinstance(value, (int, float)):
                raise TypeError(f"变量 {node.name} 需要数字类型，但得到 {type(value).__name__}")
            if node.var_type == 'char' and not (isinstance(value, str) and len(value) == 1):
                raise TypeError(f"变量 {node.name} 需要字符类型")
            if node.var_type == 'string' and not isinstance(value, str):
                raise TypeError(f"变量 {node.name} 需要字符串类型")
            self.env.set_var(node.name, value, node.var_type)
            return value
        elif isinstance(node, ForLoop):
            # 执行初始化
            self.evaluate(node.init_stmt)
            # 循环执行
            while True:
                # 检查条件
                cond = self.evaluate(node.condition)
                if not cond:
                    break
                # 执行循环体
                for stmt in node.body:
                    self.evaluate(stmt)
                # 执行更新
                self.evaluate(node.update_expr)
            return None
        else:
            raise RuntimeError(f"未知节点类型: {type(node)}")

    def execute(self, statements):
        for stmt in statements:
            self.evaluate(stmt)