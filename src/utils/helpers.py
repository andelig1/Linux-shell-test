import os

def print_prompt():
    """生成并打印 Shell 提示符。"""
    # 一个简单的提示符，可以扩展为显示用户名、主机名、短路径等
    # 例如：f"{os.getlogin()}@{socket.gethostname().split('.')[0]}:{os.path.basename(os.getcwd())}$ "
    print("mysh> ", end='', flush=True)