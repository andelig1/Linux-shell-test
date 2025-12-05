from .commands import builtin_commands


def is_builtin_command(cmd_name):
    """判断一个命令是否为内置命令"""
    return cmd_name in builtin_commands


def execute_builtin(cmd_name, args):
    """
    执行内置命令。

    Args:
        cmd_name (str): 命令名称
        args (list): 参数列表

    Returns:
        bool: 如果该命令执行后要求 Shell 退出（如 exit），则返回 True，否则返回 False。
    """
    if cmd_name in builtin_commands:
        # 从命令字典中获取对应的函数并执行
        return builtin_commands[cmd_name](args)
    else:
        print(f"Error: '{cmd_name}' 不是可识别的内置命令。")
        return False