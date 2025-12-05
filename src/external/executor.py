import os
import sys


# subprocess 在 fork/exec 模式下不需要，但保持不变。
# 警告：此版本使用 fork/exec，只能在 Linux 或 macOS 上运行。

def execute_external(command_pipeline):
    """
    执行一个命令管道（由一个或多个外部命令组成）。

    Args:
        command_pipeline (list): 包含多个命令令牌列表的列表，例如 [['ls', '-l'], ['grep', 'main']]
    """

    input_fd = 0  # 初始输入来自标准输入 (stdin, fd=0)
    pids = []  # 存储所有子进程的 PID

    # 循环执行管道中的每个命令
    for i, cmd_tokens in enumerate(command_pipeline):
        is_last_command = (i == len(command_pipeline) - 1)

        # 1. 创建管道 (如果不是最后一个命令)
        if not is_last_command:
            try:
                # pipe_read (p_in), pipe_write (p_out)
                pipe_read, pipe_write = os.pipe()
            except OSError as e:
                print(f"mysh: 管道创建失败: {e}", file=sys.stderr)
                # 发生错误时，尝试清理已启动的进程
                for pid in pids:
                    try:
                        os.kill(pid, 9)
                    except OSError:
                        pass
                return

        # 2. 创建子进程
        try:
            pid = os.fork()
        except OSError as e:
            print(f"mysh: fork 失败: {e}", file=sys.stderr)
            # 错误处理：关闭管道并等待已启动的子进程
            if not is_last_command:
                os.close(pipe_read)
                os.close(pipe_write)
            while pids:
                os.waitpid(pids.pop(0), 0)
            return

        # --- 子进程逻辑 (pid == 0) ---
        if pid == 0:
            # 3. 设置输入重定向 (如果不是第一个命令)
            if input_fd != 0:
                os.dup2(input_fd, sys.stdin.fileno())  # 重定向 stdin
                os.close(input_fd)  # 关闭父进程传递过来的旧 fd

            # 4. 设置输出重定向 (如果不是最后一个命令)
            if not is_last_command:
                os.dup2(pipe_write, sys.stdout.fileno())  # 重定向 stdout
                os.close(pipe_read)  # 子进程不需要管道的读端
                os.close(pipe_write)  # 关闭 dup2 后的冗余 fd

            # 5. 执行命令
            try:
                os.execvp(cmd_tokens[0], cmd_tokens)
            except FileNotFoundError:
                print(f"mysh: 命令未找到: {cmd_tokens[0]}", file=sys.stderr)
                sys.exit(127)
            except PermissionError:
                print(f"mysh: 权限不足: {cmd_tokens[0]}", file=sys.stderr)
                sys.exit(126)
            except Exception as e:
                print(f"mysh: 执行错误 '{cmd_tokens[0]}': {e}", file=sys.stderr)
                sys.exit(1)

        # --- 父进程逻辑 (pid > 0) ---
        else:
            pids.append(pid)

            # 6. 父进程关闭不再需要的描述符
            # 必须关闭上一个命令的输入 fd
            if input_fd != 0:
                os.close(input_fd)

            # 7. 更新 input_fd 为当前管道的读取端 (供下一个命令使用)
            if not is_last_command:
                os.close(pipe_write)  # 父进程不需要管道的写端
                input_fd = pipe_read  # 下一个命令的输入将是当前命令的输出

    # 8. 父进程等待所有子进程完成
    for pid in pids:
        try:
            # 阻塞等待所有进程完成
            os.waitpid(pid, 0)
        except ChildProcessError:
            pass  # 进程可能已被其他 wait 调用处理
        except Exception as e:
            print(f"mysh: 等待子进程错误: {e}", file=sys.stderr)

    # 9. 确保最后使用的 input_fd 被关闭 (如果存在)
    if input_fd != 0:
        os.close(input_fd)