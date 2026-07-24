import heapq
from itertools import count
from constants import FAIL_MARK
from exceptions import GoalReached, NoSolutionFound
from prints import print_initial_state, print_solution
counter = count()


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
# already in closed_set.
def _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                       goal_state, size, g_cost, open_set):
    if tuple(new_board) in closed_set:
        return
    came_from[tuple(new_board)] = tuple(board)
    h_cost = heuristic(new_board, goal_state, size)
    if h_cost == 0:
        closed_set.add(tuple(new_board))
        raise GoalReached(tuple(new_board))
    heapq.heappush(open_set, (g_cost + h_cost, h_cost, next(counter),
                   new_board))


# One A* iteration: take the most promising board out of open_set, mark it as
# explored, and hand each of its neighbors to _consider_neighbor.
#
# The heap is ordered by f_cost, so heappop always returns the board with the
# lowest f = g + h. We do not store g in the heap: since f and h travel
# together in the tuple, the popped board's own g is f_cost - h_cost, and
# every neighbor is exactly one move further away, hence the + 1. That g_cost
# is what _consider_neighbor scores the neighbors with.
#
# A board is added to closed_set the moment it is popped, meaning "already
# expanded, never look at it again". Note this is why solve_puzzle needs its
# h_cost == 0 shortcut: if the initial board is already the goal, it gets
# closed here and _consider_neighbor's closed_set check would then hide it
# forever, since the goal is only ever detected when it is generated.
#
# The blank tile is what actually moves. From its (y, x) coordinates we know
# which of the four slides are legal: the bounds checks stop the blank from
# wrapping around a row edge or falling off the board. Each legal slide gets
# its own copy of board (copy() so siblings do not corrupt each other), then
# swaps the blank with the neighboring tile - written as two assignments
# because one of the two values is always 0.
def _expand_board(open_set, closed_set, size, heuristic, goal_state,
                  came_from):
    f_cost, h_cost, _, board = heapq.heappop(open_set)
    g_cost = f_cost - h_cost + 1
    closed_set.add(tuple(board))
    zero_position = board.index(0)
    zero_position_y, zero_position_x = divmod(zero_position, size)
    if zero_position_x > 0:                             # slide blank left
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position - 1]
        new_board[zero_position - 1] = 0
        _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                           goal_state, size, g_cost, open_set)
    if zero_position_x < size - 1:                      # slide blank right
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position + 1]
        new_board[zero_position + 1] = 0
        _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                           goal_state, size, g_cost, open_set)
    if zero_position_y > 0:                             # slide blank up
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position - size]
        new_board[zero_position - size] = 0
        _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                           goal_state, size, g_cost, open_set)
    if zero_position_y < size - 1:                      # slide blank down
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position + size]
        new_board[zero_position + size] = 0
        _consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                           goal_state, size, g_cost, open_set)


def solve_puzzle(size, board, goal_state, heuristic):
    print_initial_state(size, board, goal_state, heuristic)
    open_set = []
    closed_set = set()
    came_from = {tuple(board): None}
    g_cost = 0
    h_cost = heuristic(board, goal_state, size)
    if (h_cost == 0):
        print_solution([board], size, 0, 1)
        return
    heapq.heappush(open_set, (g_cost + h_cost, h_cost, next(counter), board))
    max_states = len(open_set) + len(closed_set)
    while open_set:
        try:
            _expand_board(open_set, closed_set, size, heuristic, goal_state,
                          came_from)
        except GoalReached as reached:
            goal_board = reached.args[0]
            break
        max_states = max(max_states, len(open_set) + len(closed_set))
    else:
        raise NoSolutionFound(f"No solution found {FAIL_MARK} ")
    max_states = max(max_states, len(open_set) + len(closed_set))
    final_path = _reconstruct_path(came_from, goal_board)
    print_solution(final_path, size, len(closed_set), max_states)
