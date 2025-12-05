import shlex
import sys


def parse_input(input_string):
    """
    将输入字符串解析成令牌列表，识别重定向符号、后台运行符号和管道符号

    Args:
        input_string (str): 用户输入的命令行字符串

    Returns:
        tuple: (命令列表, 是否后台运行, 重定向信息字典, 管道信息)
    """
    if not input_string or not input_string.strip():
        return [], False, {}, False

    try:
        # 检查是否以 & 结尾（后台运行）
        background = False
        trimmed_input = input_string.strip()

        if trimmed_input.endswith('&'):
            background = True
            trimmed_input = trimmed_input[:-1].strip()

        # 使用 shlex.split 可以正确处理带引号的参数
        tokens = shlex.split(trimmed_input)
        if not tokens:
            return [], background, {}, False

        # 检查是否有管道符号
        has_pipe = '|' in tokens

        if has_pipe:
            # 管道处理逻辑
            return parse_pipeline(tokens, background)
        else:
            # 原来的单命令处理逻辑
            return parse_single_command(tokens, background)

    except ValueError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return [], False, {}, False


def parse_single_command(tokens, background):
    """解析单个命令（无管道）"""
    redirections = {}
    command_tokens = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token in ('>', '>>', '<'):
            # 找到重定向符号
            redir_type = token
            if i + 1 >= len(tokens):
                print(f"语法错误: 重定向符号 '{token}' 后缺少文件名", file=sys.stderr)
                return [], False, {}, False

            filename = tokens[i + 1]
            redirections[redir_type] = filename
            i += 2  # 跳过重定向符号和文件名
        else:
            command_tokens.append(token)
            i += 1

    return [command_tokens], background, redirections, False


def parse_pipeline(tokens, background):
    """解析管道命令"""
    commands = []  # 每个元素是一个命令的token列表
    current_command = []
    redirections = {}  # 目前只支持最后一个命令的重定向

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token == '|':
            # 管道符号，保存当前命令并开始新命令
            if current_command:
                commands.append(current_command)
                current_command = []
            i += 1
        elif token in ('>', '>>', '<'):
            # 重定向符号（目前只支持最后一个命令的重定向）
            redir_type = token
            if i + 1 >= len(tokens):
                print(f"语法错误: 重定向符号 '{token}' 后缺少文件名", file=sys.stderr)
                return [], False, {}, True

            filename = tokens[i + 1]
            redirections[redir_type] = filename
            i += 2
        else:
            current_command.append(token)
            i += 1

    # 添加最后一个命令
    if current_command:
        commands.append(current_command)

    if len(commands) < 2:
        print("语法错误: 管道符号 '|' 前后都需要命令", file=sys.stderr)
        return [], False, {}, True

    return commands, background, redirections, True