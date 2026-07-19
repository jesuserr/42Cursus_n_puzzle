# Raised to unwind the search as soon as a neighbor with h_cost == 0 is
# generated, so solve_puzzle's while loop can stop without exploring further.
class GoalReached(Exception):
    pass


# Raised when open_set is exhausted without ever raising GoalReached.
class NoSolutionFound(Exception):
    pass
