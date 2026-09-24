import os

def is_viable_core(core):
    return core >= 0 and core < CORES

def invalid_core_number(args):
    print(f"Invalid core: {args.core} (0-{CORES - 1})")

PROC_STAT_PATH = "/proc/stat"
CORES = os.cpu_count()
EMPTY_INIT_STRING_VALS = ("0 ")*9 + "0"
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
