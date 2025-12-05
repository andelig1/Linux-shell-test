#!/usr/bin/env python3
import sys
import os
import tty
import termios

# 将项目根目录添加到 Python 路径，确保模块可以正确导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入自定义模块（在pycharm上跑时在每个库前面加一个“.”，不然会报错，在Linux上跑不能加）
from utils.helpers import print_prompt
from parser.parser import parse_input
from builtin.builtin import is_builtin_command, execute_builtin
from external.executor import execute_external


def main_loop():
    """Shell 的主循环"""
    status = True  # 控制循环的状态标志

    while status:
        try:
            # 1. 打印提示符
            print_prompt()

            # 2. 读取用户输入（使用自定义输入函数）
            user_input = get_input().strip()
            if not user_input:
                continue  # 忽略空输入

            # 3. 解析输入
            command_tokens = parse_input(user_input)
            if not command_tokens:
                continue  # 解析结果为空，继续下一轮循环

            # 4. 判断并执行命令
            command_name = command_tokens[0]
            args = command_tokens[1:]

            if is_builtin_command(command_name):
                # 执行内置命令，并检查是否需要退出 Shell
                should_exit = execute_builtin(command_name, args)
                if should_exit:
                    status = False
                    print("shell退出")
            else:
                # 执行外部命令
                execute_external(command_tokens)

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