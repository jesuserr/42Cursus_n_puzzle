def check_puzzle_solvability(size, puzzle, goal):
    goal_position = {value: index for index, value in enumerate(goal)}
    ranks = [goal_position[tile] for tile in puzzle if tile != 0]
    inversions = sum(
        1 for i in range(len(ranks))
        for j in range(i + 1, len(ranks))
        if ranks[i] > ranks[j]
    )
    if size % 2 == 1:
        return inversions % 2 == 0
    current_blank_row = puzzle.index(0) // size
    goal_blank_row = goal.index(0) // size
    row_distance = abs(current_blank_row - goal_blank_row)
    return (inversions + row_distance) % 2 == 0
