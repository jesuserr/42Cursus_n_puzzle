#!/usr/bin/env python3
# Checks the output of a solver run: re-reads the printed sequence of boards
# and confirms every step is a single legal slide leading from the initial
# state to the goal, and that the reported move count matches. Nothing of the
# search is trusted, only what n_puzzle.py printed, so `python3 n_puzzle.py
# board > output && python3 tests/checker.py output` verifies a run end to end.
import re
import sys
from pathlib import Path
# The checker lives in tests/, which is what Python puts on the import path
# when it is run as a script, so the repository root is added explicitly to
# reach the npuzzle package the marks and the banner width come from.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from npuzzle.constants import PASS_MARK, FAIL_MARK       # noqa: E402
from npuzzle.prints import BANNER_WIDTH, BLANK_CELL      # noqa: E402
# Output file read when the command line names none, as the solver defaults
# to the board file 'board'.
DEFAULT_OUTPUT = 'output'
# A printed board row: tiles are digits and the blank is BLANK_CELL.
ROW = rf"[\d{BLANK_CELL}]+(\s+[\d{BLANK_CELL}]+)*"
# Line the solver prints just before the initial -> goal sequence of boards.
SEQUENCE_HEADER = "Solution sequence (initial -> goal):"
# Width the check labels are padded to, so the ✓/✗ marks form a column.
LABEL_WIDTH = 42
# What the solver prints instead of a solution when it stops before reaching
# the goal. Such a run leaves no sequence to check, so the checker names the
# reason rather than calling the output malformed.
ABORT_MESSAGES = ("Puzzle is NOT solvable", "No solution found",
                  "Puzzle needs too much memory")


# Read the output to be checked, printing the same status line the solver
# prints for a board file. Raises ValueError on any problem, OSError included,
# so main only ever catches ValueError.
def read_output_file(filename):
    print(f'Reading solver output from file "{filename}" ', end="")
    try:
        with open(filename) as f:
            text = f.read()
        if not text:
            raise ValueError(f"File '{filename}' is empty.")
    except (OSError, ValueError) as e:
        print(f"{FAIL_MARK}")
        raise ValueError(f"Error: {e}")
    print(f"{PASS_MARK}")
    return text


# Turn one printed row into ints, mapping the blank back to the 0 the solver
# stores internally.
def _parse_row(line):
    return [0 if cell == BLANK_CELL else int(cell) for cell in line.split()]


# Read the size x size grid printed right after `label`, returned as a flat
# list. Cells are right-aligned to a common width, so each line is stripped
# before splitting. Anything that is not a row of tiles is skipped ahead of
# the grid and ends it once the grid has started, which lets the goal label
# carry the goal type in brackets.
def _read_grid(text, label, size):
    parts = text.split(label, 1)
    if len(parts) < 2:
        raise ValueError(f"Error: output is missing '{label}'.")
    rows = []
    for line in parts[1].splitlines():
        line = line.strip()
        if re.fullmatch(ROW, line):
            rows.append(_parse_row(line))
            if len(rows) == size:
                return [cell for row in rows for cell in row]
        elif rows:
            break
    raise ValueError(f"Error: '{label}' is not followed by a "
                     f"{size}x{size} grid.")


# Parse a solver output, returning the declared size, the initial and goal
# states as flat lists, the reported move count and the ordered boards of the
# solution sequence. The boards live between SEQUENCE_HEADER and the trailing
# statistics: every line made only of tiles is a board row, and rows are
# grouped into boards of `size` rows each.
def parse_output(text):
    for message in ABORT_MESSAGES:
        if message in text:
            raise ValueError(f'Error: nothing to check, the run ended with '
                             f'"{message}".')
    size_match = re.search(r"Puzzle size:\s*(\d+)\s*x\s*(\d+)", text)
    moves_match = re.search(r"Number of moves:\s*([\d,]+)", text)
    if not (size_match and moves_match):
        raise ValueError("Error: output is missing the puzzle size or the "
                         "move count.")
    size = int(size_match.group(1))
    if int(size_match.group(2)) != size:
        raise ValueError("Error: puzzle is not square.")
    initial = _read_grid(text, "Initial state:", size)
    goal = _read_grid(text, "Goal state", size)
    reported_moves = int(moves_match.group(1).replace(",", ""))
    if SEQUENCE_HEADER not in text:
        raise ValueError(f"Error: output is missing '{SEQUENCE_HEADER}'.")
    body = text.split(SEQUENCE_HEADER, 1)[1].split("Number of moves:", 1)[0]
    rows = [_parse_row(line.strip()) for line in body.splitlines()
            if re.fullmatch(ROW, line.strip())]
    if not rows:
        raise ValueError("Error: no boards found in the solution sequence.")
    if len(rows) % size != 0:
        raise ValueError(f"Error: row count {len(rows)} is not a multiple "
                         f"of size {size}.")
    boards = [[cell for row in rows[i:i + size] for cell in row]
              for i in range(0, len(rows), size)]
    return size, initial, goal, reported_moves, boards


# A board is valid when it is exactly a permutation of 0..size*size-1, which
# also rejects a board of the wrong length.
def is_valid_board(board, size):
    return sorted(board) == list(range(size * size))


# Two boards are one legal move apart when they are identical except that the
# blank (0) has swapped places with an orthogonally adjacent tile: exactly two
# cells differ, one of them holds the blank in each board, their contents are
# exchanged, and they sit in the same row one column apart or in the same
# column one row apart.
def is_single_move(prev, curr, size):
    diff = [i for i in range(len(prev)) if prev[i] != curr[i]]
    if len(diff) != 2:
        return False
    a, b = diff
    if not ((prev[a] == 0 and curr[b] == 0)
            or (prev[b] == 0 and curr[a] == 0)):
        return False
    if prev[a] != curr[b] or prev[b] != curr[a]:
        return False
    ra, ca = divmod(a, size)
    rb, cb = divmod(b, size)
    return (ra == rb and abs(ca - cb) == 1) or (ca == cb and abs(ra - rb) == 1)


# Run every check on a parsed output and return them in printing order as
# (label, errors) pairs. errors is empty when the check passed and holds one
# message per problem otherwise, so the caller can mark each check and detail
# only the ones that failed.
def run_checks(size, initial, goal, reported_moves, boards):
    invalid = [f"board {i} is not a permutation of 0..{size * size - 1}"
               for i, board in enumerate(boards)
               if not is_valid_board(board, size)]
    illegal = [f"step {i - 1} -> {i} is not a single legal move"
               for i in range(1, len(boards))
               if not is_single_move(boards[i - 1], boards[i], size)]
    moves = len(boards) - 1
    return [
        ("Boards are valid permutations", invalid),
        ("First board matches the initial state",
         [] if boards[0] == initial else ["first board is not the declared "
                                          "initial state"]),
        ("Last board matches the goal state",
         [] if boards[-1] == goal else ["last board is not the declared "
                                        "goal state"]),
        ("Every transition is a single legal move", illegal),
        ("Move count matches the sequence",
         [] if moves == reported_moves else [f"{reported_moves:,} moves "
                                             f"reported, sequence has "
                                             f"{moves:,}"]),
    ]


# Print a header summarizing what is being checked: the output file it was
# read from, the puzzle size and the number of moves the solver claimed, so
# the verdict below is read against the run it came from.
def print_check_header(filename, size, reported_moves):
    print("\n" + " SOLUTION CHECK ".center(BANNER_WIDTH, "*"))
    print(f"Checked file:  {filename}")
    print(f"Puzzle size:   {size} x {size}")
    print(f"Moves claimed: {reported_moves:,}\n")


# Print one line per check, its label padded so the ✓/✗ marks line up, with
# every failure listed under the check that found it, and close on whether
# the printed sequence solves the puzzle.
def print_check_results(checks):
    for label, errors in checks:
        print(f"{label:<{LABEL_WIDTH}}{FAIL_MARK if errors else PASS_MARK}")
        for error in errors:
            print(f"  - {error}")
    if any(errors for _, errors in checks):
        print(f"\nSolution is NOT valid {FAIL_MARK}")
    else:
        print(f"\nSolution is valid {PASS_MARK}")


# Entry point: read the output file named on the command line, defaulting to
# DEFAULT_OUTPUT, parse the sequence out of it and report every check. This is
# the single place errors become an exit status: an unreadable or malformed
# output and a failed check all exit 1, while Ctrl-C exits 130, the shell
# convention for death by SIGINT.
def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT
    try:
        text = read_output_file(filename)
        size, initial, goal, reported_moves, boards = parse_output(text)
        print_check_header(filename, size, reported_moves)
        checks = run_checks(size, initial, goal, reported_moves, boards)
        print_check_results(checks)
        if any(errors for _, errors in checks):
            sys.exit(1)
    except ValueError as error:
        print(f"{error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
