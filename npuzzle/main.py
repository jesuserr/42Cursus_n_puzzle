import sys
from npuzzle.solvability import check_puzzle_solvability
from npuzzle.parser import parse_arguments, read_puzzle_file
from npuzzle.constants import PASS_MARK, FAIL_MARK
from npuzzle.generator import generate_random_puzzle, build_goal_state
from npuzzle.heuristics import (hamming_distance, manhattan_distance,
                                linear_conflict)
from npuzzle.solver import solve_puzzle
from npuzzle.exceptions import MemoryLimitExceeded, NoSolutionFound
from npuzzle.prints import print_initial_state, print_solution


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


# Entry point: build the puzzle from the command line, print the setup header
# and hand it to the search. A board already on its goal is answered directly,
# since solve_puzzle only reports a goal it reaches through a move. This is the
# single place errors become an exit status: a bad file or option, an
# unreachable goal and the memory abort all print their own message and exit 1,
# while Ctrl-C exits 130, the shell convention for death by SIGINT.
def main():
    args = parse_arguments()
    try:
        size, board, goal_state, heuristic = setup_puzzle(args)
        print_initial_state(size, board, goal_state, heuristic, args.variant,
                            args.goal_state)
        if board == goal_state:
            print_solution([board], size, 0, 1, None, None)
            sys.exit(0)
        solve_puzzle(size, board, goal_state, heuristic, args.variant,
                     args.timing, args.animation)
    except (ValueError, NoSolutionFound, MemoryLimitExceeded) as error:
        print(f"{error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
