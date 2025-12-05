import os
import glob
import re


class CommandCompleter:
    def __init__(self, alias_manager=None):
        self.alias_manager = alias_manager
        self.common_commands = ['cd', 'ls', 'pwd', 'exit', 'help', 'history', 'alias', 'unalias']

        # 从PATH获取系统命令
        self.system_commands = self._get_system_commands()

    def _get_system_commands(self):
        """从PATH环境变量获取所有可执行命令"""
        commands = set()
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)

        for path_dir in path_dirs:
            if os.path.isdir(path_dir):
                try:
                    for item in os.listdir(path_dir):
                        if os.access(os.path.join(path_dir, item), os.X_OK):
                            commands.add(item)
                except (PermissionError, OSError):
                    continue

        return list(commands)

    def get_completions(self, text, cwd):
        """获取补全建议列表"""
        if not text:
            return []

        # 如果包含空格，可能是路径补全
        if ' ' in text:
            return self._path_completion(text, cwd)
        else:
            # 命令补全
            return self._command_completion(text)

    def _command_completion(self, partial):
        """命令补全"""
        completions = []

        # 检查内置命令
        for cmd in self.common_commands:
            if cmd.startswith(partial):
                completions.append(cmd)

        # 检查别名
        if self.alias_manager:
            for alias in self.alias_manager.aliases.keys():
                if alias.startswith(partial):
                    completions.append(alias)

        # 检查系统命令
        for cmd in self.system_commands:
            if cmd.startswith(partial):
                completions.append(cmd)

        return sorted(list(set(completions)))  # 去重并排序

    def _path_completion(self, text, cwd):
        """路径补全"""
        parts = text.split(' ')
        last_part = parts[-1]

        # 如果是空的部分，不补全
        if not last_part:
            return []

        # 确定要补全的目录
        if '/' in last_part:
            # 包含路径分隔符
            dir_part = os.path.dirname(last_part)
            base_part = os.path.basename(last_part)

            if dir_part.startswith('/'):
                # 绝对路径
                search_dir = dir_part
            else:
                # 相对路径
                search_dir = os.path.join(cwd, dir_part)
        else:
            # 当前目录
            search_dir = cwd
            base_part = last_part

        # 确保目录存在
        if not os.path.isdir(search_dir):
            return []

        try:
            # 获取匹配的文件和目录
            matches = []
            for item in os.listdir(search_dir):
                if item.startswith(base_part):
                    item_path = os.path.join(search_dir, item)

                    # 如果是目录，添加斜杠
                    if os.path.isdir(item_path):
                        matches.append(item + '/')
                    else:
                        matches.append(item)

            return matches
        except (PermissionError, OSError):
            return []

    def get_common_prefix(self, completions):
        """获取补全列表的公共前缀"""
        if not completions:
            return ""

        # 找到最长的公共前缀
        prefix = completions[0]
        for item in completions[1:]:
            while not item.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return ""
        return prefix