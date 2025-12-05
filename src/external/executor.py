import os
import sys


def execute_external(cmd_tokens, background=False, redirections=None, is_pipeline=False, pipeline_commands=None):
    """
    使用 fork/exec 机制执行外部命令，支持后台运行、I/O重定向和管道

    Args:
        cmd_tokens (list): 包含命令及其参数的列表（或命令列表的列表，如果是管道）
        background (bool): 是否在后台运行
        redirections (dict): 重定向信息
        is_pipeline (bool): 是否是管道命令
        pipeline_commands (list): 管道中的命令列表（仅当is_pipeline=True时使用）
    """
    if redirections is None:
        redirections = {}

    try:
        if is_pipeline:
            # 执行管道命令
            execute_pipeline(pipeline_commands, background, redirections)
        else:
            # 原来的单命令执行逻辑
            execute_single_command(cmd_tokens, background, redirections)

    except OSError as e:
        print(f"mysh: fork 失败: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print()
    except Exception as e:
        print(f"mysh: 意外错误: {e}", file=sys.stderr)


def execute_single_command(cmd_tokens, background, redirections):
    """执行单个命令"""
    if background:
        # 后台运行代码（双重fork）
        pid1 = os.fork()
        if pid1 == 0:
            try:
                os.setsid()
                pid2 = os.fork()
                if pid2 == 0:
                    # 设置重定向
                    setup_redirections(redirections)
                    try:
                        os.execvp(cmd_tokens[0], cmd_tokens)
                    except FileNotFoundError:
                        sys.exit(127)
                    except PermissionError:
                        sys.exit(126)
                    except Exception:
                        sys.exit(1)
                else:
                    os._exit(0)
            except Exception:
                os._exit(1)
        else:
            os.waitpid(pid1, 0)
            print(f"[{pid1}] 后台进程已启动")
    else:
        # 前台运行
        pid = os.fork()
        if pid == 0:
            # 子进程代码
            try:
                # 设置重定向
                setup_redirections(redirections)
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
        else:
            # 父进程代码
            _, status = os.waitpid(pid, 0)

            if os.WIFEXITED(status):
                exit_code = os.WEXITSTATUS(status)
            elif os.WIFSIGNALED(status):
                signal_num = os.WTERMSIG(status)
                print(f"\n进程被信号终止: {signal_num}", file=sys.stderr)


def execute_pipeline(commands, background, redirections):
    """执行管道命令"""
    if background:
        print("mysh: 管道命令暂不支持后台运行")
        return

    if len(commands) < 2:
        print("mysh: 管道需要至少两个命令")
        return

    # 保存原始的stdin和stdout
    original_stdin = os.dup(sys.stdin.fileno())
    original_stdout = os.dup(sys.stdout.fileno())

    try:
        # 创建管道
        pipes = []
        for i in range(len(commands) - 1):
            pipe_read, pipe_write = os.pipe()
            pipes.append((pipe_read, pipe_write))

        # 执行每个命令
        pids = []
        for i, cmd_tokens in enumerate(commands):
            pid = os.fork()
            if pid == 0:
                # 子进程
                try:
                    # 设置输入重定向
                    if i > 0:  # 不是第一个命令，从上一个管道读取
                        os.dup2(pipes[i - 1][0], sys.stdin.fileno())

                    # 设置输出重定向
                    if i < len(commands) - 1:  # 不是最后一个命令，写入到下一个管道
                        os.dup2(pipes[i][1], sys.stdout.fileno())
                    else:  # 最后一个命令，处理文件重定向
                        setup_redirections(redirections)

                    # 关闭所有管道文件描述符
                    for pipe_read, pipe_write in pipes:
                        os.close(pipe_read)
                        os.close(pipe_write)

                    # 恢复原始标准输入输出
                    os.close(original_stdin)
                    os.close(original_stdout)

                    # 执行命令
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
            else:
                pids.append(pid)

        # 关闭所有管道文件描述符（在父进程中）
        for pipe_read, pipe_write in pipes:
            os.close(pipe_read)
            os.close(pipe_write)

        # 等待所有子进程完成
        for pid in pids:
            os.waitpid(pid, 0)

    except Exception as e:
        print(f"mysh: 管道执行错误: {e}", file=sys.stderr)
    finally:
        # 恢复原始标准输入输出
        os.dup2(original_stdin, sys.stdin.fileno())
        os.dup2(original_stdout, sys.stdout.fileno())
        os.close(original_stdin)
        os.close(original_stdout)


def setup_redirections(redirections):
    """设置输入输出重定向（保持不变）"""
    for redir_type, filename in redirections.items():
        try:
            if redir_type == '>':  # 输出重定向（覆盖）
                fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
                os.dup2(fd, sys.stdout.fileno())
                os.close(fd)
            elif redir_type == '>>':  # 输出重定向（追加）
                fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
                os.dup2(fd, sys.stdout.fileno())
                os.close(fd)
            elif redir_type == '<':  # 输入重定向
                fd = os.open(filename, os.O_RDONLY)
                os.dup2(fd, sys.stdin.fileno())
                os.close(fd)
        except IOError as e:
            print(f"mysh: 重定向错误: {e}", file=sys.stderr)
            sys.exit(1)