import sys
from solvability import check_puzzle_solvability
from parser import parse_arguments, read_puzzle_file, PASS_MARK, FAIL_MARK


def main():
    args = parse_arguments()
    try:
        size, board = read_puzzle_file(args.board)
        print(f"Puzzle size: {size}")
        print(f"Puzzle board: {board}")
        if not check_puzzle_solvability(size, board):
            print(f"Puzzle is NOT solvable {FAIL_MARK} ")
            sys.exit(0)
        print(f"Puzzle is solvable {PASS_MARK} ")
    except ValueError as error:
        print(f"{error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
