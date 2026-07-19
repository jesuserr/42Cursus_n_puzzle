import random
from solvability import check_puzzle_solvability
from constants import PASS_MARK


# Build the goal state: numbers 1..size*size-1 spiraling clockwise
# inward from the top-left corner, with the blank (0) as the last cell
# the spiral would have filled.
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


# Shuffle a board of the given size until it's solvable against the
# snail goal state. Returns (size, board, goal_state).
def generate_random_puzzle(size):
    goal_state = build_snail_goal(size)
    print(f'Generating random [{size}x{size}] solvable puzzle ', end='')
    print(end='', flush=True)
    board = list(range(size * size))
    random.shuffle(board)
    while not check_puzzle_solvability(size, board, goal_state):
        random.shuffle(board)
    print(f'{PASS_MARK}')
    return size, board, goal_state
