# N-Puzzle

A solver for the N-puzzle ("taquin") written in Python 3, using the A\* search
algorithm and two of its variants. Standard library only — no third-party
dependencies.

The project follows the 42 subject (`subject/en.subject.pdf`): it manages
arbitrary puzzle sizes, reads boards from a file or generates them randomly,
offers three admissible heuristics, and reports the four values the subject
demands at the end of every search.

---

**Contents** —
[Quick start](#quick-start) ·
[What the subject requires](#what-the-subject-requires) ·
[Input file format](#input-file-format) ·
[Options](#command-line-options-in-detail) ·
[Reading the output](#reading-the-output) ·
[Search algorithm](#the-search-algorithm) ·
[Heuristics](#the-heuristics-and-why-they-are-admissible) ·
[Data structures](#data-structures) ·
[Solvability](#solvability) ·
[Bonus](#bonus-features) ·
[Verifying a solution](#verifying-a-solution) ·
[Benchmarks](#benchmarks) ·
[Project layout](#project-layout)

---

## Quick start

Requires Python 3 (standard library only, nothing to install). A `Makefile`
with the usual rules is provided because the subject asks for one, but every
example below runs the solver directly:

```bash
python3 n_puzzle.py                     # default board file, default settings
python3 n_puzzle.py tests/3x3_solvable  # a specific board file
python3 n_puzzle.py -r 4 -hf linear -t  # random solvable 4x4, timed
python3 n_puzzle.py -h                  # full option list
```

Exit codes: `0` on success, `1` on any error (bad file, bad option, unsolvable
puzzle, unreachable goal, memory abort), `130` on Ctrl-C.

---

## What the subject requires

| Subject requirement | Where it is met |
|---|---|
| A\* search algorithm (or a variant) | `npuzzle/solver.py` — A\* with a lazy-deletion binary heap |
| Manage various puzzle sizes (3, 4, 5, 17 …) | No size is hard-coded; the only limit is memory, which is watched and reported |
| Manage random states, self-generated | `-r <size>`, see `npuzzle/generator.py` |
| Manage input files with the appendix format | positional `board` argument, see `npuzzle/parser.py` |
| Transition cost always 1 | `g_cost += 1` per expansion in `_expand_board` |
| At least 3 relevant heuristics, Manhattan mandatory | `-hf manhattan\|hamming\|linear`, see `npuzzle/heuristics.py` |
| **Complexity in time** — total states selected in the opened set | printed as *Time complexity (states selected)* |
| **Complexity in size** — max states in memory at once | printed as *Size complexity (max states in memory)* |
| **Number of moves** from initial to final state | printed as *Number of moves* |
| **Ordered sequence of states** making up the solution | printed board by board, `Initial:` then `Step 1:`, `Step 2:` … |
| Unsolvable puzzle: inform the user and exit | detected *before* the search starts, prints `Puzzle is NOT solvable ✗`, exits 1 |
| A Makefile with the usual rules | `Makefile` |
| Examples of varied sizes to run the program on | `tests/`, from 3x3 to 15x15: solvable, unsolvable, already-solved and malformed boards |
| Bonus: uniform-cost and greedy search | `-av uniform_cost`, `-av greedy` |

The program never raises an uncaught exception: bad files, bad options, an
unreachable goal, a memory blow-up and Ctrl-C are all caught in
`npuzzle/main.py` and turned into a message plus an exit status.

The three points the subject asks to be justified each have their own section
below: the [search algorithm](#the-search-algorithm) and which variant of A\*
it is, the [heuristics and their admissibility](#the-heuristics-and-why-they-are-admissible),
and the [choice of data structures](#data-structures) for the open and closed
sets.

---

## Input file format

Exactly the format described in the subject appendix:

```
# this is a comment
3
3 2 6 #another comment
1 4 0
8 7 5
```

Any `#` starts a comment running to the end of the line. The first non-comment
value is the size `N` (minimum 3), followed by `N` rows of `N` integers which
must be exactly `0 .. N*N-1`, each appearing once, `0` being the blank. Rows may
be aligned or not — any run of whitespace separates values. Anything else
(missing file, wrong row count, duplicate or out-of-range tiles, size below 3)
prints `Reading starting board from file "…" ✗` with the reason, and exits 1.

Sample boards from 3x3 to 15x15 — solvable, unsolvable and already-solved —
live in `tests/`. Boards can also be produced with the subject's generator:

```bash
python3 subject/npuzzle-gen.py -s 4 > my_board && python3 n_puzzle.py my_board
```

---

## Command line options in detail

```
python3 n_puzzle.py [board] [-h] [-r <size>] [-hf <heuristic>]
                    [-av <variant>] [-gs <goal_state>] [-t] [-as [<delay>]]
```

### `board` (positional, optional, default `board`)

Path to a puzzle file in the format above. Omitting it reads the file named
`board` in the current directory, which is committed to the repository so that
a bare `python3 n_puzzle.py` always has something to solve. Ignored when `-r`
is given: a randomly generated puzzle replaces any file.

### `-h`, `--help`

Prints the usage line, a description of every option, and exits. Provided by
`argparse`.

### `-r <size>` — random puzzle

Generates a random **solvable** puzzle of `<size> x <size>` instead of reading
a file. `<size>` must be an integer ≥ 3; anything smaller is rejected with
`Size must be at least 3 for a valid n-puzzle ✗`.

The board is shuffled and re-shuffled until it passes the solvability test
*against the goal state currently in use* — so `-r` composes correctly with
`-gs`, and roughly half of all permutations qualify, so this converges
immediately. Solvability is therefore guaranteed by construction, and no
separate solvability message is printed in this mode.

### `-hf <heuristic>` — heuristic function

Chooses `h(x)`. One of:

| Value | Function | Behavior |
|---|---|---|
| `manhattan` (default) | `manhattan_distance` | Sum of row + column offsets of every tile from its goal cell |
| `hamming` | `hamming_distance` | Count of misplaced tiles |
| `linear` | `linear_conflict` | Manhattan plus the linear-conflict correction |

All three are admissible; see
[the heuristics section](#the-heuristics-and-why-they-are-admissible) for how
each works and why it never overestimates. In practice `linear` explores the
fewest states and is the right choice for 4x4 and larger, `manhattan` is the
fastest per state and usually wins on 3x3, and `hamming` is the weakest —
mainly interesting to show how much heuristic strength matters (see
[Benchmarks](#benchmarks)).

Ignored when `-av uniform_cost` is used, since that variant pins `h` to 0. The
setup header then reports `Heuristic: None (uniform cost search)`.

### `-av <variant>` — algorithm variant

Chooses how `f(x)` is built from `g(x)` and `h(x)`, which is what turns the
same search loop into three different algorithms:

| Value | Scoring | Meaning |
|---|---|---|
| `a_star` (default) | `f = g + h` | A\*: balances the cost already paid against the estimate of what remains |
| `greedy` | `f = h` | Greedy best-first: ignores the path cost, always dives toward whatever *looks* closest to the goal |
| `uniform_cost` | `f = g`, with `h = 0` | Uniform-cost search: Dijkstra on a unit-cost graph, i.e. breadth-first in disguise |

The trade-off is the point of the bonus: greedy finds *a* solution very fast
but a much longer one, uniform-cost explores an enormous number of states, and
A\* sits between the two. [Benchmarks](#benchmarks) shows this on one board.

### `-gs <goal_state>` — goal configuration

Chooses the target board the search aims for:

| Value | Goal for a 3x3 |
|---|---|
| `snail` (default) | `1 2 3 / 8 _ 4 / 7 6 5` — the spiral the subject requires |
| `top_left` | `_ 1 2 / 3 4 5 / 6 7 8` — blank first, then tiles in reading order |
| `bottom_right` | `1 2 3 / 4 5 6 / 7 8 _` — reading order, blank last |

`snail` fills the board with `1 .. N*N-1` spiralling clockwise inward from the
top-left, and puts the blank in the cell the spiral would have filled last.

This matters more than it looks: **solvability is relative to the goal**. A
board that can reach the snail goal may be unreachable from `top_left`, and
vice versa. The solvability check and the random generator both take the
selected goal into account, so every mode stays consistent. The goal in use is
printed in the setup header, e.g. `Goal state (Snail):`.

### `-t` — timing

Adds `Search time` and `States selected per second` to the results. The clock
brackets the search only — reading the file, checking solvability and printing
the solution are all outside it, so the figure measures the algorithm rather
than the I/O. The rate is the time complexity divided by that duration, which
makes it easy to compare heuristics of different cost per state.

### `-as [<delay>]` — animated solution

Replays the solution in place instead of printing every board one under the
other: each frame overwrites the previous one, so the puzzle appears to solve
itself.

* `-as` alone uses the default delay of `0.50` seconds per board; `-as 0.1`
  sets it explicitly. A negative delay is rejected with
  `Animation delay cannot be negative ✗`.
* The animation only engages when standard output is a terminal. Redirect to
  a file or pipe the output and the normal full listing is printed instead, so
  the sequence stays complete and machine-readable (this is what lets the
  checker validate an animated run).

### Examples

Options are independent and can be freely combined:

```bash
python3 n_puzzle.py tests/4x4_solvable -hf linear      # file board, stronger heuristic
python3 n_puzzle.py -r 5 -gs top_left                  # random 5x5, different goal
python3 n_puzzle.py tests/3x3_solvable_hard -av greedy # greedy instead of A*
python3 n_puzzle.py -r 4 -hf linear -t -as 0.2         # timed, animated replay
```

---

## Reading the output

A run prints status lines, a setup header, and the solution:

```
Reading starting board from file "tests/3x3_solvable" ✓
Puzzle is solvable ✓

*********************** PUZZLE SETUP ***********************
Puzzle size:   3 x 3

Initial state:
5 7 8
2 6 4
_ 3 1

Goal state (Snail):
1 2 3
8 _ 4
7 6 5

Variant:       A Star
Heuristic:     Linear Conflict

********************* PUZZLE SOLUTION **********************
Solution found ✓
Solution sequence (initial -> goal):
Initial:                        (then Step 1:, Step 2: ... Step 28:,
5 7 8                            each drawn the same way)
2 6 4
_ 3 1

Number of moves:                        28
Time complexity (states selected):      1,267
Size complexity (max states in memory): 2,094
```

The blank tile is stored internally as `0` but drawn as `_`, so it reads as an
empty slot rather than as another tile. Cells are right-aligned to the width of
the largest tile, so columns line up at any size.

The last four lines are the values the subject requires:

| Line | Meaning |
|---|---|
| `Solution sequence` | The ordered sequence of states, `Initial:` followed by `Step 1:` … `Step N:`, each drawn as an N×N grid. Consecutive boards always differ by exactly one legal slide. |
| `Number of moves` | Length of that sequence minus the initial state, i.e. the number of moves the search says are needed. |
| `Time complexity (states selected)` | Total number of states ever selected out of the open set and expanded — the size of the closed set at the end. |
| `Size complexity (max states in memory)` | Peak of `open set + closed set` observed at any point during the search. |

While a long search runs, a progress line refreshed every 25 000 explored
states shows how many states have been expanded and how much memory the process
holds: `Explored 250,000 │ Memory 1,024/7,680 MiB (13.3%)`.

**Unsolvable puzzles** are detected from the inversion parity before the search
even starts, so the program answers instantly — `Puzzle is NOT solvable ✗` —
instead of exhausting the state space, and exits 1. **Already-solved boards**
are answered directly, with 0 moves, 0 states selected and a size complexity
of 1.

---

## The search algorithm

`npuzzle/solver.py` implements **A\* with a binary heap and lazy deletion**.
The loop is the one from the subject appendix, with two deliberate departures
explained below.

```
push the start board onto the open set, scored by the variant
while the open set is not empty:
    pop the board with the lowest f
    add it to the closed set                  # "expanded, never revisit"
    for each of the (up to 4) legal slides of the blank:
        if the neighbor is already closed: skip it
        record its parent
        if it is the goal: stop
        score it and push it
if the open set empties without reaching the goal: no solution
```

**Moves.** The blank is what actually moves. From its `(y, x)` coordinates the
four candidate slides are bounds-checked so the blank cannot wrap around a row
edge or fall off the board. Each legal slide copies the board and swaps the
blank with its neighbor. Each move costs exactly 1, as the subject requires,
which is why `g` is simply the parent's `g + 1`.

**Early goal test.** The goal is detected when it is *generated* rather than
when it is popped. On a unit-cost graph with an admissible heuristic this
finds the goal one heap round-trip earlier at no practical cost, and it keeps
the closed set — the reported time complexity — meaningful.

**Lazy deletion instead of a decrease-key.** A better route to a board already
sitting in the open set is pushed as a *new* heap entry rather than the old one
being located and updated. The stale copy is simply skipped when it eventually
surfaces, because the board is by then in the closed set. This is the standard
trade: `O(log n)` pushes and no need for an index from board to heap position,
at the price of a slightly larger heap.

**Path reconstruction.** `came_from` maps every board to the board it was
reached from, with the start board mapping to `None`. From the goal, following
those links backwards and reversing the list yields the ordered sequence of
states printed as the solution — this is what the subject calls the solution
"according to the search".

**No solution.** If the open set empties without the goal being generated, the
search reports `No solution found ✗` and exits 1. With the parity check done
up front this is unreachable for a well-formed board, and exists as a safety
net.

**Memory guard.** Every 25 000 expansions the process compares its peak
resident memory against what the machine could still give it (`MemAvailable`
from `/proc/meminfo`). At 80 % it aborts cleanly with a message naming the
figures, rather than letting the kernel's OOM killer take the process down.
(This check is Linux-only.)

---

## The heuristics and why they are admissible

A heuristic is **admissible** when it never overestimates the true remaining
cost. That is what guarantees A\* is searching for a least-cost path rather
than being misled into settling for a worse one. All three heuristics here
ignore the blank, which is correct because the blank is not a tile that has to
reach a destination — it is the mechanism by which tiles move.

### `hamming` — misplaced tiles

Counts the tiles that are not on their goal cell.

*Admissible:* every misplaced tile must move at least once to reach its goal,
and one move relocates exactly one tile. So the number of misplaced tiles is a
lower bound on the number of moves. Weak, but never an overestimate.

### `manhattan` — sum of grid distances (mandatory)

For each tile, `|Δrow| + |Δcolumn|` between where it is and where it belongs;
summed over all tiles.

*Admissible:* a single move changes one tile's position by exactly one cell,
either horizontally or vertically, so it can reduce the total by at most 1. A
tile at Manhattan distance `d` therefore needs at least `d` moves, and the sum
is a lower bound on the total. It also ignores the fact that tiles get in each
other's way, which is exactly why it under-counts rather than over-counts.

### `linear` — Manhattan plus linear conflicts

Manhattan distance, plus 2 for every unavoidable detour caused by a *linear
conflict*.

Two tiles are in linear conflict when they are both already on their goal row
(or goal column) but in reversed order relative to each other. They cannot
simply slide past one another: one of them has to step off the line and come
back, which is 2 moves that Manhattan does not count anywhere.

For each row and each column, the implementation lists the goal positions of
the tiles that already belong to that line, in board order. The tiles that can
stay put must be in increasing order, so the minimum number that must leave is
the length minus the *longest increasing subsequence*, computed by patience
sorting (`bisect` over a `tails` array, `O(k log k)`). Two moves are added per
tile that must leave.

*Admissible:* the added moves are ones Manhattan provably does not count — a
tile leaving and re-entering its line does not contribute to the row/column
offsets Manhattan already charged for. Counting the minimum number of removals
per line, and counting rows and columns separately, ensures no move is counted
twice. The result therefore remains a lower bound while strictly dominating
Manhattan (`linear ≥ manhattan` always), which is what makes A\* expand far
fewer states with it.

---

## Data structures

### Open set — a binary heap (priority queue)

`heapq` over a list of tuples:

```python
(f_cost, h_cost, g_cost, insertion_counter, board)
```

*Why:* the search does exactly one thing to the open set on every iteration —
retrieve the lowest-cost element. A binary heap gives that in `O(log n)`, with
`O(log n)` insertion, which is the operation profile the algorithm actually
has. A plain list would make every iteration an `O(n)` scan over a container
that routinely holds millions of entries.

*Why the tuple is ordered that way:* Python compares tuples element by element.
Ranking by `f` first is the algorithm; falling back to `h` then `g` breaks
ties toward states estimated to be closer to the goal, which measurably reduces
expansions. The monotonically increasing counter sits last so that a full tie
is resolved by insertion order — and, crucially, so comparison **never reaches
the board itself**, which would be both meaningless and slow.

### Closed set — a hash set

A Python `set` of boards as tuples.

*Why:* the only question ever asked of the closed set is "have I already
expanded this board?", asked once per generated neighbor — millions of times
in a large search. A hash set answers in `O(1)` average time. A list would make
each of those checks `O(n)` and turn the search quadratic. Boards are converted
from `list` to `tuple` because a tuple is hashable and immutable, so it can
serve both as a set member and as a dictionary key.

### `came_from` — a dictionary

Maps each board (tuple) to its parent board (tuple), the start mapping to
`None`. `O(1)` insertion and lookup, and it stores the search tree implicitly:
one parent link per state is all that is needed to rebuild the full path at the
end, instead of carrying a copy of the path in every node.

---

## Solvability

`npuzzle/solvability.py` decides reachability by **inversion parity**, before
any search happens, so an unsolvable puzzle costs microseconds rather than an
exhausted state space.

Each tile is ranked by the index it occupies *in the goal*, so the goal itself
has zero inversions by construction and the rule works for any goal layout,
not just the classic reading order. An inversion is a pair of tiles out of that
goal order (the blank excluded). Then:

* **Odd board size** — a legal move never changes inversion parity, so the
  puzzle is solvable exactly when its inversion count is even.
* **Even board size** — a horizontal move keeps parity, a vertical move flips
  it, so the blank's vertical travel has to be folded in: the puzzle is
  solvable when `inversions + |blank row − goal blank row|` is even.

This is also what the random generator (`-r`) calls to reject unsolvable
shuffles, which is why generated puzzles are always solvable against whichever
goal `-gs` selected.

---

## Bonus features

The subject's bonus is the two extra search strategies; the rest are additions
of this implementation.

* **Uniform-cost search** and **greedy search** (`-av`) — described under
  [`-av`](#-av-variant--algorithm-variant). Greedy in particular is the "read
  up on why the solution may be different" the subject asks about: it has no
  lower-bound guarantee at all, so it trades move count for speed.
* **Three goal states** (`-gs`) — including the demonstration that solvability
  is a property of the *(board, goal)* pair, not of the board alone.
* **Timing report** (`-t`) — search duration and states selected per second.
* **Animated replay** (`-as`) — the solution played back in place, with the
  full listing preserved whenever output is not a terminal.
* **Live progress and a memory guard** — long searches show explored states and
  memory usage, and abort cleanly at 80 % of available memory rather than being
  OOM-killed.
* **Independent solution checker** (`tests/checker.py`) — validates a run from
  its printed output alone, trusting nothing about the search. See below.

---

## Verifying a solution

A solution is only worth anything if it is genuinely valid, so the sequence can
be verified independently of the program that produced it. `tests/checker.py`
re-reads the solver's *printed output* — not its internal state — and confirms
it:

```bash
python3 n_puzzle.py tests/3x3_solvable > output && python3 tests/checker.py output
```
```
Boards are valid permutations             ✓
First board matches the initial state     ✓
Last board matches the goal state         ✓
Every transition is a single legal move   ✓
Move count matches the sequence           ✓

Solution is valid ✓
```

Because nothing but the printed text is trusted, a passing check proves the
program really produced a legal sequence of single slides from the given
initial state to the declared goal.

---

## Benchmarks

Measured with `-t` on this machine; absolute times vary, the ratios are the
point.

**Heuristics** — same board (`tests/3x3_solvable_hard`), same variant (A\*):

| Heuristic | Moves | States selected | Max in memory | Time |
|---|---:|---:|---:|---:|
| `hamming` | 29 | 75,546 | 116,076 | 0.618 s |
| `manhattan` | 29 | 4,276 | 6,876 | 0.035 s |
| `linear` | 29 | 1,997 | 3,178 | 0.048 s |

`linear` visits half the states of `manhattan` but costs more per state, so on
a 3x3 it does not pay off yet; on 4x4 and above it does, decisively.

**Variants** — same board, `manhattan`. Greedy gets there with 12× fewer states
but takes 69 % more moves; uniform-cost matches A\*'s move count while
expanding 42× more states. That contrast is the whole point of the bonus.

| Variant | Moves | States selected | Max in memory | Time |
|---|---:|---:|---:|---:|
| `a_star` | 29 | 4,276 | 6,876 | 0.034 s |
| `greedy` | 49 | 358 | 589 | 0.003 s |
| `uniform_cost` | 29 | 178,365 | 219,492 | 2.136 s |

**Scale** — A\* with `linear`. Large boards are best attacked with greedy,
which handles sizes A\* cannot fit in memory: `tests/15x15_solvable` is solved
in 122 moves and about 13 seconds with `-av greedy -hf linear`.

| Board | Moves | States selected | Time |
|---|---:|---:|---:|
| `tests/4x4_solvable` | 39 | 2,767 | 0.12 s |
| `tests/4x4_solvable_hard` | 51 | 1,026,834 | 51.4 s |

---

## Project layout

```
n_puzzle.py              entry point: forwards to the npuzzle package
board                    default puzzle file, used when no board is given
Makefile                 usual rules (help, install, run, debug, test, clean)
npuzzle/
    main.py              builds the puzzle, drives the run, maps errors to exit codes
    parser.py            command line definition and puzzle file parsing
    generator.py         goal states (snail / top_left / bottom_right) and -r generation
    solvability.py       inversion-parity reachability test
    heuristics.py        hamming, manhattan, linear conflict
    solver.py            the A* search loop and its variants
    memory.py            memory budget watchdog
    prints.py            setup header, board rendering, solution and animation
    constants.py         the ✓ / ✗ status marks
    exceptions.py        GoalReached, NoSolutionFound, MemoryLimitExceeded
subject/
    en.subject.pdf       the project subject
    npuzzle-gen.py       puzzle generator supplied with the subject
tests/
    checker.py           validates a run from its printed output
    test_solution.py     earlier checker, superseded by checker.py
    <boards>             sample boards, 3x3 to 15x15, plus the puzzles*/ corpora
```
