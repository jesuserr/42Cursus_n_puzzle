import heapq
import time
from itertools import count
from npuzzle.constants import FAIL_MARK
from npuzzle.exceptions import GoalReached, NoSolutionFound
from npuzzle.memory import check_memory
from npuzzle.prints import print_solution
counter = count()
# Number of explored states between refreshes of the search progress line.
PROGRESS_INTERVAL = 25000


# Rebuild the solution as an ordered list of boards from start to goal.
# came_from maps each board to the board it was reached from; the start board
# maps to None. Starting at goal_board, we follow those parent links backwards
# until we hit None, collecting boards goal -> start, then reverse the list so
# it reads start -> goal.
def _reconstruct_path(came_from, goal_board):
    final_path = []
    current_board = goal_board
    while current_board is not None:
        final_path.append(current_board)
        current_board = came_from[current_board]
    final_path.reverse()
    return final_path


# Record new_board's parent, score it, and either raise GoalReached (if it's
# the goal) or push it onto open_set. Skips new_board entirely if it's
# already in closed_set. Uniform cost pins h to 0, leaving greedy as the only
# variant needing an explicit f formula: with h at 0 the g + h sum already
# gives g. Entries rank by f, then h and g, with the counter last so full
# ties fall to insertion order and boards are never compared.
def _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                       goal_state, size, g_cost, open_set, variant):
    if tuple(new_board) in closed_set:
        return
    came_from[tuple(new_board)] = tuple(board)
    if new_board == goal_state:
        closed_set.add(tuple(new_board))
        raise GoalReached(tuple(new_board))
    if variant == 'uniform_cost':
        h_cost = 0
    else:
        h_cost = heuristic(new_board, goal_state, size)
    if variant == 'greedy':
        f_cost = h_cost
    else:
        f_cost = g_cost + h_cost
    heapq.heappush(open_set, (f_cost, h_cost, g_cost,
                   next(counter), new_board))


# One search iteration: heappop takes the board the variant rates best out of
# open_set, marks it as explored, and hands each of its neighbors to
# _consider_neighbor. g is carried in the tuple because greedy scores f = h,
# leaving no way to derive it; every neighbor sits one move further away,
# hence the + 1. A board joins closed_set the moment it is popped, meaning
# "already expanded, never look at it again", and there is no goal test here:
# the goal is caught in _consider_neighbor as soon as it is generated.
#
# The blank tile is what actually moves. From its (y, x) coordinates we know
# which of the four slides are legal: the bounds checks stop the blank from
# wrapping around a row edge or falling off the board. Each legal slide gets
# its own copy of board (copy() so siblings do not corrupt each other), then
# swaps the blank with the neighboring tile - written as two assignments
# because one of the two values is always 0.
def _expand_board(open_set, closed_set, size, heuristic, goal_state,
                  came_from, variant):
    _, _, g_cost, _, board = heapq.heappop(open_set)
    g_cost += 1
    closed_set.add(tuple(board))
    zero_position = board.index(0)
    zero_position_y, zero_position_x = divmod(zero_position, size)
    if zero_position_x > 0:                             # slide blank left
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position - 1]
        new_board[zero_position - 1] = 0
        _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                           goal_state, size, g_cost, open_set, variant)
    if zero_position_x < size - 1:                      # slide blank right
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position + 1]
        new_board[zero_position + 1] = 0
        _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                           goal_state, size, g_cost, open_set, variant)
    if zero_position_y > 0:                             # slide blank up
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position - size]
        new_board[zero_position - size] = 0
        _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                           goal_state, size, g_cost, open_set, variant)
    if zero_position_y < size - 1:                      # slide blank down
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position + size]
        new_board[zero_position + size] = 0
        _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                           goal_state, size, g_cost, open_set, variant)


# Drive the search: seed open_set with the start board, scored by the variant
# like any other, then expand boards one at a time until _consider_neighbor
# raises GoalReached. An open_set emptied without that raise means the goal is
# unreachable, which the while else reports. max_states follows the peak of
# open_set + closed_set, and every PROGRESS_INTERVAL explored boards
# check_memory refreshes the progress line, or aborts if the process is close
# to filling the memory it can still reach. The clock brackets the search
# alone, leaving the printing out of it. Ends by printing the rebuilt path.
def solve_puzzle(size, board, goal_state, heuristic, variant, timing):
    open_set = []
    closed_set = set()
    came_from = {tuple(board): None}
    g_cost = 0
    h_cost = (0 if variant == 'uniform_cost'
              else heuristic(board, goal_state, size))
    heapq.heappush(open_set, (g_cost + h_cost, h_cost, g_cost,
                              next(counter), board))
    max_states = len(open_set) + len(closed_set)
    start_time = time.perf_counter()
    while open_set:
        try:
            _expand_board(open_set, closed_set, size, heuristic, goal_state,
                          came_from, variant)
        except GoalReached as reached:
            goal_board = reached.args[0]
            elapsed_time = time.perf_counter() - start_time if timing else None
            break
        max_states = max(max_states, len(open_set) + len(closed_set))
        if len(closed_set) % PROGRESS_INTERVAL == 0:
            used, budget, percent = check_memory()
            print(f"\rExplored {len(closed_set):>11,}  │  Memory "
                  f"{used >> 10:>5,}/{budget >> 10:,} MiB ({percent:>5.1f}%)",
                  end="")
    else:
        raise NoSolutionFound(f"\nNo solution found {FAIL_MARK} ")
    max_states = max(max_states, len(open_set) + len(closed_set))
    final_path = _reconstruct_path(came_from, goal_board)
    print_solution(final_path, size, len(closed_set), max_states, elapsed_time)
