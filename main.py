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
    tui = terminal.SysTui(0, cpu_utils.CORES)

    if args.core == -1:
        visualize_cpu.visualize_all(args.bar, tui)
    elif cpu_utils.is_viable_core(args.core):
        visualize_cpu.visualize_core(args.core, args.bar, tui)
    else:
        cpu_utils.invalid_core_number(args)

if __name__ == "__main__":
    main()