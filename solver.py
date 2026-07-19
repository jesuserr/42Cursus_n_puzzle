import heapq
from itertools import count
from constants import FAIL_MARK
from exceptions import GoalReached, NoSolutionFound
counter = count()


def possible_moves(open_set, closed_set, size, heuristic, goal_state):
    f_cost, h_cost, _, board = heapq.heappop(open_set)
    g_cost = f_cost - h_cost + 1
    closed_set.add(tuple(board))
    zero_position = board.index(0)
    zero_position_y, zero_position_x = divmod(zero_position, size)
    if zero_position_x > 0:
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position - 1]
        new_board[zero_position - 1] = 0
        if tuple(new_board) not in closed_set:
            h_cost = heuristic(new_board, goal_state, size)
            if h_cost == 0:
                closed_set.add(tuple(new_board))
                raise GoalReached("Goal state reached")
            heapq.heappush(open_set, (g_cost + h_cost, h_cost, next(counter), new_board))
            print(f"New board, f_cost, g_cost, h_cost: {new_board}, {g_cost + h_cost}, {g_cost}, {h_cost}")
    if zero_position_x < size - 1:
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position + 1]
        new_board[zero_position + 1] = 0
        if tuple(new_board) not in closed_set:
            h_cost = heuristic(new_board, goal_state, size)
            if h_cost == 0:
                closed_set.add(tuple(new_board))
                raise GoalReached("Goal state reached")
            heapq.heappush(open_set, (g_cost + h_cost, h_cost, next(counter), new_board))
            print(f"New board, f_cost, g_cost, h_cost: {new_board}, {g_cost + h_cost}, {g_cost}, {h_cost}")
    if zero_position_y > 0:
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position - size]
        new_board[zero_position - size] = 0
        if tuple(new_board) not in closed_set:
            h_cost = heuristic(new_board, goal_state, size)
            if h_cost == 0:
                closed_set.add(tuple(new_board))
                raise GoalReached("Goal state reached")
            heapq.heappush(open_set, (g_cost + h_cost, h_cost, next(counter), new_board))
            print(f"New board, f_cost, g_cost, h_cost: {new_board}, {g_cost + h_cost}, {g_cost}, {h_cost}")
    if zero_position_y < size - 1:
        new_board = board.copy()
        new_board[zero_position] = new_board[zero_position + size]
        new_board[zero_position + size] = 0
        if tuple(new_board) not in closed_set:
            h_cost = heuristic(new_board, goal_state, size)
            if h_cost == 0:
                closed_set.add(tuple(new_board))
                raise GoalReached("Goal state reached")
            heapq.heappush(open_set, (g_cost + h_cost, h_cost, next(counter), new_board))
            print(f"New board, f_cost, g_cost, h_cost: {new_board}, {g_cost + h_cost}, {g_cost}, {h_cost}")


def solve_puzzle(size, board, goal_state, heuristic):
    print(f"\nPuzzle size: {size}")
    print(f"Puzzle board: {board}")
    print(f"Goal state:   {goal_state}")
    print(f"Heuristic:   {heuristic.__name__}\n")

    open_set = []
    closed_set = set()
    g_cost = 0
    h_cost = heuristic(board, goal_state, size)
    heapq.heappush(open_set, (g_cost + h_cost, h_cost, next(counter), board))
    while open_set:
        try:
            possible_moves(open_set, closed_set, size, heuristic, goal_state)
            print("\n")
        except GoalReached:
            break
    else:
        raise NoSolutionFound(f"No solution found {FAIL_MARK} ")
    print("Iter count: ", next(counter))
    print("closed set: ", closed_set)
    print("closed set length: ", len(closed_set))
    print("open set length: ", len(open_set))


    """
    #heapq.heappush(open_set, (f_cost, h_cost, next(counter), board))
    heapq.heappush(open_set, (8, 7, next(counter), [2,0,3,1,4,5,8,7,6]))
    heapq.heappush(open_set, (6, 5, next(counter), [1,2,3,0,4,5,8,7,6]))
    closed_set.add(tuple(heapq.heappop(open_set)[-1])) #better unpack it
    #print(heapq.heappop(open_set))
    heapq.heappush(open_set, (8, 6, next(counter), [1,2,3,4,0,5,8,7,6]))
    heapq.heappush(open_set, (6, 4, next(counter), [1,2,3,8,4,5,0,7,6]))
    print(heapq.heappop(open_set))
    heapq.heappush(open_set, (6, 3, next(counter), [1,2,3,8,4,5,7,0,6]))
    print(heapq.heappop(open_set))
    #heapq.heappush(open_set, (f_cost, neighbors[0]))
    #print(heapq.heappop(open_set))
    print(f"Closed set: {closed_set}")
    #f_cost, h_cost, tie_breaker, board = heapq.heappop(open_set)
    #closed_set.add(tuple(board))"""
    """
    print(f"\nInitial board: {board}")
    print(f"Initial heuristic value: {h_cost}")
    print(f"Initial g_cost: {g_cost}")
    print(f"Initial f(n) = g(n) + h(n): {f_cost}")
    print(f"Initial open set: {open_set}")
    print(f"Initial closed set: {closed_set}")"""


# heapq (open set)    →  always gives you the cheapest unexplored node O(log n)
# set() (closed set)  →  instantly tells you if a node was already seen O(1)
