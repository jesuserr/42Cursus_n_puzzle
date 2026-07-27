import argparse
import sys
from constants import PASS_MARK, FAIL_MARK
MIN_SIZE = 3                                # 3x3 smallest legal n-puzzle
HEADER_LINES = 2                            # comment line + size line
FILE_MIN_LINES = HEADER_LINES + MIN_SIZE    # header + 3 rows


def parse_arguments():
    arg_parser = argparse.ArgumentParser(
        usage="python3 n-puzzle.py [board] [-h] [-r size] [-hf heuristic]",
        description="Solves N-puzzle using A* search algorithm:\n"
                    "- with no arguments reads puzzle from default file\n"
                    "  'board' and applies default Manhattan distance\n"
                    "  heuristic using A* search variant\n"
                    "- with -r <size> generates a random solvable puzzle\n"
                    "  instead, ignoring any board file argument\n"
                    "- with -hf <heuristic> uses the specified heuristic\n"
                    "  function instead of the default Manhattan distance\n"
                    "  heuristic function\n"
                    "- with -av <variant> uses the specified algorithm\n"
                    "  variant instead of the default A* search variant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    arg_parser.add_argument('board', nargs='?', default='board')
    arg_parser.add_argument('-r', type=int, metavar=' <size>', dest='random',
                            help='generate random solvable puzzle of <size>')
    arg_parser.add_argument('-hf',
                            choices=['manhattan', 'hamming', 'linear'],
                            metavar='<heuristic>', dest='heuristic',
                            default='manhattan',
                            help="use specified <heuristic> function: "
                                 "'manhattan', 'hamming' or 'linear'")
    arg_parser.add_argument('-av',
                            choices=['a_star', 'greedy', 'uniform_cost'],
                            metavar='<variant>', dest='variant',
                            default='a_star',
                            help="use specified <variant> of the algorithm: "
                                 "'a_star', 'greedy' or 'uniform_cost'")
    args = arg_parser.parse_args()
    if args.random is not None and args.random < MIN_SIZE:
        print(f"Size must be at least {MIN_SIZE} for a valid n-puzzle "
              f"{FAIL_MARK}")
        sys.exit(1)
    return args


# Parse an n-puzzle file: line 0 is a comment, line 1 is the size,
# followed by `size` rows of `size` space-separated integers covering
# 0..size*size-1 exactly once. On a row, everything from the first '#' to the
# end of the line is dropped as a comment.
# Returns (size, flat list of ints). Raises ValueError on any problem, format
# errors and OSError alike, so callers only ever catch ValueError.
def read_puzzle_file(filename):
    print(f'Reading starting board from file "{filename}" ', end="")
    try:
        with open(filename) as f:
            contents_str = f.read()
        if not contents_str:
            raise ValueError(f"File '{filename}' is empty.")
        contents_list = contents_str.strip().splitlines()
        if len(contents_list) < FILE_MIN_LINES:
            raise ValueError(f"File '{filename}' not valid n-puzzle file.")
        if not contents_list[1].isdigit() or int(contents_list[1]) < MIN_SIZE:
            raise ValueError(f"File '{filename}' not valid n-puzzle file.")
        size = int(contents_list[1])
        if len(contents_list) != size + HEADER_LINES:
            raise ValueError(f"File '{filename}' not valid n-puzzle file.")
        puzzle = []
        for line in contents_list[HEADER_LINES:]:
            numbers = line.split('#', 1)[0].split()
            if len(numbers) != size:
                raise ValueError(f"File '{filename}' not valid n-puzzle file.")
            puzzle += numbers
        puzzle_ints = [int(x) for x in puzzle]
        if set(puzzle_ints) != set(range(size * size)):
            raise ValueError(f"File '{filename}' not valid n-puzzle file.")
    except (OSError, ValueError) as e:
        print(f"{FAIL_MARK}")
        raise ValueError(f"Error: {e}")
    print(f"{PASS_MARK}")
    return size, puzzle_ints
