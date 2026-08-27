import json
import sys
from src.lexer import lex
from src.parser import Parser
from src.interpreter import Interpreter

def load_config(config_path="config.json"):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 默认配置
        return {
            "language": "zh",
            "gui_default": False,
            "log_level": "info",
            "prefix_style": {
                "warning": "[WARNING] ",
                "error": "[ERROR] ",
                "success": "[SUCCESS] ",
                "debug": "[DEBUG] "
            }
        }

def run_mra_file(filename, config):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    # 将配置传递给词法分析器（如果需要错误信息本地化）
    tokens = lex(code, language=config.get("language", "zh"))
    parser = Parser(tokens, language=config.get("language", "zh"))
    statements = parser.parse_program()
    interpreter = Interpreter(config=config)   # 传递整个配置给解释器
    interpreter.execute(statements)

if __name__ == "__main__":
    config = load_config()
    if len(sys.argv) < 2:
        print("用法: python main.py <文件.mra>")
    else:
        run_mra_file(sys.argv[1], config)