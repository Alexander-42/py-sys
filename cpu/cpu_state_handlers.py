import cpu.cpu_state as state
import cpu.utils as utils

def init_core_states(file, num_cores):
    cores = { f"cpu{i}": state.CPUState(f"cpu{i}" + " " + utils.EMPTY_INIT_STRING_VALS, f"cpu{i}", i + 1) for i in range(num_cores) }

    for line in file:
        if line[3].isnumeric():
            cores[line[0:4]] = state.CPUState(line, line[0:4], int(line[3]) + 1)
        else:
            pass

    return cores

def init_cpu_state(file):
    cpu_line = file.readline()
    cpu = state.CPUState(cpu_line, "global", 0)

    return cpu

def init_single_core(file, core_no):
    for line in file:
        if line[0:4] == f"cpu{core_no}":
            core = state.CPUState(line, f"cpu{core_no}", 0)

    return core

def observe_single_core(bar_on, terminal_width, filepath, core, tui):
    with open(filepath, mode="r") as file:
        for line in file:
            if line[0:4] == core.name:
                core.update_core_state(line)
    file.close()
    tui.print_rows([core.core_row()] + core.key_rows(), terminal_width, bar_on)

def observe_whole_cpu_usage(bar_on, terminal_width, filepath, cores, cpu, tui):
    with open(filepath, mode="r") as file:
        for line in file:
            if line[0:4] == "cpu ":
                cpu.update_core_state(line)
            elif line[3].isnumeric():
                this_core = cores.get(line[0:4])
                this_core.update_core_state(line)
                cores[this_core.name] = this_core
            else:
                pass
    file.close()
    rows = [cpu.core_row()] + [ core.core_row() for core in cores.values() ]
    tui.print_rows(rows, terminal_width, bar_on)