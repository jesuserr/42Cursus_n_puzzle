# Raised when a new neighbor turns out to be the goal state. It carries that
# board, so solve_puzzle can stop the search and rebuild the path from it.
class GoalReached(Exception):
    pass


# Raised when open_set is exhausted without ever raising GoalReached.
class NoSolutionFound(Exception):
    pass


# Raised when the peak memory of the process reaches MEMORY_LIMIT percent of
# what it can still reach, so the puzzle is abandoned before the kernel runs
# out of memory and kills it.
class MemoryLimitExceeded(Exception):
    pass
