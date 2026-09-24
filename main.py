import cpu_state
import time
import shutil
import argparse
import os

PROC_STAT_PATH = "/proc/stat"
CORES = os.cpu_count()

def initialize_terminal():
    print('\x1b[?1049h')
    print('\x1b[?25l')
    print('\x1b[H')
    return shutil.get_terminal_size().columns

def cleanup():
    print('\x1b[?1049h')
    print('\x1b[?25h')
    print('\x1b[H')

def check_terminal(prev_width):
    print('\x1b[H')
    size = shutil.get_terminal_size()
    width = size.columns
    if (prev_width != width):
        print('\x1b[2J')
        print('\x1b[H')
    return width
    
def visualize_all(bar_on):
    with open(PROC_STAT_PATH, mode="r") as file:
        cpu = cpu_state.init_cpu_state(file)
        cpus = cpu_state.init_core_states(file, CORES)
        time.sleep(0.5)
    file.close()
    try:
        initial_width = initialize_terminal()
        while True:
            terminal_width = check_terminal(initial_width)
            initial_width = terminal_width
            cpu_state.observe_whole_cpu_usage(bar_on, terminal_width, PROC_STAT_PATH, cpus, cpu)
            time.sleep(.5)
    except KeyboardInterrupt:
        cleanup()
        print("Process safely exited by user")

def visualize_core(core_no, bar_on):
    with open(PROC_STAT_PATH, mode="r") as file:
        core = cpu_state.init_single_core(file, core_no)
        time.sleep(0.5)
    file.close()
    try:
        initial_width = initialize_terminal()
        while True:
            terminal_width = check_terminal(initial_width)
            cpu_state.observe_single_core(bar_on, terminal_width, PROC_STAT_PATH, core)
            initial_width = terminal_width
            time.sleep(0.5)
    except KeyboardInterrupt:
        cleanup()
        print("Process safely exited by user")

def arg_parser():
    parser = argparse.ArgumentParser(description="System monitoring written in python")

    parser.add_argument(
        "-c", "--core",
        type=int,
        default=-1,
        help="Select the CPU core (default: -1 all cores)."
    )

    parser.add_argument(
        "-b", "--bar",
        action="store_false",
        help="Disable bar-graph of cpu core usage."
    )

    return parser.parse_args()

def is_viable_core(core):
    return core >= 0 and core < CORES

def main():
    args = arg_parser()
    print(args)

    if args.core == -1:
        visualize_all(args.bar)
    elif is_viable_core(args.core):
        visualize_core(args.core, args.bar)
    else:
        print(f"Invalid core: {args.core} (0-{CORES - 1})")


if __name__ == "__main__":
    main()