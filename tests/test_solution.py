#!/usr/bin/env python3

import re
import sys


# Read the size x size grid printed right after `label`, returned as a flat
# list. Cells are right-aligned to a common width, so each line is stripped
# before splitting. Blank lines ahead of the grid are skipped; anything that
# is not a row of integers once the grid has started ends it.
def read_grid(text, label, size):
    parts = text.split(label, 1)
    if len(parts) < 2:
        raise ValueError(f"output is missing '{label}'")
    rows = []
    for line in parts[1].splitlines():
        line = line.strip()
        if re.fullmatch(r"\d+(\s+\d+)*", line):
            rows.append([int(n) for n in line.split()])
            if len(rows) == size:
                return [cell for row in rows for cell in row]
        elif rows:
            break
    raise ValueError(f"'{label}' is not followed by a {size}x{size} grid")


# Parse an n_puzzle output file, returning the declared size, the initial and
# goal states (as flat lists) and the ordered list of boards that make up the
# solution sequence (each board a flat list of size * size ints).
def parse_output(text):
    size_match = re.search(r"Puzzle size:\s*(\d+)\s*x\s*(\d+)", text)
    moves_match = re.search(r"Number of moves:\s*(\d+)", text)
    if not (size_match and moves_match):
        raise ValueError("output is missing puzzle size or move count")

    size = int(size_match.group(1))
    if int(size_match.group(2)) != size:
        raise ValueError("puzzle is not square")
    initial = read_grid(text, "Initial state:", size)
    goal = read_grid(text, "Goal state:", size)
    reported_moves = int(moves_match.group(1))

    # The boards live between the "Solution sequence" header and the trailing
    # statistics. Every line made only of integers is a board row; blank lines
    # separate boards. Group rows into boards of size rows each.
    header = "Solution sequence (initial -> goal):"
    if header not in text:
        raise ValueError(f"output is missing '{header}'")
    body = text.split(header, 1)[1]
    body = body.split("Number of moves:", 1)[0]
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        if not re.fullmatch(r"(\d+\s*)+", line):
            continue
        rows.append([int(n) for n in line.split()])

    if len(rows) % size != 0:
        raise ValueError(f"row count {len(rows)} is not a multiple "
                         f"of size {size}")
    boards = []
    for i in range(0, len(rows), size):
        board = [cell for row in rows[i:i + size] for cell in row]
        boards.append(board)

    return size, initial, goal, reported_moves, boards


# A board is valid when it is exactly a permutation of 0..size*size-1.
def is_valid_board(board, size):
    return sorted(board) == list(range(size * size))


# Two boards are one legal move apart when they are identical except that the
# blank (0) has swapped places with an orthogonally adjacent tile.
def is_single_move(prev, curr, size):
    diff = [i for i in range(len(prev)) if prev[i] != curr[i]]
    if len(diff) != 2:
        return False
    a, b = diff
    # One of the two changed cells must be the blank in each board, and the two
    # cells must be adjacent (same row & adjacent columns, or same column &
    # adjacent rows). The swap must move the blank between the two positions.
    if not ((prev[a] == 0 and curr[b] == 0)
            or (prev[b] == 0 and curr[a] == 0)):
        return False
    if prev[a] != curr[b] or prev[b] != curr[a]:
        return False
    ra, ca = divmod(a, size)
    rb, cb = divmod(b, size)
    return (ra == rb and abs(ca - cb) == 1) or (ca == cb and abs(ra - rb) == 1)


def verify(text):
    size, initial, goal, reported_moves, boards = parse_output(text)
    errors = []

    if not boards:
        errors.append("no boards found in solution sequence")
        return errors

    for i, board in enumerate(boards):
        if len(board) != size * size:
            errors.append(f"board {i} has {len(board)} tiles, "
                          f"expected {size * size}")
        elif not is_valid_board(board, size):
            errors.append(f"board {i} is not a valid permutation "
                          f"of 0..{size * size - 1}")

    if boards[0] != initial:
        errors.append("first board does not match the declared initial state")
    if boards[-1] != goal:
        errors.append("last board does not match the declared goal state")

    for i in range(1, len(boards)):
        if not is_single_move(boards[i - 1], boards[i], size):
            errors.append(f"transition {i - 1} -> {i} is not a single "
                          f"legal move")

    actual_moves = len(boards) - 1
    if actual_moves != reported_moves:
        errors.append(f"reported {reported_moves} moves but sequence "
                      f"has {actual_moves}")

    return errors


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "output"
    try:
        with open(path) as f:
            text = f.read()
    except OSError as e:
        print(f"Cannot read '{path}': {e}")
        sys.exit(1)

    try:
        errors = verify(text)
    except ValueError as e:
        print(f"Malformed output: {e}")
        sys.exit(1)

    if errors:
        print("INVALID - the solution does not solve the puzzle:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    print("VALID - the sequence solves the puzzle with legal moves.")


if __name__ == "__main__":
    main()
