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

    def update_state(self, state_string):
        self.__prev_state_dict = self.__curr_state_dict
        self.__prev_busy = self.__curr_busy
        self.__prev_idle = self.__curr_idle
        self.__curr_state_dict = self.__parse_state_string(state_string)
        self.__curr_idle = int(self.__curr_state_dict["idle"]) + int(self.__curr_state_dict["iowait"])
        self.__curr_busy = sum([int(val) for val in self.__curr_state_dict.values()]) - self.__curr_idle

    def calculate_delta(self):
        for key in self.__curr_state_dict.keys():
            self.__delta[f"{key}_del"] = int(self.__curr_state_dict[key]) - int(self.__prev_state_dict[key])

    def calculate_usage(self):
        del_busy = self.__curr_busy-self.__prev_busy
        del_idle = self.__curr_idle-self.__prev_idle
        return 100*del_busy/(del_busy + del_idle)

    def __cpu_usage_bar(self):
        usage = self.calculate_usage()
        num_bars = int((usage * BAR_LENGTH) // 100)
        bar = "["
        for _ in range(num_bars):
            bar += "|"
        for _ in range(num_bars, BAR_LENGTH):
            bar += " "
        bar += "]"

        return bar, usage

    def print_bar(self):
        bar, usage = self.__cpu_usage_bar()
        print(f"{bar} {self.name.strip()} {round(usage, 1)}%")

def init_cpu_states(file):
    cpus = {}

    for line in file:
        if line[3] == ' ':
            cpus[line[0:4]] = CPUState(line, line[0:4])
        elif line[3].isnumeric():
            cpus[line[0:4]] = CPUState(line, line[0:4])

    return cpus

def observe_cpu_state(filepath, cpus):
    with open(filepath, mode="r") as file:
        for line in file:
            this_cpu = cpus.get(line[0:4])
            if this_cpu:
                this_cpu.update_state(line)
                this_cpu.print_bar()
            else:
                break
    file.close()
