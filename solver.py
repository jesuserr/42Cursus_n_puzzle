import heapq


def puzzle_solver(size, board, goal_state, heuristic):
    print(f"\nPuzzle size: {size}")
    print(f"Puzzle board: {board}")
    print(f"Goal state:   {goal_state}")
    print(f"Heuristic:   {heuristic.__name__}\n")
    open_set = []
    closed_set = set()
    closed_set.add(tuple(board))
    heuristic_value = heuristic(board, goal_state, size)
    cost = 0
    heapq.heappush(open_set, (cost + heuristic_value, board))
    heapq.heappush(open_set, (cost + heuristic_value + 1, goal_state))
    print(heapq.heappop(open_set))
    print(f"Initial board: {board}")
    print(f"Initial heuristic value: {heuristic_value}")
    print(f"Initial cost: {cost}")
    print(f"Initial f(n) = g(n) + h(n): {cost + heuristic_value}")
    print(f"Initial open set: {open_set}")


# heapq (open set)    →  always gives you the cheapest unexplored node O(log n)
# set() (closed set)  →  instantly tells you if a node was already seen O(1)
