# Linux-shell-text
操作系统作业
使用python，软件使用pycharm

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

在终端输入 python -m src.main 运行，而不是直接运行
