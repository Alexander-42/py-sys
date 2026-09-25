import cpu.visualize_cpu as visualize_cpu
import cpu.utils as cpu_utils
import argparse
import terminal

def arg_parser():
    parser = argparse.ArgumentParser(description="System monitoring written in python")

    parser.add_argument(
        "-c", "--core",
        type=int,
        default=-1,
        help="Select the CPU core (default: -1 all cores)."
    )

    parser.add_argument(
        "-b", "--bar",
        action="store_false",
        help="Disable bar-graph of cpu core usage."
    )

    return parser.parse_args()

def main():
    args = arg_parser()

    if args.core != -1 and not cpu_utils.is_viable_core(args.core):
        cpu_utils.invalid_core_number(args)
        return

    tui = terminal.SysTui(0, cpu_utils.CORES)
    tui.initialize_terminal()

    try:
        core = args.core if args.core != -1 else None
        while True:
            tui.selector_line = 0
            tui.clear_screen()
            if core is None:
                tui.lines = cpu_utils.CORES
                core = visualize_cpu.visualize_all(args.bar, tui)
            else:
                tui.lines = len(cpu_utils.INIT_KEYS)
                core = visualize_cpu.visualize_core(core, args.bar, tui)
    except KeyboardInterrupt:
        pass
    finally:
        tui.cleanup()
    print("Process safely exited by user")

if __name__ == "__main__":
    main()