def print_initial_state(size, board, goal_state, heuristic):
    print(f"\nPuzzle size:   {size} x {size}")
    print(f"Initial state: {board}")
    print(f"Goal state:    {goal_state}")
    print(f"Heuristic:     {heuristic.__name__}\n")


# Print a single state as a size x size grid, right-aligning every cell to the
# width of the largest tile so columns line up regardless of puzzle size.
def print_board(state, size):
    width = len(str(size * size - 1))
    for row in range(size):
        cells = state[row * size:(row + 1) * size]
        print(" ".join(f"{cell:>{width}}" for cell in cells))


# Print the four values the subject asks for at the end of a successful
# search: the ordered start -> goal sequence of states (each drawn as a
# size x size square), the number of moves (path length minus the initial
# state), the time complexity (total states selected from the open set) and
# the size complexity (peak number of states held in memory at once).
def print_solution(final_path, size, time_complexity, size_complexity):
    print("Solution sequence (initial -> goal):")
    for state in final_path:
        print_board(state, size)
        print()
    print(f"Number of moves:                        {len(final_path) - 1}")
    print(f"Time complexity (states selected):      {time_complexity}")
    print(f"Size complexity (max states in memory): {size_complexity}")
