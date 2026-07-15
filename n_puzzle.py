import sys
from solvability import check_puzzle_solvability
from parser import parse_arguments, read_puzzle_file, PASS_MARK, FAIL_MARK
from generator import generate_random_puzzle, build_snail_goal
from heuristics import hamming_distance, manhattan_distance
from solver import puzzle_solver


def setup_puzzle(args):
    if args.random is None:
        size, board = read_puzzle_file(args.board)
        goal_state = build_snail_goal(size)
        if not check_puzzle_solvability(size, board, goal_state):
            print(f"Puzzle is NOT solvable {FAIL_MARK} ")
            sys.exit(1)
        print(f"Puzzle is solvable {PASS_MARK} ")
    else:
        size, board, goal_state = generate_random_puzzle(args.random)
    if args.heuristic == 'hamming':
        heuristic = hamming_distance
    elif args.heuristic == 'manhattan':
        heuristic = manhattan_distance
    return size, board, goal_state, heuristic


def main():
    args = parse_arguments()
    try:
        size, board, goal_state, heuristic = setup_puzzle(args)
        puzzle_solver(size, board, goal_state, heuristic)
    except ValueError as error:
        print(f"{error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
