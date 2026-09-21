
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
                          "quest",
                          "quest_nice"]
        self.__prev_state_dict = {}
        self.__curr_state_dict = self.__parse_state_string(init_string)

    def __parse_state_string(self, state_string):
        state_vals = state_string.split()
        return {i:k for i,k in zip(self.__init_keys, state_vals) }
        

    def print_curr_state_dict_and_name(self):
        print(self.name)
        print(self.__curr_state_dict)
        print("--------")

    def update_state(self, state_string):
        self.__prev_state_dict = self.__curr_state_dict
        self.__curr_state_dict = self.__parse_state_string(state_string)
        

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
            print(this_cpu.print_curr_state_dict_and_name())
        else:
            break
    file.close()