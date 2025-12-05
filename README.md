# Linux-shell-text
操作系统作业
使用python，软件使用pycharm

**项目结构**
MyShell/
├── src/                   # 源代码目录
│   ├── main.py            # 程序入口，负责主循环和协调
│   ├── parser/            # 解析模块
│   │   ├── __init__.py
│   │   ├── parser.py      # 命令解析器
│   │   └── tokens.py      # 定义令牌或命令结构（如未来支持管道重定向）
│   ├── builtin/           # 内置命令
│   │   ├── __init__.py
│   │   ├── builtin.py     # 内置命令执行器
│   │   └── commands.py    # 各个内置命令的具体实现（如 cd, exit）
│   ├── utils/             # 工具函数
│   │   ├── __init__.py
│   │   └── helpers.py     # 如提示符生成、错误处理等工具
│   └── external/          # 外部命令执行
│       ├── __init__.py
│       └── executor.py    # 处理外部命令的 fork/exec 逻辑
├── requirements.txt       # Python 项目依赖（当前为空）
└── README.md

**如何运行**
在Linux中安装python后用 ‘python main.py’ 运行即可

**后台运行功能**
使用例 ‘sleep 10 &’ 命令，10表示10毫秒

**重定向测试示例**
    # 输出重定向（覆盖）
        echo "Hello World" > test.txt
        cat test.txt

    # 输出重定向（追加）
        echo "Second line" >> test.txt
        cat test.txt

    # 输入重定向
        cat < test.txt

    # 结合使用
        wc -l < test.txt > line_count.txt
        cat line_count.txt

    # 后台运行与重定向结合
        sleep 5 > sleep_output.txt &


**管道测试示例**
    # 基础管道
        ls | grep py

        ps aux | grep python

        cat /etc/passwd | cut -d: -f1 | sort

    # 多级管道
        ls -la | grep "\.txt" | wc -l

        ps aux | sort -nrk 3 | head -5

    # 管道与重定向组合
        ls | grep py > python_files.txt
        cat python_files.txt

        cat /etc/passwd | cut -d: -f1 | uniq > users.txt
        cat users.txt

        ps aux | grep python > processes.txt
        cat processes.txt