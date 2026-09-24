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

EMPTY_INIT_STRING_VALS = ("0"+" ")*9 + "0"

class CPUState:
    def __init__(self, init_string, name):
        self.name = name
        self.__online = True
        self.__online = self.__is_online()
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

    def __is_online(self):
        if self.name == "global" or self.name == "cpu0":
            return True
        with open(f"/sys/devices/system/cpu/{self.name}/online") as file:
            return file.readline().strip() == "1"

    def update_core_state(self, state_string):
        self.__online = self.__is_online()
        self.__prev_state_dict = self.__curr_state_dict
        self.__prev_busy = self.__curr_busy
        self.__prev_idle = self.__curr_idle
        self.__curr_state_dict = self.__parse_state_string(state_string)
        self.__curr_idle = int(self.__curr_state_dict["idle"]) + int(self.__curr_state_dict["iowait"])
        self.__curr_busy = sum([int(val) for val in self.__curr_state_dict.values()]) - self.__curr_idle
        self.calculate_delta()

    def calculate_delta(self):
        if self.__online:
            for key in self.__curr_state_dict.keys():
                self.__delta[f"{key}_del"] = int(self.__curr_state_dict[key]) - int(self.__prev_state_dict[key])

    def calculate_core_usage(self):
        if self.__online:
            del_busy = self.__curr_busy-self.__prev_busy
            del_idle = self.__curr_idle-self.__prev_idle
            return 100*del_busy/(del_busy + del_idle)

    def calculate_key_usage(self):
        if self.__online:
            key_usages=[]
            for key in self.__delta.keys():
                key_usages.append(100*self.__delta[key]/(sum(self.__delta.values())))
            return zip(INIT_KEYS, key_usages)

    def print_core_usage(self, terminal_width):
        if self.__online:
            usage = self.calculate_core_usage()
            usage_string = f"{self.name} usage is at {round(usage,1)}%"
            usage_string += (terminal_width-len(usage_string))*' '
            print(usage_string)
        else:
            print(f"{self.name} is offline")

    def print_key_usages(self, terminal_width):
        if self.__online:
            key_usage_pairs = self.calculate_key_usage()
            print(f'Key as percentage of core usage')
            for key, usage in key_usage_pairs:
                usage_string = f"{key}: {round(usage, 1)}%"
                usage_string += (terminal_width-len(usage_string))*' '
                print(usage_string)

    def __cpu_usage_bar(self, terminal_width):
        terminal_width = terminal_width - 15
        if self.__online:
            usage = self.calculate_core_usage()
            num_bars = int((usage * terminal_width) // 100)
            bar = "["
            for _ in range(num_bars):
                bar += "|"
            for _ in range(num_bars, terminal_width):
                bar += " "
            bar += "]"

            return bar, usage
        else:
            return f"{"["+" "*(terminal_width-2)+"]"}" , "offline"

    def __key_usage_bars(self, terminal_width):
        bars = []
        terminal_width = terminal_width - 20
        key_usage_pairs = self.calculate_key_usage()
        for key, usage in key_usage_pairs:
            num_bars = int((usage * terminal_width) // 100)
            bar = "["
            for _ in range(num_bars):
                bar += "|"
            for _ in range(num_bars, terminal_width):
                bar += " "
            bar += "]"
            bars.append((bar, usage, key))
        return bars
            
        

    def print_core_bar(self, terminal_width):
        bar, usage = self.__cpu_usage_bar(terminal_width)
        if self.__online:
            bar_string = f"{bar} {self.name.strip()} {round(usage, 1)}%"
        else:
            bar_string = f"{bar} {self.name.strip()} {usage}"
        bar_string += (terminal_width-len(bar_string))*' '
        print(bar_string)

    def print_key_bars(self, terminal_width):
        if self.__online:
            bars = self.__key_usage_bars(terminal_width)
            bar_strings = [ f"{bar[0]} {bar[2].strip()} {round(bar[1],1)}%" for bar in bars ]
            for bstring in bar_strings:
                bstring += (terminal_width-len(bstring))*' '
                print(bstring)
    


def init_core_states(file, num_cores):
    cores = { f"cpu{i}": CPUState(f"cpu{i}" + " " + EMPTY_INIT_STRING_VALS, f"cpu{i}") for i in range(num_cores) }

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

def observe_single_core(bar_on, terminal_width, filepath, core):
    with open(filepath, mode="r") as file:
        for line in file:
            if line[0:4] == core.name:
                core.update_core_state(line)
                core.print_core_usage(terminal_width)
                if bar_on:
                    core.print_key_bars(terminal_width)
                else:
                    core.print_key_usages(terminal_width)
    file.close()

def observe_whole_cpu_usage(bar_on, terminal_width, filepath, cores, cpu):
    with open(filepath, mode="r") as file:
        for line in file:
            if line[0:4] == "cpu ":
                cpu.update_core_state(line)
                cpu.print_core_usage(terminal_width)
            try:
                this_core = cores.get(line[0:4])
                if this_core:
                    this_core.update_core_state(line)
                    if bar_on:
                        this_core.print_core_bar(terminal_width)
                    else:
                        this_core.print_core_usage(terminal_width)
            finally:
                break
    file.close()

def print_core_status(core):
    core.print_bar()