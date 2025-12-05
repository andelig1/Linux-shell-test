import os
import getpass
import sys

def print_prompt():
    """
    打印带颜色的漂亮提示符
    效果：[绿色用户名]@[蓝色路径] $
    """
    # 1. 定义颜色代码 (ANSI Escape Codes)
    GREEN = '\033[92m'  # 亮绿色
    BLUE = '\033[94m'   # 亮蓝色
    RESET = '\033[0m'   # 重置颜色（必须有，不然后面全变色）

    # 2. 获取当前用户名
    try:
        user = getpass.getuser()
    except:
        user = "user"

    # 3. 获取当前路径，把长路径 /home/xxx 缩短为 ~
    try:
        cwd = os.getcwd().replace(os.path.expanduser("~"), "~")
    except:
        cwd = os.getcwd()

    # 4. 拼接这一长串漂亮的字符串
    # 结构：[ 绿色用户 白色@ 蓝色路径 白色 ] $
    prompt_str = f"[{GREEN}{user}{RESET}@{BLUE}{cwd}{RESET}]$ "

    # 5. 打印出来 (注意 flush=True 确保立即显示)
    print(prompt_str, end="", flush=True)

def print_error(msg):
    """
    打印红色的错误报错（可选工具）
    """
    RED = '\033[91m'
    RESET = '\033[0m'
    print(f"{RED}Error: {msg}{RESET}")