#!/usr/bin/env python3
import sys
import os
import tty
import termios

# 将项目根目录添加到 Python 路径，确保模块可以正确导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入自定义模块（在pycharm上跑时在每个库前面加一个“.”，不然会报错，在Linux上跑不要加!!!）
from builtin.commands import HISTORY_LIST, alias_manager
from utils.helpers import print_prompt
from parser.parser import parse_input
from builtin.builtin import is_builtin_command, execute_builtin
from external.executor import execute_external
from utils.wildcard_expander import WildcardExpander
from utils.completer import CommandCompleter
from utils.tab_handler import TabHandler

# from .builtin.commands import HISTORY_LIST
# from .utils.helpers import print_prompt
# from .parser.parser import parse_input
# from .builtin.builtin import is_builtin_command, execute_builtin
# from .external.executor import execute_external

# 全局补全器实例
completer = None
tab_handler = None

def main_loop():
    """Shell 的主循环"""
    status = True

    while status:
        try:
            print_prompt()
            user_input = get_input().strip()
            if not user_input:
                continue
            HISTORY_LIST.append(user_input)

            # 解析输入（现在返回 tokens, background, redirections）
            commands, background, redirections, has_pipe = parse_input(user_input)
            if not commands:
                continue

            if has_pipe:
                # 管道命令处理
                if background:
                    print("mysh: 管道命令暂不支持后台运行")
                    continue
                # 检查管道中是否有内置命令
                for cmd_tokens in commands:
                    if is_builtin_command(cmd_tokens[0]):
                        print("mysh: 管道中不支持内置命令")
                        break
                else:
                    # 执行外部管道命令
                    execute_external(None, background, redirections, True, commands)
            else:
                # 单命令处理
                command_tokens = commands[0]
                command_name = command_tokens[0]
                args = command_tokens[1:]

                if is_builtin_command(command_name):
                    # 内置命令不支持后台运行和重定向（或需要特殊处理）
                    if background:
                        print("mysh: 内置命令不支持后台运行")
                        continue
                    if redirections:
                        print("mysh: 内置命令不支持重定向")
                        continue

                    should_exit = execute_builtin(command_name, args)
                    if should_exit:
                        status = False
                        print("MyShell已退出")
                else:
                    # 执行外部命令，传递 background 和 redirections 参数
                    execute_external(command_tokens, background, redirections)

        except KeyboardInterrupt:
            print("\n使用 'exit' 或 'logout' 退出。")
        except EOFError:
            print("\n收到EOF，退出。")
            status = False
        except Exception as e:
            print(f"发生意外错误: {e}", file=sys.stderr)

def get_input():
    """改进的输入函数，正确处理退格键并确保终端设置恢复"""
    if os.name != 'posix':
        try:
            return input()
        except EOFError:
            raise EOFError
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        # 设置终端为原始模式
        tty.setraw(fd)
        input_chars = []
        line_printed = False  # 跟踪是否已经打印了内容
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
                    line_printed = True

                continue

            # 方向键处理和其他特殊键（简单实现左右移动）
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

            elif ch == '\r' or ch == '\n':  # 回车键 - 从文档1优化
                # 总是输出换行符，确保光标移动到下一行
                sys.stdout.write('\r\n')
                sys.stdout.flush()
                break

            elif ch == '\x7f' or ch == '\x08':  # 退格键或删除键
                if input_chars:
                    input_chars.pop(cursor_pos - 1)
                    cursor_pos -= 1
                    # 重新显示从光标位置到行尾的内容
                    remaining_chars = input_chars[cursor_pos:]
                    sys.stdout.write('\r' + ' ' * 80 + '\r')  # 清空当前行
                    sys.stdout.write(''.join(input_chars))

                    # 如果还有剩余字符，移动光标到正确位置
                    if cursor_pos < len(input_chars):
                        sys.stdout.write('\x1b[' + str(len(input_chars) - cursor_pos) + 'D')

                    sys.stdout.flush()
                    line_printed = True

            elif ch == '\x03':  # Ctrl+C
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                raise KeyboardInterrupt

            elif ch == '\x04':  # Ctrl+D
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                raise EOFError


            else:  # 普通字符
                # 在光标位置插入字符
                input_chars.insert(cursor_pos, ch)
                cursor_pos += 1
                # 重新显示从插入位置开始的字符
                sys.stdout.write(''.join(input_chars[cursor_pos - 1:]))
                # 如果不是在末尾插入，移动光标回正确位置
                if cursor_pos < len(input_chars):
                    sys.stdout.write('\x1b[' + str(len(input_chars) - cursor_pos) + 'D')

                sys.stdout.flush()
                line_printed = True

        return ''.join(input_chars)

    except Exception as e:
        # 发生任何异常时也确保恢复终端设置
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        raise e

    finally:
        # 确保终端设置被恢复
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        # 发送终端重置序列，确保状态正确
        sys.stdout.write('\x1b[0m')  # 重置所有属性
        sys.stdout.flush()

def init_completers():
    """初始化补全器"""
    global completer, tab_handler
    completer = CommandCompleter(alias_manager)
    tab_handler = TabHandler(completer)

if __name__ == "__main__":
    print("欢迎使用MyShell")
    main_loop()