import os
import re
import shlex
import sys

HISTORY_LIST = []


# ================== 别名管理器类（移动到commands.py内部） ==================
class AliasManager:
    def __init__(self):
        self.aliases = {}
        self.config_file = os.path.expanduser("~/.myshrc")
        self.load_aliases()

    def load_aliases(self):
        """从配置文件加载别名"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            match = re.match(r'alias\s+(\w+)=[\'"]?(.*?)[\'"]?$', line)
                            if match:
                                alias_name = match.group(1)
                                alias_value = match.group(2).strip('\'"')
                                self.aliases[alias_name] = alias_value
            except Exception as e:
                print(f"加载别名配置失败: {e}", file=sys.stderr)

    def save_aliases(self):
        """保存别名到配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write("# MyShell 别名配置\n")
                for name, value in self.aliases.items():
                    f.write(f"alias {name}='{value}'\n")
            return True
        except Exception as e:
            print(f"保存别名配置失败: {e}", file=sys.stderr)
            return False

    def add_alias(self, name, value):
        """添加别名"""
        self.aliases[name] = value
        self.save_aliases()

    def remove_alias(self, name):
        """移除别名"""
        if name in self.aliases:
            del self.aliases[name]
            self.save_aliases()
            return True
        return False

    def resolve_aliases(self, command_tokens):
        """解析命令中的别名"""
        if not command_tokens:
            return command_tokens

        first_token = command_tokens[0]
        if first_token in self.aliases:
            alias_value = self.aliases[first_token]
            try:
                alias_tokens = shlex.split(alias_value)
            except:
                alias_tokens = alias_value.split()

            alias_tokens.extend(command_tokens[1:])
            return alias_tokens

        return command_tokens

    def list_aliases(self):
        """列出所有别名"""
        return self.aliases.copy()


# 创建全局别名管理器实例
alias_manager = AliasManager()


# ================== 内置命令函数定义 ==================
def builtin_cd(args):
    """内置命令 cd: 切换工作目录"""
    try:
        target_dir = args[0] if args else os.path.expanduser("~")
        os.chdir(target_dir)
        print(f"Changed directory to {os.getcwd()}")
    except FileNotFoundError:
        print(f"cd: {args[0]}: No such file or directory", file=sys.stderr)
    except Exception as e:
        print(f"cd: {e}", file=sys.stderr)
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
    history       Show command history.
    alias [name[='value']]  Manage command aliases.
    unalias name  Remove an alias.
    """
    print(help_text)
    return False


def builtin_history(args):
    """内置命令 history: 显示历史记录"""
    for i, cmd in enumerate(HISTORY_LIST, 1):
        print(f"{i}  {cmd}")
    return False  # 不退出 Shell


def builtin_alias(args):
    """内置命令 alias: 管理命令别名"""
    if not args:
        # 显示所有别名
        aliases = alias_manager.list_aliases()
        if not aliases:
            print("当前没有定义任何别名")
        else:
            for name, value in aliases.items():
                print(f"{name}='{value}'")
        return False

    # 处理 alias name=value 格式
    if '=' in args[0]:
        parts = args[0].split('=', 1)
        if len(parts) == 2:
            name, value = parts
            alias_manager.add_alias(name.strip(), value.strip())
            print(f"别名已定义: {name}='{value}'")
        else:
            print("用法: alias name='value' 或 alias name=value", file=sys.stderr)
        return False

    # 显示特定别名
    for name in args:
        if name in alias_manager.aliases:
            print(f"{name}='{alias_manager.aliases[name]}'")
        else:
            print(f"别名未定义: {name}", file=sys.stderr)
    return False


def builtin_unalias(args):
    """内置命令 unalias: 删除别名"""
    if not args:
        print("用法: unalias 别名名称", file=sys.stderr)
        return False

    for name in args:
        if alias_manager.remove_alias(name):
            print(f"别名已删除: {name}")
        else:
            print(f"别名不存在: {name}", file=sys.stderr)
    return False


# ================== 内置命令字典 ==================
# 内置命令字典：命令名称 -> 执行函数
builtin_commands = {
    "cd": builtin_cd,
    "exit": builtin_exit,
    "logout": builtin_exit,  # logout 作为 exit 的别名
    "pwd": builtin_pwd,
    "help": builtin_help,
    "history": builtin_history,
    "alias": builtin_alias,  # 新增
    "unalias": builtin_unalias,  # 新增（注意：这里之前少了函数引用）
}