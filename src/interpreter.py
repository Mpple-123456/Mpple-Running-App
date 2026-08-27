from src.ast_nodes import *
from src.config import get_config
from src.errors import get_error_message

class Environment:
    def __init__(self):
        self.vars = {}
        self.types = {}
        self.functions = {}

    def get_var(self, name):
        if name in self.vars:
            return self.vars[name]
        raise NameError(get_error_message("variable_undefined", name=name))

    def set_var(self, name, value, var_type=None):
        self.vars[name] = value
        if var_type:
            self.types[name] = var_type

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        raise NameError(get_error_message("function_undefined", name=name))

    def set_function(self, name, func):
        self.functions[name] = func

class Interpreter:
    def __init__(self):
        self.env = Environment()
        self.gui_mode = False
        self._setup_builtins()

    def _setup_builtins(self):
        config = get_config()
        prefixes = config.get("prefix_style", {
            "warning": "[WARNING] ",
            "error": "[ERROR] ",
            "success": "[SUCCESS] ",
            "debug": "[DEBUG] ",
        })

        def builtin_out(text, msg_type="info"):
            text = str(text)
            msg_type = str(msg_type).lower()
            prefix = prefixes.get(msg_type, "")
            formatted = prefix + text
            if self.gui_mode:
                import tkinter as tk
                from tkinter import messagebox
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("消息", formatted)
                root.destroy()
            else:
                print(formatted)

        def builtin_in(prompt=""):
            if self.gui_mode:
                import tkinter as tk
                from tkinter import simpledialog
                root = tk.Tk()
                root.withdraw()
                answer = simpledialog.askstring("输入", str(prompt))
                root.destroy()
                return answer if answer is not None else ""
            else:
                return input(str(prompt))

        def builtin_outGUI(text, msg_type="info"):
            text = str(text)
            msg_type = str(msg_type).lower()
            if msg_type in ("info", "warning", "error"):
                if self.gui_mode:
                    import tkinter as tk
                    from tkinter import messagebox
                    root = tk.Tk()
                    root.withdraw()
                    if msg_type == "info":
                        messagebox.showinfo("信息", text)
                    elif msg_type == "warning":
                        messagebox.showwarning("警告", text)
                    elif msg_type == "error":
                        messagebox.showerror("错误", text)
                    root.destroy()
                else:
                    icons = {"info": "ℹ️ ", "warning": "⚠️ ", "error": "❌ "}
                    print(icons.get(msg_type, "") + text)
            else:
                print(text)

        def builtin_run_for_gui():
            pass

        self.env.set_function("out", builtin_out)
        self.env.set_function("in", builtin_in)
        self.env.set_function("outGUI", builtin_outGUI)
        self.env.set_function("run_for_gui", builtin_run_for_gui)

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
                    raise ZeroDivisionError(get_error_message("division_by_zero"))
                return left / right
            elif op in ('<', '>', '<=', '>=', '==', '!='):
                if op == '<': return left < right
                if op == '>': return left > right
                if op == '<=': return left <= right
                if op == '>=': return left >= right
                if op == '==': return left == right
                if op == '!=': return left != right
            else:
                raise RuntimeError(get_error_message("unsupported_operator", op=op))
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
            if node.var_type == 'num' and not isinstance(value, (int, float)):
                raise TypeError(get_error_message("type_mismatch_num", name=node.name, type=type(value).__name__))
            if node.var_type == 'char' and not (isinstance(value, str) and len(value) == 1):
                raise TypeError(get_error_message("type_mismatch_char", name=node.name))
            if node.var_type == 'string' and not isinstance(value, str):
                raise TypeError(get_error_message("type_mismatch_string", name=node.name))
            self.env.set_var(node.name, value, node.var_type)
            return value
        elif isinstance(node, ForLoop):
            if node.init_stmt:
                self.evaluate(node.init_stmt)
            while True:
                cond = self.evaluate(node.condition)
                if not cond:
                    break
                for stmt in node.body:
                    self.evaluate(stmt)
                self.evaluate(node.update_expr)
            return None
        elif isinstance(node, WhileLoop):
            while True:
                cond = self.evaluate(node.condition)
                if not cond:
                    break
                for stmt in node.body:
                    self.evaluate(stmt)
            return None
        else:
            raise RuntimeError(get_error_message("unknown_node", node_type=type(node).__name__))

    def execute(self, statements):
        def has_run_for_gui(node):
            if isinstance(node, FunctionCall) and node.name == "run_for_gui":
                return True
            if isinstance(node, ForLoop):
                if node.init_stmt and has_run_for_gui(node.init_stmt):
                    return True
                if has_run_for_gui(node.condition):
                    return True
                if has_run_for_gui(node.update_expr):
                    return True
                return any(has_run_for_gui(s) for s in node.body)
            if isinstance(node, WhileLoop):
                if has_run_for_gui(node.condition):
                    return True
                return any(has_run_for_gui(s) for s in node.body)
            if isinstance(node, BinaryOp):
                return has_run_for_gui(node.left) or has_run_for_gui(node.right)
            return False

        for stmt in statements:
            if has_run_for_gui(stmt):
                self.gui_mode = True
                break

        for stmt in statements:
            self.evaluate(stmt)