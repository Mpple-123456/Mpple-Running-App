from src.lexer import lex
from src.parser import Parser
from src.interpreter import Interpreter

def run_mra_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    tokens = lex(code)
    parser = Parser(tokens)
    statements = parser.parse_program()
    interpreter = Interpreter()
    interpreter.execute(statements)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python main.py <文件.mra>")
    else:
        run_mra_file(sys.argv[1])