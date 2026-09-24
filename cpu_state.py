INIT_KEYS=[
    "user",
    "nice",
    "system",
    "idle",
    "iowait",
    "irq",
    "softirq",
    "steal",
    "guest",
    "guest_nice"
]

BAR_LENGTH = 80

class CPUState:
    def __init__(self, init_string, name):
        self.name = name
        self.init_string = init_string
        self.__init_keys = INIT_KEYS
        self.__prev_state_dict = {}
        self.__curr_state_dict = self.__parse_state_string(init_string)
        self.__delta = {}
        self.__curr_idle = int(self.__curr_state_dict["idle"]) + int(self.__curr_state_dict["iowait"])
        self.__curr_busy = sum([int(val) for val in self.__curr_state_dict.values()]) - self.__curr_idle
        self.__prev_busy = 0
        self.__prev_idle = 0

    def __parse_state_string(self, state_string):
        state_vals = state_string.split()[1:]
        return {i:k for i,k in zip(self.__init_keys, state_vals) }        

    def update_core_state(self, state_string):
        self.__prev_state_dict = self.__curr_state_dict
        self.__prev_busy = self.__curr_busy
        self.__prev_idle = self.__curr_idle
        self.__curr_state_dict = self.__parse_state_string(state_string)
        self.__curr_idle = int(self.__curr_state_dict["idle"]) + int(self.__curr_state_dict["iowait"])
        self.__curr_busy = sum([int(val) for val in self.__curr_state_dict.values()]) - self.__curr_idle
        self.calculate_delta()

    def calculate_delta(self):
        for key in self.__curr_state_dict.keys():
            self.__delta[f"{key}_del"] = int(self.__curr_state_dict[key]) - int(self.__prev_state_dict[key])

    def calculate_core_usage(self):
        del_busy = self.__curr_busy-self.__prev_busy
        del_idle = self.__curr_idle-self.__prev_idle
        return 100*del_busy/(del_busy + del_idle)

    def calculate_key_usage(self):
        key_usages=[]
        for key in self.__delta.keys():
            key_usages.append(100*self.__delta[key]/(sum(self.__delta.values())))
        return key_usages

    def print_core_usage(self, terminal_width):
        usage = self.calculate_core_usage()
        usage_string = f"{self.name} usage is at {round(usage,1)}%"
        usage_string += (terminal_width-len(usage_string))*' '
        print(usage_string)

    def print_key_usages(self, terminal_width):
        key_usages = self.calculate_key_usage()
        key_usage_pairs = zip(INIT_KEYS, key_usages)
        print('% of core usage')
        for key, usage in key_usage_pairs:
            usage_string = f"{key}: {round(usage, 1)}%"
            usage_string += (terminal_width-len(usage_string))*' '
            print(usage_string)

    def __cpu_usage_bar(self, terminal_width):
        terminal_width = terminal_width - 15
        usage = self.calculate_core_usage()
        num_bars = int((usage * terminal_width) // 100)
        bar = "["
        for _ in range(num_bars):
            bar += "|"
        for _ in range(num_bars, terminal_width):
            bar += " "
        bar += "]"

        return bar, usage

    def print_core_bar(self, terminal_width):
        bar, usage = self.__cpu_usage_bar(terminal_width)
        bar_string = f"{bar} {self.name.strip()} {round(usage, 1)}%"
        bar_string += (terminal_width-len(bar_string))*' '
        print(bar_string)

def init_core_states(file):
    cores = {}

    for line in file:
        if line[3].isnumeric():
            cores[line[0:4]] = CPUState(line, line[0:4])
        else:
            pass

    return cores

def init_cpu_state(file):
    cpu_line = file.readline()
    cpu = CPUState(cpu_line, "global")

    return cpu

def init_single_core(file, core_no):
    for line in file:
        if line[0:4] == f"cpu{core_no}":
            core = CPUState(line, f"cpu{core_no}")

    return core

def observe_single_core(terminal_width, filepath, core):
    with open(filepath, mode="r") as file:
        for line in file:
            if line[0:4] == core.name:
                core.update_core_state(line)
                core.print_core_usage(terminal_width)
                core.print_key_usages(terminal_width)
    file.close()

def observe_whole_cpu_usage(terminal_width, filepath, cores, cpu):
    with open(filepath, mode="r") as file:
        for line in file:
            if line[0:4] == "cpu ":
                cpu.update_core_state(line)
                cpu.print_core_usage(terminal_width)
            try:
                this_core = cores.get(line[0:4])
                if this_core:
                    this_core.update_core_state(line)
                    this_core.print_core_bar(terminal_width)
            finally:
                pass
    file.close()

def print_core_status(core):
    core.print_bar()