import random
from solvability import check_puzzle_solvability
from parser import PASS_MARK


def generate_random_puzzle(size):
    board = list(range(size * size))
    print(f'Generating a random [{size}x{size}] solvable puzzle ', end='')
    print(end='', flush=True)
    random.shuffle(board)
    while not check_puzzle_solvability(size, board):
        random.shuffle(board)
    print(f'{PASS_MARK}')
    return size, board