import sys
from solvability import check_puzzle_solvability
from parser import parse_arguments, read_puzzle_file
from constants import PASS_MARK, FAIL_MARK
from generator import generate_random_puzzle, build_goal_state
from heuristics import hamming_distance, manhattan_distance, linear_conflict
from solver import solve_puzzle
from exceptions import MemoryLimitExceeded, NoSolutionFound
from prints import print_initial_state, print_solution


# Build the initial board/goal_state from a file or -r random generation,
# checking solvability for the file case (generated puzzles are always
# solvable by construction), then resolve the -hf choice to its heuristic
# function. Returns (size, board, goal_state, heuristic).
def setup_puzzle(args):
    if args.random is None:
        size, board = read_puzzle_file(args.board)
        goal_state = build_goal_state(size, args.goal_state)
        if not check_puzzle_solvability(size, board, goal_state):
            print(f"Puzzle is NOT solvable {FAIL_MARK} ")
            sys.exit(1)
        print(f"Puzzle is solvable {PASS_MARK} ")
    else:
        goal_state = build_goal_state(args.random, args.goal_state)
        size, board = generate_random_puzzle(args.random, goal_state)
    if args.heuristic == 'hamming':
        heuristic = hamming_distance
    elif args.heuristic == 'manhattan':
        heuristic = manhattan_distance
    elif args.heuristic == 'linear':
        heuristic = linear_conflict
    return size, board, goal_state, heuristic


def main():
    args = parse_arguments()
    try:
        size, board, goal_state, heuristic = setup_puzzle(args)
        print_initial_state(size, board, goal_state, heuristic, args.variant)
        if board == goal_state:
            print_solution([board], size, 0, 1)
            sys.exit(0)
        solve_puzzle(size, board, goal_state, heuristic, args.variant)
    except (ValueError, NoSolutionFound, MemoryLimitExceeded) as error:
        print(f"{error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
