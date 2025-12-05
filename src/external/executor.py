import os
import sys
import subprocess


def execute_external(cmd_tokens):
    """
    使用 fork/exec 机制执行外部命令

    Args:
        cmd_tokens (list): 包含命令及其参数的列表，例如 ['ls', '-l']
    """
    try:
        # 创建子进程
        pid = os.fork()
        if pid == 0:
            # 子进程代码
            try:
                # 使用 execvp 执行命令
                # execvp 会在 PATH 环境变量中查找命令
                os.execvp(cmd_tokens[0], cmd_tokens)
            except FileNotFoundError:
                print(f"mysh: 命令未找到: {cmd_tokens[0]}", file=sys.stderr)
                sys.exit(127)  # 127 是命令未找到的标准退出码
            except PermissionError:
                print(f"mysh: 权限不足: {cmd_tokens[0]}", file=sys.stderr)
                sys.exit(126)  # 126 是权限错误的标准退出码
            except Exception as e:
                print(f"mysh: 执行错误 '{cmd_tokens[0]}': {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # 父进程代码
            # 等待子进程结束
            _, status = os.waitpid(pid, 0)

            # 检查子进程是否正常退出
            if os.WIFEXITED(status):
                exit_code = os.WEXITSTATUS(status)
                # 如果需要，可以在这里处理退出码
                # if exit_code != 0:
                #     print(f"进程退出，状态码: {exit_code}")
            elif os.WIFSIGNALED(status):
                signal_num = os.WTERMSIG(status)
                print(f"\n进程被信号终止: {signal_num}", file=sys.stderr)

    except OSError as e:
        print(f"mysh: fork 失败: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        # 处理在等待子进程时按 Ctrl+C
        print()  # 换行
    except Exception as e:
        print(f"mysh: 意外错误: {e}", file=sys.stderr)