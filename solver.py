import heapq
from itertools import count
from constants import FAIL_MARK
from exceptions import GoalReached, NoSolutionFound
from prints import print_initial_state, print_solution
counter = count()


# Record new_board's parent, score it, and either raise GoalReached (if it's
# the goal) or push it onto open_set. Skips new_board entirely if it's
# already in closed_set.
def consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                      goal_state, size, g_cost, open_set):
    if tuple(new_board) in closed_set:
        return
    came_from[tuple(new_board)] = tuple(board)
    h_cost = heuristic(new_board, goal_state, size)
    if h_cost == 0:
        closed_set.add(tuple(new_board))
        raise GoalReached("Goal state reached")
    heapq.heappush(open_set, (g_cost + h_cost, h_cost, next(counter),
                   new_board))


def expand_board(open_set, closed_set, size, heuristic, goal_state, came_from):
    f_cost, h_cost, _, board = heapq.heappop(open_set)
    g_cost = f_cost - h_cost + 1
    closed_set.add(tuple(board))
    zero_position = board.index(0)
    zero_position_y, zero_position_x = divmod(zero_position, size)
    if zero_position_x > 0:
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position - 1]
        new_board[zero_position - 1] = 0
        consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                          goal_state, size, g_cost, open_set)
    if zero_position_x < size - 1:
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position + 1]
        new_board[zero_position + 1] = 0
        consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                          goal_state, size, g_cost, open_set)
    if zero_position_y > 0:
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position - size]
        new_board[zero_position - size] = 0
        consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                          goal_state, size, g_cost, open_set)
    if zero_position_y < size - 1:
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position + size]
        new_board[zero_position + size] = 0
        consider_neighbor(new_board, board, closed_set, came_from, heuristic,
                          goal_state, size, g_cost, open_set)


def solve_puzzle(size, board, goal_state, heuristic):
    print_initial_state(size, board, goal_state, heuristic)
    open_set = []
    closed_set = set()
    came_from = {tuple(board): None}
    g_cost = 0
    h_cost = heuristic(board, goal_state, size)
    heapq.heappush(open_set, (g_cost + h_cost, h_cost, next(counter), board))
    while open_set:
        try:
            expand_board(open_set, closed_set, size, heuristic, goal_state,
                         came_from)
        except GoalReached:
            break
    else:
        raise NoSolutionFound(f"No solution found {FAIL_MARK} ")
    print_solution(came_from, closed_set, open_set)

# heapq (open set)    →  always gives you the cheapest unexplored node O(log n)
# set() (closed set)  →  instantly tells you if a node was already seen O(1)
