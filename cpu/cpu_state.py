import cpu.utils as u

class CPUState:
    def __init__(self, init_string, name, line):
        self.name = name
        self.line = line
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

    def core_row(self):
        if not self.is_online() or self.calculate_del_tot() == 0:
            return (self.name.strip(), self.line, 0.0, False)
        return (self.name.strip(), self.line, self.calculate_core_usage(), True)

    def key_rows(self):
        if not self.is_online() or sum(self.__delta.values()) == 0:
            return [ (key, self.line + 1 + i, 0.0, False) for i, key in enumerate(u.INIT_KEYS) ]
        return [ (key, self.line + 1 + i, usage, True)
                 for i, (key, usage) in enumerate(self.calculate_key_usage()) ]