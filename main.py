import state
import time

def main():
    file = open("/proc/stat")
    cpus = state.init_cpu_states(file)
    file.close()
    time.sleep(0.5)
    while True:
        state.observe_state(cpus)
        time.sleep(.5)


if __name__ == "__main__":
    main()