<<<<<<< HEAD
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
        self.gui_mode = False
        self._setup_builtins()

    def _setup_builtins(self):
        import tkinter as tk
        from tkinter import messagebox, simpledialog

        # out 函数
        def builtin_out(text, msg_type="info"):
            text = str(text)
            msg_type = str(msg_type).lower()
            prefixes = {
                "warning": "[WARNING] ",
                "error": "[ERROR] ",
                "success": "[SUCCESS] ",
                "debug": "[DEBUG] ",
            }
            prefix = prefixes.get(msg_type, "")
            formatted = prefix + text

            if self.gui_mode:
                # GUI 模式：弹出 messagebox（不带图标）
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("消息", formatted)
                root.destroy()
            else:
                print(formatted)

        # in 函数
        def builtin_in(prompt=""):
            if self.gui_mode:
                root = tk.Tk()
                root.withdraw()
                answer = simpledialog.askstring("输入", str(prompt))
                root.destroy()
                return answer if answer is not None else ""
            else:
                return input(str(prompt))

        # outGUI 函数
        def builtin_outGUI(text, msg_type="info"):
            text = str(text)
            msg_type = str(msg_type).lower()

            if msg_type in ("info", "warning", "error"):
                if self.gui_mode:
                    root = tk.Tk()
                    root.withdraw()
                    if msg_type == "info":
                        messagebox.showinfo("信息", text)        # 纯文本，无自定义符号
                    elif msg_type == "warning":
                        messagebox.showwarning("警告", text)     # 纯文本，无自定义符号
                    elif msg_type == "error":
                        messagebox.showerror("错误", text)       # 纯文本，无自定义符号
                    root.destroy()
                else:
                    # 终端模式下是否保留符号？如果也不想要符号，可改为 print(text)
                    icons = {"info": "ℹ️ ", "warning": "⚠️ ", "error": "❌ "}
                    print(icons.get(msg_type, "") + text)
            else:
                print(text)

        # run_for_gui 函数：仅启动 GUI 主循环
        def builtin_run_for_gui():
            # 不需要启动 mainloop，因为 messagebox 已经是模态的
            pass

        self.env.set_function("out", builtin_out)
        self.env.set_function("in", builtin_in)
        self.env.set_function("outGUI", builtin_outGUI)
        self.env.set_function("run_for_gui", builtin_run_for_gui)

    def _start_gui(self):
        """启动一个简单的 GUI 窗口（跑步应用占位界面）"""
        try:
            import tkinter as tk
        except ImportError:
            print("[WARNING] tkinter 不可用，无法启动 GUI。")
            return

        root = tk.Tk()
        root.title("Mpple Running App")
        root.geometry("400x300")

        label = tk.Label(root, text="🏃‍♂️ Mpple Running App\n(演示界面)", font=("Arial", 16))
        label.pack(expand=True)

        root.mainloop()

    def _show_gui(self):
        """显示 GUI 日志窗口"""
        try:
            import tkinter as tk
        except ImportError:
            print("tkinter 不可用，无法显示 GUI。")
            for log in self.logs:
                print(log)
            return

        root = tk.Tk()
        root.title("MRA 运行日志")
        root.geometry("600x400")

        scrollbar = tk.Scrollbar(root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(root, yscrollcommand=scrollbar.set, wrap=tk.WORD, font=("Arial", 12))
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        for log in self.logs:
            text_widget.insert(tk.END, log + "\n")

        text_widget.config(state=tk.DISABLED)
        root.mainloop()

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
        elif isinstance(node, WhileLoop):
            while True:
                cond = self.evaluate(node.condition)
                if not cond:
                    break
                for stmt in node.body:
                    self.evaluate(stmt)
            return None
        else:
            raise RuntimeError(f"未知节点类型: {type(node)}")

    def execute(self, statements):
        # 检测是否包含 run_for_gui 调用
        def has_run_for_gui(node):
            if isinstance(node, FunctionCall) and node.name == "run_for_gui":
                return True
            if isinstance(node, ForLoop):
                return any(has_run_for_gui(s) for s in node.body)
            if isinstance(node, BinaryOp):
                return has_run_for_gui(node.left) or has_run_for_gui(node.right)
            return False

        for stmt in statements:
            if has_run_for_gui(stmt):
                self.gui_mode = True
                break

        # 执行所有语句
        for stmt in statements:
            self.evaluate(stmt)

=======
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
        self.gui_mode = False
        self._setup_builtins()

    def _setup_builtins(self):
        import tkinter as tk
        from tkinter import messagebox, simpledialog

        # out 函数
        def builtin_out(text, msg_type="info"):
            text = str(text)
            msg_type = str(msg_type).lower()
            prefixes = {
                "warning": "[WARNING] ",
                "error": "[ERROR] ",
                "success": "[SUCCESS] ",
                "debug": "[DEBUG] ",
            }
            prefix = prefixes.get(msg_type, "")
            formatted = prefix + text

            if self.gui_mode:
                # GUI 模式：弹出 messagebox（不带图标）
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("消息", formatted)
                root.destroy()
            else:
                print(formatted)

        # in 函数
        def builtin_in(prompt=""):
            if self.gui_mode:
                root = tk.Tk()
                root.withdraw()
                answer = simpledialog.askstring("输入", str(prompt))
                root.destroy()
                return answer if answer is not None else ""
            else:
                return input(str(prompt))

        # outGUI 函数
        def builtin_outGUI(text, msg_type="info"):
            text = str(text)
            msg_type = str(msg_type).lower()

            if msg_type in ("info", "warning", "error"):
                if self.gui_mode:
                    root = tk.Tk()
                    root.withdraw()
                    if msg_type == "info":
                        messagebox.showinfo("信息", text)        # 纯文本，无自定义符号
                    elif msg_type == "warning":
                        messagebox.showwarning("警告", text)     # 纯文本，无自定义符号
                    elif msg_type == "error":
                        messagebox.showerror("错误", text)       # 纯文本，无自定义符号
                    root.destroy()
                else:
                    # 终端模式下是否保留符号？如果也不想要符号，可改为 print(text)
                    icons = {"info": "ℹ️ ", "warning": "⚠️ ", "error": "❌ "}
                    print(icons.get(msg_type, "") + text)
            else:
                print(text)

        # run_for_gui 函数：仅启动 GUI 主循环
        def builtin_run_for_gui():
            # 不需要启动 mainloop，因为 messagebox 已经是模态的
            pass

        self.env.set_function("out", builtin_out)
        self.env.set_function("in", builtin_in)
        self.env.set_function("outGUI", builtin_outGUI)
        self.env.set_function("run_for_gui", builtin_run_for_gui)

    def _start_gui(self):
        """启动一个简单的 GUI 窗口（跑步应用占位界面）"""
        try:
            import tkinter as tk
        except ImportError:
            print("[WARNING] tkinter 不可用，无法启动 GUI。")
            return

        root = tk.Tk()
        root.title("Mpple Running App")
        root.geometry("400x300")

        label = tk.Label(root, text="🏃‍♂️ Mpple Running App\n(演示界面)", font=("Arial", 16))
        label.pack(expand=True)

        root.mainloop()

    def _show_gui(self):
        """显示 GUI 日志窗口"""
        try:
            import tkinter as tk
        except ImportError:
            print("tkinter 不可用，无法显示 GUI。")
            for log in self.logs:
                print(log)
            return

        root = tk.Tk()
        root.title("MRA 运行日志")
        root.geometry("600x400")

        scrollbar = tk.Scrollbar(root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(root, yscrollcommand=scrollbar.set, wrap=tk.WORD, font=("Arial", 12))
        text_widget.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        for log in self.logs:
            text_widget.insert(tk.END, log + "\n")

        text_widget.config(state=tk.DISABLED)
        root.mainloop()

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
        # 检测是否包含 run_for_gui 调用
        def has_run_for_gui(node):
            if isinstance(node, FunctionCall) and node.name == "run_for_gui":
                return True
            if isinstance(node, ForLoop):
                return any(has_run_for_gui(s) for s in node.body)
            if isinstance(node, BinaryOp):
                return has_run_for_gui(node.left) or has_run_for_gui(node.right)
            return False

        for stmt in statements:
            if has_run_for_gui(stmt):
                self.gui_mode = True
                break

        # 执行所有语句
        for stmt in statements:
            self.evaluate(stmt)

>>>>>>> 1d6029b (修复 GUI 模式程序无法正常退出的问题)
        # 注意：run_for_gui 执行时会进入 mainloop，因此这里不需要额外处理