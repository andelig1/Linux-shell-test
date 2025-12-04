import subprocess
import sys


def execute_external(cmd_tokens):
    """
    在一个子进程中执行外部命令。

    Args:
        cmd_tokens (list): 包含命令及其参数的列表，例如 ['ls', '-l']
    """
    try:
        # 使用 subprocess.run 来执行命令
        # 它会等待命令完成，然后返回一个 CompletedProcess 对象
        result = subprocess.run(
            cmd_tokens,
            check=False,  # 如果命令返回非零退出码，我们不希望抛出异常，而是自己处理
            capture_output=True,  # 捕获标准输出和标准错误
            encoding='utf-8'  # 以文本模式处理输出
        )

        # 打印命令的输出
        if result.stdout:
            print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, end='', file=sys.stderr)

        # 选择是否打印返回码（调试用）
        # if result.returncode != 0:
        #     print(f"Process finished with exit code {result.returncode}")

    except FileNotFoundError:
        print(f"mysh: 命令未找到: {cmd_tokens[0]}")
    except PermissionError:
        print(f"mysh: 权限不足: {cmd_tokens[0]}")
    except Exception as e:
        print(f"mysh: 执行错误 '{cmd_tokens[0]}': {e}")