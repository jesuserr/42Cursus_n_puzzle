def print_initial_state(size, board, goal_state, heuristic):
    print(f"\nPuzzle size:  {size}")
    print(f"Puzzle board: {board}")
    print(f"Goal state:   {goal_state}")
    print(f"Heuristic:    {heuristic.__name__}\n")


def print_solution(closed_set, open_set, final_path):
    print("Solution path:")
    for state in final_path:
        print(state)
    print("Solution found in ", len(final_path) - 1, " moves.")
    print("Closed set length: ", len(closed_set))
    print("Open set length: ", len(open_set))
