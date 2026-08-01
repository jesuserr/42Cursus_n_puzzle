import bisect


# Counts tiles that are out of place (blank excluded).
# `size` is unused; kept so all three heuristics share one call signature.
def hamming_distance(state, goal_state, size):
    paired_tiles = zip(state, goal_state)
    misplaced_tiles_count = 0
    for s, g in paired_tiles:
        if s != g and s != 0:
            misplaced_tiles_count += 1
    return misplaced_tiles_count


# Sums each tile's grid distance (row+column offset) from its goal
# position (blank excluded). Needs `size` to convert flat indices
# into 2D row/column coordinates.
def manhattan_distance(state, goal_state, size):
    manhattan_distance_sum = 0
    for i in range(len(state)):
        if state[i] != 0:
            state_row, state_column = divmod(i, size)
            goal_index = goal_state.index(state[i])
            goal_row, goal_column = divmod(goal_index, size)
            manhattan_distance_sum += abs(goal_row - state_row) + \
                abs(goal_column - state_column)
    return manhattan_distance_sum


# Minimum number of tiles that must leave one line to clear its linear
# conflicts. `goal_pos` lists, in board order, the goal position-along-the-line
# of each tile that belongs on the line; two tiles conflict when their board
# order is the reverse of their goal order. The tiles that stay must therefore
# be in increasing order, so the fewest removals is the length minus the
# longest increasing subsequence, found here by patience sorting: `tails[i]`
# keeps the smallest value ending an increasing run of length i + 1.
def _line_conflicts(goal_pos):
    tails = []
    for position in goal_pos:
        index = bisect.bisect_left(tails, position)
        if index == len(tails):
            tails.append(position)
        else:
            tails[index] = position
    return len(goal_pos) - len(tails)


# Manhattan distance plus the linear-conflict correction. Two tiles already on
# their goal line but in reversed order force one of them to step off the line
# and back - 2 moves Manhattan never counts. Adding those unavoidable detours
# keeps the heuristic admissible and consistent (it never overestimates the
# true distance) while dominating plain Manhattan, so A* expands far fewer
# states.
def linear_conflict(state, goal_state, size):
    total = manhattan_distance(state, goal_state, size)
    goal_rc = {tile: divmod(i, size) for i, tile in enumerate(goal_state)}
    for line in range(size):
        row = (state[line * size + c] for c in range(size))
        col = (state[r * size + line] for r in range(size))
        row_pos = [goal_rc[t][1]
                   for t in row if t != 0 and goal_rc[t][0] == line]
        col_pos = [goal_rc[t][0]
                   for t in col if t != 0 and goal_rc[t][1] == line]
        total += 2 * _line_conflicts(row_pos)
        total += 2 * _line_conflicts(col_pos)
    return total
