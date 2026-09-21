import state

def main():
    file = open("/proc/stat")
    cpus = state.init_cpu_states(file)
    file.close()
    while True:
        state.observe_state(cpus)

    


if __name__ == "__main__":
    main()