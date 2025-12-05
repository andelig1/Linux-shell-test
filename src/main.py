#!/usr/bin/env python3
import sys
import os
import tty
import termios

# 将项目根目录添加到 Python 路径，确保模块可以正确导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入自定义模块（在pycharm上跑时在每个库前面加一个“.”，不然会报错，在Linux上跑不要加!!!）
from builtin.commands import HISTORY_LIST
from utils.helpers import print_prompt
from parser.parser import parse_input
from builtin.builtin import is_builtin_command, execute_builtin
from external.executor import execute_external

# from .builtin.commands import HISTORY_LIST
# from .utils.helpers import print_prompt
# from .parser.parser import parse_input
# from .builtin.builtin import is_builtin_command, execute_builtin
# from .external.executor import execute_external


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
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        # 设置终端为原始模式
        tty.setraw(fd)

        input_chars = []
        line_printed = False  # 跟踪是否已经打印了内容

        while True:
            ch = sys.stdin.read(1)

            if ch == '\r' or ch == '\n':  # 回车键
                # 总是输出换行符，确保光标移动到下一行
                sys.stdout.write('\r\n')
                break

            elif ch == '\x7f' or ch == '\x08':  # 退格键或删除键
                if input_chars:
                    input_chars.pop()
                    sys.stdout.write('\b \b')  # 退格、空格、再退格
                    sys.stdout.flush()
                    line_printed = True

            elif ch == '\x03':  # Ctrl+C
                raise KeyboardInterrupt

            elif ch == '\x04':  # Ctrl+D
                raise EOFError

            else:  # 普通字符
                input_chars.append(ch)
                sys.stdout.write(ch)
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

if __name__ == "__main__":
    print("欢迎使用MyShell")
    main_loop()