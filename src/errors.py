# src/errors.py
from src.config import get_config

def get_error_message(key, **kwargs):
    lang = get_config().get("language", "zh")
    messages = {
        # Lexer 错误
        "unrecognized_char": {
            "zh": "无法识别的字符: {char}",
            "en": "Unrecognized character: {char}"
        },
        "unclosed_string": {
            "zh": "未闭合的字符串",
            "en": "Unclosed string"
        },
        "unclosed_char": {
            "zh": "未闭合的字符字面量",
            "en": "Unclosed character literal"
        },
        "invalid_char_literal": {
            "zh": "字符字面量必须恰好包含一个字符",
            "en": "Character literal must contain exactly one character"
        },
        "invalid_number": {
            "zh": "无效的数字: {number}",
            "en": "Invalid number: {number}"
        },

        # Parser 错误
        "expected_token": {
            "zh": "期望 {expected}，实际得到 {actual}",
            "en": "Expected {expected}, got {actual}"
        },
        "unknown_type": {
            "zh": "未知类型: {type}",
            "en": "Unknown type: {type}"
        },
        "for_init_error": {
            "zh": "for 循环的初始化部分必须是 set 或 let 语句",
            "en": "For loop initialization must be set or let statement"
        },
        "unsupported_update_operator": {
            "zh": "不支持的更新运算符: {op}",
            "en": "Unsupported update operator: {op}"
        },
        "parse_error": {
            "zh": "无法解析的 token: {token}",
            "en": "Unable to parse token: {token}"
        },

        # Interpreter 运行时错误
        "variable_undefined": {
            "zh": "变量未定义: {name}",
            "en": "Variable undefined: {name}"
        },
        "function_undefined": {
            "zh": "函数未定义: {name}",
            "en": "Function undefined: {name}"
        },
        "type_mismatch_num": {
            "zh": "变量 {name} 需要数字类型，但得到 {type}",
            "en": "Variable {name} requires numeric type, got {type}"
        },
        "type_mismatch_char": {
            "zh": "变量 {name} 需要字符类型",
            "en": "Variable {name} requires char type"
        },
        "type_mismatch_string": {
            "zh": "变量 {name} 需要字符串类型",
            "en": "Variable {name} requires string type"
        },
        "division_by_zero": {
            "zh": "除以零",
            "en": "Division by zero"
        },
        "unsupported_operator": {
            "zh": "不支持的运算符: {op}",
            "en": "Unsupported operator: {op}"
        },
        "unknown_node": {
            "zh": "未知节点类型: {node_type}",
            "en": "Unknown node type: {node_type}"
        },
    }
    template = messages.get(key, {}).get(lang, key)
    return template.format(**kwargs)