import cpu.utils as u

class CPUState:
    def __init__(self, init_string, name):
        self.name = name
        self.__online = True
        self.init_string = init_string
        self.__init_keys = u.INIT_KEYS
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

    def is_online(self):
        if self.name == "global" or self.name == "cpu0":
            return True
        with open(f"/sys/devices/system/cpu/{self.name}/online") as file:
            return file.readline().strip() == "1"

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

    def calculate_del_tot(self):
        del_busy = self.__curr_busy - self.__prev_busy
        del_idle = self.__curr_idle - self.__prev_idle
        return del_busy + del_idle

    def calculate_core_usage(self):
        del_busy = self.__curr_busy - self.__prev_busy
        del_idle = self.__curr_idle - self.__prev_idle
        return 100*del_busy/(del_busy + del_idle)

    def calculate_key_usage(self):
        key_usages=[]
        for key in self.__delta.keys():
            key_usages.append(100*self.__delta[key]/(sum(self.__delta.values())))
        return zip(u.INIT_KEYS, key_usages)

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

    def __line_whitespace_format(self, print_string, terminal_width):
        print_string += (terminal_width-len(print_string))*' '
        return print_string
    
    def print_core_usage(self, terminal_width):
            if self.is_online():
                usage = self.calculate_core_usage()
                usage_string = f"{self.name} usage is at {round(usage,1)}%"
                print(self.__line_whitespace_format(usage_string, terminal_width))
            else:
                print(f"Core {self.name} is offline")
    
    def print_key_usages(self, terminal_width):
        if self.is_online():
            key_usage_pairs = self.calculate_key_usage()
            print(f'Key as percentage of core usage')
            for key, usage in key_usage_pairs:
                usage_string = f"{key}: {round(usage, 1)}%"
                print(self.__line_whitespace_format(usage_string, terminal_width))
        

    def print_core_bar(self, terminal_width):
        if self.is_online() and self.calculate_del_tot() != 0:
            bar, usage = self.__cpu_usage_bar(terminal_width)
            bar_string = f"{bar} {self.name.strip()} {round(usage, 1)}%"
            print(self.__line_whitespace_format(bar_string, terminal_width))
        else:
            bar_string = f"{self.name.strip()} is offline"
            print(self.__line_whitespace_format(bar_string, terminal_width))

    def print_key_bars(self, terminal_width):
        if self.is_online():
            bars = self.__key_usage_bars(terminal_width)
            bar_strings = [ f"{bar[0]} {bar[2].strip()} {round(bar[1],1)}%" for bar in bars ]
            for bstring in bar_strings:
                print(self.__line_whitespace_format(bstring, terminal_width))