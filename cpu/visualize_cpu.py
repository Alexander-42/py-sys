import cpu.cpu_state as state
import cpu.cpu_state_handlers as state_handlers
import cpu.utils as cpu_utils
import terminal
import time

def visualize_all(bar_on):
    with open(cpu_utils.PROC_STAT_PATH, mode="r") as file:
        cpu = state_handlers.init_cpu_state(file)
        cpus = state_handlers.init_core_states(file, cpu_utils.CORES)
        time.sleep(0.5)
    file.close()
    try:
        initial_width = terminal.initialize_terminal()
        while True:
            terminal_width = terminal.check_terminal(initial_width)
            initial_width = terminal_width
            state_handlers.observe_whole_cpu_usage(bar_on, terminal_width, cpu_utils.PROC_STAT_PATH, cpus, cpu)
            time.sleep(.5)
    except KeyboardInterrupt:
        terminal.cleanup()
        print("Process safely exited by user")

def visualize_core(core_no, bar_on):
    with open(cpu_utils.PROC_STAT_PATH, mode="r") as file:
        core = state_handlers.init_single_core(file, core_no)
        time.sleep(0.5)
    file.close()
    try:
        initial_width = terminal.initialize_terminal()
        while True:
            terminal_width = terminal.check_terminal(initial_width)
            state_handlers.observe_single_core(bar_on, terminal_width, cpu_utils.PROC_STAT_PATH, core)
            initial_width = terminal_width
            time.sleep(0.5)
    except KeyboardInterrupt:
        terminal.cleanup()
        print("Process safely exited by user")