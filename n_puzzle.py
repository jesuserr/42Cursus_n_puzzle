import sys
from solvability import check_puzzle_solvability
from parser import parse_arguments, read_puzzle_file, PASS_MARK, FAIL_MARK
from generator import generate_random_puzzle


def main():
    args = parse_arguments()
    try:
        if args.random is None:
            size, board = read_puzzle_file(args.board)
            if not check_puzzle_solvability(size, board):
                print(f"Puzzle is NOT solvable {FAIL_MARK} ")
                sys.exit(1)
            print(f"Puzzle is solvable {PASS_MARK} ")
        else:
            size, board = generate_random_puzzle(args.random)
        print(f"Puzzle size: {size}")
        print(f"Puzzle board: {board}")        
    except ValueError as error:
        print(f"{error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
