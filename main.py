import sys
import os
from src.lexer import lex
from src.parser import Parser
from src.interpreter import Interpreter
from src.config import load_config, get_config

def run_mra_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    tokens = lex(code)
    parser = Parser(tokens)
    statements = parser.parse_program()
    interpreter = Interpreter()
    interpreter.execute(statements)

def process_file(filename):
    config = get_config()
    lang = config.get("language", "zh")
    error_prefix = "Error: " if lang == "en" else "错误: "
    return_cfg = config.get("return_format", {})
    prefix = return_cfg.get("prefix", "Return: ")
    success_text = return_cfg.get("success_text", {}).get(lang, "成功")
    print(f"\n=== 运行: {filename} ===")
    try:
        run_mra_file(filename)
        if return_cfg.get("enabled", True):
            print(f"{prefix}{success_text}")
    except Exception as e:
        print(f"{error_prefix}{e}")

def main():
    load_config()
    if len(sys.argv) < 2:
        print("用法: python main.py <文件1.mra> [文件2.mra ...] 或 python main.py <目录>")
        return

    targets = sys.argv[1:]
    for target in targets:
        if os.path.isdir(target):
            for root, dirs, files in os.walk(target):
                for file in sorted(files):
                    if file.endswith('.mra'):
                        process_file(os.path.join(root, file))
        elif os.path.isfile(target):
            process_file(target)
        else:
            print(f"警告: 路径不存在 - {target}")

if __name__ == "__main__":
    main()