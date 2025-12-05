#!/usr/bin/env python3
import sys
import os
import tty
import termios

# 将项目根目录添加到 Python 路径，确保模块可以正确导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .builtin.commands import HISTORY_LIST, alias_manager
from .utils.helpers import print_prompt
from .parser.parser import parse_input
from .builtin.builtin import is_builtin_command, execute_builtin
from .external.executor import execute_external
from .utils.wildcard_expander import WildcardExpander
from .utils.completer import CommandCompleter
from .utils.tab_handler import TabHandler

# 全局补全器实例
completer = None
tab_handler = None


def init_completers():
    """初始化补全器"""
    global completer, tab_handler
    completer = CommandCompleter(alias_manager)
    tab_handler = TabHandler(completer)


def get_input():
    """改进的输入函数，支持Tab补全"""
    # 确保在非 Linux/macOS 环境下使用标准 input()，避免 tty/termios 报错
    if os.name != 'posix':
        try:
            return input()
        except EOFError:
            raise EOFError

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        input_chars = []
        cursor_pos = 0

        while True:
            ch = sys.stdin.read(1)

            # Tab键处理
            if ch == '\t' or ch == '\x09':
                if tab_handler is None:
                    init_completers()

                cwd = os.getcwd()
                current_input = ''.join(input_chars)

                new_input, new_pos, applied = tab_handler.handle_tab(
                    current_input, cursor_pos, cwd
                )

                if applied:
                    # 清空行并重新显示
                    sys.stdout.write('\r' + ' ' * 80 + '\r')
                    sys.stdout.flush()

                    input_chars = list(new_input)
                    cursor_pos = new_pos

                    # 重新显示
                    sys.stdout.write(''.join(input_chars))
                    sys.stdout.flush()

                continue

            # 方向键和其他特殊键（简单实现左右移动）
            elif ch == '\x1b':  # ESC键，可能是方向键
                next_ch = sys.stdin.read(1)
                if next_ch == '[':
                    direction = sys.stdin.read(1)
                    # 左箭头: \x1b[D, 右箭头: \x1b[C
                    if direction == 'D' and cursor_pos > 0:
                        cursor_pos -= 1
                        sys.stdout.write('\b')
                        sys.stdout.flush()
                    elif direction == 'C' and cursor_pos < len(input_chars):
                        cursor_pos += 1
                        sys.stdout.write('\x1b[C')
                        sys.stdout.flush()
                continue

            elif ch == '\r' or ch == '\n':
                sys.stdout.write('\r\n')
                sys.stdout.flush()
                break

            elif ch == '\x7f' or ch == '\x08':  # 退格键
                if cursor_pos > 0:
                    input_chars.pop(cursor_pos - 1)
                    cursor_pos -= 1
                    # 重新显示整行
                    sys.stdout.write('\r' + ' ' * 80 + '\r')
                    sys.stdout.write(''.join(input_chars))
                    # 移动光标到正确位置
                    if cursor_pos < len(input_chars):
                        sys.stdout.write('\x1b[' + str(len(input_chars) - cursor_pos) + 'D')
                    sys.stdout.flush()

            elif ch == '\x03':  # Ctrl+C
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                raise KeyboardInterrupt

            elif ch == '\x04':  # Ctrl+D
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                raise EOFError

            else:
                # 插入字符
                input_chars.insert(cursor_pos, ch)
                cursor_pos += 1
                # 重新显示从插入位置开始的字符
                sys.stdout.write(''.join(input_chars[cursor_pos - 1:]))
                # 如果不是在末尾插入，移动光标回正确位置
                if cursor_pos < len(input_chars):
                    sys.stdout.write('\x1b[' + str(len(input_chars) - cursor_pos) + 'D')
                sys.stdout.flush()

        return ''.join(input_chars)

    except Exception as e:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        raise e
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def main_loop():
    """Shell 的主循环"""
    status = True  # 控制循环的状态标志

    # 初始化补全器
    init_completers()

    while status:
        try:
            # 1. 打印提示符
            print_prompt()

            # 2. 读取用户输入（使用自定义输入函数）
            user_input = get_input().strip()
            if not user_input:
                continue  # 忽略空输入
            HISTORY_LIST.append(user_input)

            # 3. 解析输入
            # command_pipeline 是一个列表，包含一个或多个命令令牌列表
            command_pipeline = parse_input(user_input)
            if not command_pipeline:
                continue  # 解析结果为空，继续下一轮循环

            # 通配符扩展
            command_pipeline = WildcardExpander.expand_pipeline(command_pipeline)

            # 4. 判断并执行命令
            first_command_tokens = command_pipeline[0]

            # 解析别名（在判断是否为内置命令之前）
            first_command_tokens = alias_manager.resolve_aliases(first_command_tokens)
            if not first_command_tokens:  # 如果别名解析后为空
                continue

            # ============ 关键修复：将解析后的别名更新回命令管道 ============
            command_pipeline[0] = first_command_tokens
            # =============================================================

            command_name = first_command_tokens[0]
            args = first_command_tokens[1:]

            # 检查第一个命令是否是内置命令
            if is_builtin_command(command_name):
                # 只有当没有管道时，内置命令才被允许执行
                if len(command_pipeline) == 1:
                    # 执行内置命令，并检查是否需要退出 Shell
                    should_exit = execute_builtin(command_name, args)
                    if should_exit:
                        status = False
                        print("shell退出")
                else:
                    # 内置命令不支持作为管道的输入端
                    print(f"mysh: 错误: 内置命令 '{command_name}' 不支持作为管道的第一级命令。", file=sys.stderr)
            else:
                # 执行整个命令管道
                execute_external(command_pipeline)

        except KeyboardInterrupt:
            # 捕获 Ctrl+C，不退出 Shell，只换行
            print("\n使用 'exit' 或 'logout' 退出。")
        except EOFError:
            # 捕获 Ctrl+D (EOF)，优雅退出
            print("\n收到EOF，退出。")
            status = False
        except Exception as e:
            # 捕获其他未知错误，防止 Shell 崩溃
            print(f"发生意外错误: {e}", file=sys.stderr)


if __name__ == "__main__":
    print("欢迎使用MyShell")
    print("功能：")
    print("cd [目录]   切换工作目录（不指定目录则回家目录）")
    print("pwd   打印当前工作目录的完整路径")
    print("exit/logout   退出MyShell程序")
    print("help   显示内置命令的帮助信息")
    print("history   显示本次会话中输入过的命令历史")
    print("alias   管理命令别名（定义、查看）")
    print("unalias   删除已定义的命令别名")
    print("新功能使用说明：")
    print("  1. 别名功能: alias ll='ls -l'")
    print("  2. 通配符扩展: ls test?.txt")
    print("  3. Tab键补全: 输入部分命令按Tab自动补全")
    main_loop()