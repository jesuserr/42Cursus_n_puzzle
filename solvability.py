def build_snail_goal(size):
    snail_board_goal = [0] * (size * size)
    top, bottom, left, right = 0, size - 1, 0, size - 1
    number = 1
    while top <= bottom and left <= right:
        for column in range(left, right + 1):
            snail_board_goal[top * size + column] = number
            number += 1
        top += 1
        for row in range(top, bottom + 1):
            snail_board_goal[row * size + right] = number
            number += 1
        right -= 1
        if top <= bottom:
            for column in range(right, left - 1, -1):
                snail_board_goal[bottom * size + column] = number
                number += 1
            bottom -= 1
        if left <= right:
            for row in range(bottom, top - 1, -1):
                snail_board_goal[row * size + left] = number
                number += 1
            left += 1
    snail_board_goal[snail_board_goal.index(size * size)] = 0
    return snail_board_goal


def check_puzzle_solvability(size, puzzle):
    goal = build_snail_goal(size)
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
