
class State:
    def __init__(self, init_string, name):
        self.name = name
        self.init_string = init_string
        self.__init_keys = ["user",
                          "nice",
                          "system",
                          "idle",
                          "iowait",
                          "irq",
                          "softirq",
                          "steal",
                          "guest",
                          "guest_nice"]
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

    def print_curr_state_dict_and_name(self):
        print(self.name)
        print(self.__curr_state_dict)
        print("--------")

    def print_delta(self):
        print(self.__delta)

    def print_curr_busy(self):
        print(self.__curr_busy)

    def print_curr_idle(self):
        print(self.__curr_idle)

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

def init_cpu_states(file):
    cpus = {}

    for line in file:
        if line[3] == ' ':
            cpus[line[0:4]] = State(line, line[0:4])
        elif line[3].isnumeric():
            cpus[line[0:4]] = State(line, line[0:4])

    return cpus

def observe_state(cpus):
    file = open("/proc/stat")
    for line in file:
        this_cpu = cpus.get(line[0:4])
        if this_cpu:
            this_cpu.update_state(line)
            this_cpu.calculate_delta()
            print(this_cpu.name)
            print("Busy: ")
            this_cpu.print_curr_busy()
            print("Idle: ")
            this_cpu.print_curr_idle()
        else:
            break
    file.close()