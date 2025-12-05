import os
HISTORY_LIST = []

def builtin_cd(args):
    """内置命令 cd: 切换工作目录"""
    try:
        target_dir = args[0] if args else os.path.expanduser("~")
        os.chdir(target_dir)
        print(f"Changed directory to {os.getcwd()}")
    except FileNotFoundError:
        print(f"cd: {args[0]}: No such file or directory")
    except Exception as e:
        print(f"cd: {e}")
    return False  # 不退出 Shell

def builtin_exit(args):
    """内置命令 exit: 退出 Shell"""
    return True  # 通知主循环退出

def builtin_pwd(args):
    """内置命令 pwd: 打印当前工作目录"""
    print(os.getcwd())
    return False

def builtin_help(args):
    """内置命令 help: 显示帮助信息"""
    help_text = """
MyShell (Python) Built-in Commands:
    cd [dir]      Change the current directory to 'dir'. Defaults to home directory.
    pwd           Print the current working directory.
    exit, logout  Exit the shell.
    help          Display this help message.
    """
    print(help_text)
    return False

def builtin_history(args):
    """内置命令 history: 显示历史记录"""
    for i, cmd in enumerate(HISTORY_LIST, 1):
        print(f"{i}  {cmd}")
    return False  # 不退出 Shell

# 内置命令字典：命令名称 -> 执行函数
builtin_commands = {
    "cd": builtin_cd,
    "exit": builtin_exit,
    "logout": builtin_exit,  # logout 作为 exit 的别名
    "pwd": builtin_pwd,
    "help": builtin_help,
    "history": builtin_history,
}