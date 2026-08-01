import resource
from npuzzle.constants import FAIL_MARK
from npuzzle.exceptions import MemoryLimitExceeded
# Percentage of the reachable memory the search may hold before aborting.
MEMORY_LIMIT = 80


# Kilobytes the machine could still give this process, as estimated by the
# kernel in MemAvailable. Read on every check, so the limit follows the
# machine, down when other programs take memory and up when they free it.
# Excludes what this process already holds, which is why check_memory adds it
# back. Linux only: /proc/meminfo does not exist on macOS or Windows.
def _memory_available():
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])


# Peak memory of this process measured against everything it could still
# reach, both in kilobytes, the unit ru_maxrss and MemAvailable already use on
# Linux. Aborts the search once the process holds MEMORY_LIMIT percent of that
# total, and otherwise returns the three values for the caller to report.
def check_memory():
    used = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    budget = used + _memory_available()
    percent = used / budget * 100
    if percent >= MEMORY_LIMIT:
        raise MemoryLimitExceeded(
            f"\nPuzzle needs too much memory, aborted at {used >> 10:,}/"
            f"{budget >> 10:,} MiB ({percent:.1f}%) {FAIL_MARK} ")
    return used, budget, percent
