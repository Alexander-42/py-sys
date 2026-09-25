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

    def __get_cols(self):
        return shutil.get_terminal_size().columns

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
        print('\x1b[H')

    def check_terminal(self, prev_width):
        self.__detect_input()
        print('\x1b[H')
        width = self.__get_cols()
        if (prev_width != width):
            print('\x1b[2J')
            print('\x1b[H')
        return width
