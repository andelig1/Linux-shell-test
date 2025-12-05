import shlex
import sys  # 确保 sys 已导入


def parse_input(input_string):
    """
    将输入字符串解析成一个命令管道列表（List of cmd_tokens）。

    Args:
        input_string (str): 用户输入的命令行字符串

    Returns:
        list: 包含命令及其参数列表的列表。例如：[['ls', '-l'], ['grep', 'main']]
    """
    if not input_string or not input_string.strip():
        return []

    # 1. 按管道符 '|' 分割命令
    command_pipe_strings = input_string.split('|')

    # 2. 进一步解析每个命令的参数
    pipeline = []
    for cmd_str in command_pipe_strings:
        cmd_str = cmd_str.strip()
        if not cmd_str:
            # 忽略空的命令（例如输入 'ls || grep'）
            continue

        try:
            # 使用 shlex.split 处理带引号的参数
            tokens = shlex.split(cmd_str)
            if tokens:
                pipeline.append(tokens)
        except ValueError as e:
            print(f"mysh: 解析错误 (管道命令): {e}", file=sys.stderr)
            return []  # 解析错误则返回空

    return pipeline