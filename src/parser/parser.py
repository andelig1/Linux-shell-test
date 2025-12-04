import shlex


def parse_input(input_string):
    """
    将输入字符串解析成令牌列表。

    Args:
        input_string (str): 用户输入的命令行字符串

    Returns:
        list: 由命令和参数组成的列表。如果输入为空，返回空列表。
    """
    if not input_string or not input_string.strip():
        return []

    try:
        # 使用 shlex.split 可以正确处理带引号的参数，例如 `echo "Hello World"`
        tokens = shlex.split(input_string)
        return tokens
    except ValueError as e:
        # 处理引号不匹配等错误
        print(f"Parse error: {e}", file=sys.stderr)
        return []