def print_initial_state(size, board, goal_state, heuristic):
    print(f"\nPuzzle size:  {size}")
    print(f"Puzzle board: {board}")
    print(f"Goal state:   {goal_state}")
    print(f"Heuristic:    {heuristic.__name__}\n")


def print_solution(came_from, closed_set, open_set):
    print("\nSolution path:")
    for each in came_from:
        print(each, " : ", came_from[each])
    # print("closed set: ", closed_set)
    print("closed set length: ", len(closed_set))
    print("open set length: ", len(open_set))
