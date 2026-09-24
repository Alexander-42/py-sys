import cpu_state
import time

PROC_STAT_PATH = "/proc/stat"

def initialize_terminal():
    print('\x1b[?1049h')
    print('\x1b[?25l')
    print('\x1b[H')

def cleanup():
    print('\x1b[?1049h')
    print('\x1b[?25h')
    print('\x1b[H')

def main():
    with open(PROC_STAT_PATH, mode="r") as file:
        cpus = cpu_state.init_cpu_states(file)
        time.sleep(0.5)
    file.close()
    try:
        initialize_terminal()
        while True:
            print('\x1b[H')
            cpu_state.observe_cpu_state(PROC_STAT_PATH, cpus)
            time.sleep(.5)
    except KeyboardInterrupt:
        cleanup()
        print("Process safely exited by user")


if __name__ == "__main__":
    main()