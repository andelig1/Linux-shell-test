#!/usr/bin/env python3
import sys
import os

# 将项目根目录添加到 Python 路径，确保模块可以正确导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入自定义模块
from .utils.helpers import print_prompt
from .parser.parser import parse_input
from .builtin.builtin import is_builtin_command, execute_builtin
from .external.executor import execute_external
from .builtin.commands import HISTORY_LIST

def main_loop():
    """Shell 的主循环"""
    status = True  # 控制循环的状态标志

    while status:
        try:
            # 1. 打印提示符
            print_prompt()

            # 2. 读取用户输入
            user_input = input().strip()
            if not user_input:
                continue  # 忽略空输入
            HISTORY_LIST.append(user_input)

            # 3. 解析输入
            # 此时，command_tokens 是一个列表，例如 ['ls', '-l']
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


if __name__ == "__main__":
    print("欢迎使用MyShell")
    main_loop()