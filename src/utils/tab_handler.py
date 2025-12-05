import sys
import os


class TabHandler:
    def __init__(self, completer):
        self.completer = completer
        self.last_completions = []
        self.completion_index = 0

    def handle_tab(self, current_input, cursor_pos, cwd):
        """处理Tab键按下事件"""
        text_before_cursor = current_input[:cursor_pos]
        completions = self.completer.get_completions(text_before_cursor, cwd)

        if not completions:
            return current_input, cursor_pos, False

        if len(completions) == 1:
            completion = completions[0]
            new_input, new_pos = self._apply_completion(
                current_input, cursor_pos, text_before_cursor, completion
            )
            return new_input, new_pos, True
        else:
            print()
            for i, comp in enumerate(completions):
                if i % 4 == 0:
                    print()
                print(f"{comp:<20}", end="")
            print()

            sys.stdout.write(current_input)
            sys.stdout.flush()

            return current_input, cursor_pos, False

    def _apply_completion(self, current_input, cursor_pos, text_before_cursor, completion):
        """应用补全到输入"""
        parts = text_before_cursor.split(' ')
        if len(parts) > 1:
            prefix = ' '.join(parts[:-1]) + ' '
            if prefix != ' ':
                replacement = prefix + completion
            else:
                replacement = completion
        else:
            replacement = completion

        new_cursor_pos = len(replacement)
        new_input = replacement + current_input[cursor_pos:]

        return new_input, new_cursor_pos