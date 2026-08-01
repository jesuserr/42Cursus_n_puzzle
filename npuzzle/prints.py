from npuzzle.constants import PASS_MARK
# Total width, in characters, of the asterisk banners framing the output.
BANNER_WIDTH = 60
# Character drawn in place of the blank tile, which is stored internally as 0.
BLANK_CELL = '_'


# Print a header summarizing the puzzle before the search starts: its size,
# the starting board, the goal board, the search variant and which heuristic
# is in use. board and goal_state are drawn as size x size grids. Uniform cost
# ignores the heuristic, so in that variant it is reported as None.
def print_initial_state(size, board, goal_state, heuristic, variant):
    print("\n" + " PUZZLE SETUP ".center(BANNER_WIDTH, "*"))
    print(f"Puzzle size:   {size} x {size}\n")
    print("Initial state:")
    _print_board(board, size)
    print("\nGoal state:")
    _print_board(goal_state, size)
    print(f"\nVariant:       {variant}")
    if variant == 'uniform_cost':
        print("Heuristic:     None (uniform cost search)")
    else:
        print(f"Heuristic:     {heuristic.__name__}")
    print()


# Print a single state as a size x size grid, right-aligning every cell to the
# width of the largest tile so columns line up regardless of puzzle size. The
# blank is stored as 0 but drawn as an underscore, so it reads as an empty
# slot instead of as another tile.
def _print_board(state, size):
    width = len(str(size * size - 1))
    for row in range(size):
        cells = state[row * size:(row + 1) * size]
        print(" ".join(f"{cell if cell != 0 else BLANK_CELL:>{width}}"
                       for cell in cells))


# Print the four values the subject asks for at the end of a successful
# search: the ordered start -> goal sequence of states, each labelled
# "Initial:" or "Step N:" and drawn as a size x size square, the number of
# moves (path length minus the initial state), the time complexity (total
# states selected from the open set) and the size complexity (peak number of
# states held in memory at once).
def print_solution(final_path, size, time_complexity, size_complexity):
    print("\r" + " PUZZLE SOLUTION ".center(BANNER_WIDTH, "*"))
    print(f"Solution found {PASS_MARK}")
    print("Solution sequence (initial -> goal):")
    for i, state in enumerate(final_path):
        print("Initial:" if i == 0 else f"Step {i}:")
        _print_board(state, size)
        print()
    print(f"Number of moves:                        {len(final_path) - 1:,}")
    print(f"Time complexity (states selected):      {time_complexity:,}")
    print(f"Size complexity (max states in memory): {size_complexity:,}")
