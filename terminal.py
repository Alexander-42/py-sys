import shutil

def get_cols():
    return shutil.get_terminal_size().columns

def initialize_terminal():
    print('\x1b[?1049h')
    print('\x1b[?25l')
    print('\x1b[H')
    return get_cols()

def cleanup():
    print('\x1b[?1049h')
    print('\x1b[?25h')
    print('\x1b[H')

def check_terminal(prev_width):
    print('\x1b[H')
    width = get_cols()
    if (prev_width != width):
        print('\x1b[2J')
        print('\x1b[H')
    return width
    