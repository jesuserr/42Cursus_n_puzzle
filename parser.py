import argparse

PASS_MARK = '\033[32m✓\033[0m'
FAIL_MARK = '\033[31m✗\033[0m'


def parse_arguments():
    arg_parser = argparse.ArgumentParser(
        usage="python3 n-puzzle.py [board] [-h] [-r size]",
        description="starting board default name: 'board'",
    )
    arg_parser.add_argument('board', nargs='?', default='board')
    arg_parser.add_argument('-r', type=int, metavar='size', dest='random',
                            help='generate random solvable puzzle of given size')
    args = arg_parser.parse_args()
    if args.random is not None and args.random < 3:
        print(f"Size must be at least 3 for a valid n-puzzle {FAIL_MARK}")
        exit(1)
    return args


def read_puzzle_file(filename):
    """Parse an n-puzzle file: line 0 is a comment, line 1 is the size,
    followed by `size` rows of `size` space-separated integers covering
    0..size*size-1 exactly once. Trailing '#' tokens in a row are comments.
    Returns (size, flat list of ints). Raises ValueError on any format issue.
    """
    print(f'Reading starting board from file "{filename}" ', end="")
    try:
        with open(filename) as f:
            contents_str = f.read()
        if not contents_str:
            raise ValueError(f"File '{filename}' is empty.")
        contents_list = contents_str.strip().splitlines()
        if len(contents_list) < 5:
            raise ValueError(f"File '{filename}' is not a valid n-puzzle file.")
        if not contents_list[1].isdigit() or int(contents_list[1]) < 3:
            raise ValueError(f"File '{filename}' is not a valid n-puzzle file.")
        size = int(contents_list[1])
        if len(contents_list) != size + 2:
            raise ValueError(f"File '{filename}' is not a valid n-puzzle file.")
        puzzle = []
        for line in contents_list[2:]:
            numbers = line.split()
            if numbers and numbers[-1].startswith('#'):
                numbers = numbers[:-1]
            if len(numbers) != size:
                raise ValueError(f"File '{filename}' is not a valid n-puzzle file.")
            puzzle += numbers
        puzzle_ints = [int(x) for x in puzzle]
        if set(puzzle_ints) != set(range(size * size)):
            raise ValueError(f"File '{filename}' is not a valid n-puzzle file.")
    except (OSError, ValueError) as e:
        print(f"{FAIL_MARK}")
        raise ValueError(f"Error: {e}")
    print(f"{PASS_MARK}")
    return size, puzzle_ints
