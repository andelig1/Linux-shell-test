import os
import glob
import re


class WildcardExpander:
    @staticmethod
    def expand_tokens(tokens):
        """扩展token列表中的通配符"""
        expanded_tokens = []
        for token in tokens:
            # 检查token是否包含通配符
            if WildcardExpander._has_wildcard(token):
                # 使用glob进行扩展
                matches = glob.glob(token)
                if matches:
                    # 按字母顺序排序匹配结果
                    matches.sort()
                    expanded_tokens.extend(matches)
                else:
                    # 没有匹配项，保留原始token
                    expanded_tokens.append(token)
            else:
                expanded_tokens.append(token)
        return expanded_tokens

    @staticmethod
    def expand_pipeline(pipeline):
        """扩展整个命令管道中的通配符"""
        expanded_pipeline = []
        for command_tokens in pipeline:
            expanded_tokens = WildcardExpander.expand_tokens(command_tokens)
            if expanded_tokens:
                expanded_pipeline.append(expanded_tokens)
        return expanded_pipeline

    @staticmethod
    def _has_wildcard(token):
        """检查字符串是否包含通配符"""
        wildcard_chars = ['*', '?', '[', ']']
        return any(char in token for char in wildcard_chars)