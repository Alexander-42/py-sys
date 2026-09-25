import os
import sys
import select
import shutil
import termios
import tty

class SysTui:
    def __init__(self, selector_line, lines):
        self.selector_line = selector_line
        self.lines = lines
        self.__action = False
        self.__old_settings = None
        self.__fd = sys.stdin.fileno()
        self.__pending = ''

    def __read_available(self):
        data = ''
        while select.select([self.__fd], [], [], 0)[0]:
            chunk = os.read(self.__fd, 1024)
            if not chunk:
                break
            data += chunk.decode(errors='ignore')
        return data

    def __detect_input(self):
        buffer = self.__pending + self.__read_available()
        self.__pending = ''
        i = 0
        while i < len(buffer):
            ch = buffer[i]
            if ch == '\x1b':
                if len(buffer) - i < 3:
                    self.__pending = buffer[i:]
                    return
                if buffer[i + 1] == '[':
                    if buffer[i + 2] == 'A':
                        if self.selector_line > 0:
                            self.selector_line -= 1
                    elif buffer[i + 2] == 'B':
                        if self.selector_line < self.lines:
                            self.selector_line += 1
                i += 3
                continue
            if ch in ('\r', '\n'):
                self.__action = True
            i += 1

    def is_action(self):
        if not self.__action:
            return -1
        self.__action = False
        return self.selector_line

    def __get_cols(self):
        return shutil.get_terminal_size().columns

    def get_width(self):
        return self.__get_cols()

    def clear_screen(self):
        print('\x1b[2J')
        print('\x1b[H')

    def __usage_bar(self, label, percent, terminal_width):
        bar_width = terminal_width - len(label) - 10
        num_bars = int((percent * bar_width) // 100)
        return "[" + num_bars*"|" + (bar_width - num_bars)*" " + "]"

    def __line_whitespace_format(self, print_string, terminal_width):
        print_string += (terminal_width - len(print_string))*' '
        return print_string

    def __format_row(self, row, terminal_width, bar_on):
        label, _, percent, status = row
        if not status:
            row_string = f"{label} is offline"
        elif bar_on:
            bar = self.__usage_bar(label, percent, terminal_width)
            row_string = f"{bar} {label} {round(percent, 1)}%"
        else:
            row_string = f"{label} usage is at {round(percent, 1)}%"
        return self.__line_whitespace_format(row_string, terminal_width)

    def print_row(self, row, terminal_width, bar_on):
        row_string = self.__format_row(row, terminal_width, bar_on)
        if row[1] == self.selector_line:
            print(f"\x1b[7m{row_string}\x1b[0m")
        else:
            print(row_string)

    def print_rows(self, rows, terminal_width, bar_on):
        for row in rows:
            self.print_row(row, terminal_width, bar_on)

    def initialize_terminal(self):
        self.__old_settings = termios.tcgetattr(self.__fd)
        tty.setcbreak(self.__fd)
        print('\x1b[?1049h')
        print('\x1b[?25l')
        print('\x1b[H')
        return self.__get_cols()

    def cleanup(self):
        if self.__old_settings != None:
            termios.tcsetattr(self.__fd, termios.TCSADRAIN, self.__old_settings)
        print('\x1b[?1049l')
        print('\x1b[?25h')

    def check_terminal(self, prev_width):
        self.__detect_input()
        print('\x1b[H')
        width = self.__get_cols()
        if (prev_width != width):
            print('\x1b[2J')
            print('\x1b[H')
        return width
