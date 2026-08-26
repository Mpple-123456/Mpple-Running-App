import re

def lex(code):
    tokens = []
    i = 0
    while i < len(code):
        # 跳过空白字符
        if code[i].isspace():
            i += 1
            continue

        # 括号和结构符号
        if code[i] == '(':
            tokens.append(('LPAREN', '(')); i += 1
        elif code[i] == ')':
            tokens.append(('RPAREN', ')')); i += 1
        elif code[i] == '{':
            tokens.append(('LBRACE', '{')); i += 1
        elif code[i] == '}':
            tokens.append(('RBRACE', '}')); i += 1
        elif code[i] == ';':
            tokens.append(('SEMICOLON', ';')); i += 1
        elif code[i] == ',':
            tokens.append(('COMMA', ',')); i += 1

        # 复合赋值运算符（必须在单个运算符之前检查）
        elif code[i] == '+':
            if i + 1 < len(code) and code[i+1] == '=':
                tokens.append(('PLUS_ASSIGN', '+=')); i += 2
            else:
                tokens.append(('PLUS', '+')); i += 1
        elif code[i] == '-':
            if i + 1 < len(code) and code[i+1] == '=':
                tokens.append(('MINUS_ASSIGN', '-=')); i += 2
            else:
                tokens.append(('MINUS', '-')); i += 1
        elif code[i] == '*':
            if i + 1 < len(code) and code[i+1] == '=':
                tokens.append(('MUL_ASSIGN', '*=')); i += 2
            else:
                tokens.append(('MUL', '*')); i += 1
        elif code[i] == '/':
            if i + 1 < len(code) and code[i+1] == '=':
                tokens.append(('DIV_ASSIGN', '/=')); i += 2
            else:
                tokens.append(('DIV', '/')); i += 1

        # 等号和比较运算符
        elif code[i] == '=':
            if i + 1 < len(code) and code[i+1] == '=':
                tokens.append(('EQEQ', '==')); i += 2
            else:
                tokens.append(('EQUALS', '=')); i += 1
        elif code[i] == '<':
            if i + 1 < len(code) and code[i+1] == '=':
                tokens.append(('LTE', '<=')); i += 2
            else:
                tokens.append(('LT', '<')); i += 1
        elif code[i] == '>':
            if i + 1 < len(code) and code[i+1] == '=':
                tokens.append(('GTE', '>=')); i += 2
            else:
                tokens.append(('GT', '>')); i += 1
        elif code[i] == '!':
            if i + 1 < len(code) and code[i+1] == '=':
                tokens.append(('NEQ', '!=')); i += 2
            else:
                raise SyntaxError("无法识别的字符: '!' (应为 '!=')")

        # 双引号字符串
        elif code[i] == '"':
            j = i + 1
            while j < len(code) and code[j] != '"':
                j += 1
            if j >= len(code):
                raise SyntaxError("未闭合的字符串")
            tokens.append(('STRING', code[i+1:j])); i = j + 1

        # 单引号字符
        elif code[i] == "'":
            j = i + 1
            while j < len(code) and code[j] != "'":
                j += 1
            if j >= len(code):
                raise SyntaxError("未闭合的字符字面量")
            char_value = code[i+1:j]
            if len(char_value) != 1:
                raise SyntaxError("字符字面量必须恰好包含一个字符")
            tokens.append(('CHAR', char_value)); i = j + 1

        # 数字（整数或浮点数）
        elif code[i].isdigit() or (code[i] == '.' and i + 1 < len(code) and code[i+1].isdigit()):
            j = i
            while j < len(code) and (code[j].isdigit() or code[j] == '.'):
                j += 1
            num_str = code[i:j]
            if num_str.count('.') > 1:
                raise SyntaxError(f"无效的数字: {num_str}")
            if '.' in num_str:
                tokens.append(('FLOAT', float(num_str)))
            else:
                tokens.append(('INTEGER', int(num_str)))
            i = j

        # 标识符或关键字
        else:
            m = re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', code[i:])
            if not m:
                raise SyntaxError(f"无法识别的字符: {code[i]}")
            word = m.group(0)
            keywords = {
                'set': 'SET',
                'num': 'TYPE_NUM',
                'char': 'TYPE_CHAR',
                'string': 'TYPE_STRING',
                'let': 'LET',
                'for': 'FOR'
            }
            token_type = keywords.get(word, 'IDENTIFIER')
            tokens.append((token_type, word))
            i += len(word)

    return tokens