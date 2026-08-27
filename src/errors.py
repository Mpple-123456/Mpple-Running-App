# src/errors.py
ERROR_MESSAGES = {
    "unrecognized_char": {
        "zh": "无法识别的字符: {char}",
        "en": "Unrecognized character: {char}"
    },
    "unclosed_string": {
        "zh": "未闭合的字符串",
        "en": "Unclosed string"
    },
    # 其他错误...
}

def get_error_message(key, lang="zh", **kwargs):
    template = ERROR_MESSAGES.get(key, {}).get(lang, key)
    return template.format(**kwargs)