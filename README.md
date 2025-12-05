# Linux-shell-text
操作系统作业
使用python，软件使用pycharm

# MyShell - 增强型 Python Shell

一个用 Python 实现的类 Linux Shell，支持命令管道、内置命令，并创新性地实现了**命令别名**、**Tab键补全**和**通配符扩展**功能。

## ✨ 核心特性

- **完整的Shell基础**：支持外部命令执行、管道 (`|`)、内置命令和友好交互
- **三大增强功能**：
  - **命令别名**：支持 `alias`/`unalias` 命令，配置持久化
  - **智能Tab补全**：命令补全、路径补全、多选项提示
  - **通配符扩展**：支持 `*`、`?` 等通配符，自动扩展文件列表
- **现代化交互**：彩色提示符、完整退格支持、Ctrl+C/D 正确处理

## 📁 项目结构
MyShell/
├── src/
│ ├── main.py # 程序入口，主循环和输入处理
│ ├── parser/
│ │ ├── init.py
│ │ └── parser.py # 命令解析器（支持管道）
│ ├── builtin/
│ │ ├── init.py
│ │ ├── builtin.py # 内置命令执行器
│ │ └── commands.py # 内置命令实现 & 别名管理器
│ ├── utils/
│ │ ├── init.py
│ │ ├── helpers.py # 工具函数（彩色提示符等）
│ │ ├── wildcard_expander.py # 通配符扩展器
│ │ ├── completer.py # 补全逻辑
│ │ └── tab_handler.py # Tab键处理器
│ └── external/
│ ├── init.py
│ └── executor.py # 外部命令执行（支持管道）
├── requirements.txt # 项目依赖（当前为空）
└── README.md # 本文档


## 🚀 快速开始

### 环境要求
- Python 3.6+
- Linux 或 macOS 系统


### 运行方法

# 克隆项目
# git clone <repository-url>

# 进入项目目录
cd Linux-shell-test-main

# 运行 MyShell
pycharm：在终端输入 python -m src.main 运行，而不是直接运行
Linux：在Linux中安装python后用python main.py运行 或者 在根目录下用python -m src.main运行

