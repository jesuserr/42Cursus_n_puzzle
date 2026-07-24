# Counts tiles that are out of place (blank excluded).
# `size` is unused; kept so both heuristics share one call signature.
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
# order is the reverse of their goal order. Counts REMOVED tiles, not
# conflicting pairs (one tile can settle several conflicts at once, so counting
# pairs would overestimate and break admissibility), greedily removing the
# most-conflicted tile until none remain.
def _line_conflicts(goal_pos):
    goal_pos = list(goal_pos)
    counts = [0] * len(goal_pos)
    for i in range(len(goal_pos)):
        for j in range(i + 1, len(goal_pos)):
            if goal_pos[i] > goal_pos[j]:
                counts[i] += 1
                counts[j] += 1
    removed = 0
    while max(counts, default=0) > 0:
        k = counts.index(max(counts))
        for j in range(len(goal_pos)):
            if goal_pos[j] is None or j == k:
                continue
            if (k < j and goal_pos[k] > goal_pos[j]) or \
               (k > j and goal_pos[k] < goal_pos[j]):
                counts[j] -= 1
        counts[k] = 0
        goal_pos[k] = None
        removed += 1
    return removed


# Manhattan distance plus the linear-conflict correction. Two tiles already on
# their goal line but in reversed order force one of them to step off the line
# and back - 2 moves Manhattan never counts. Adding those unavoidable detours
# keeps the heuristic admissible and consistent (so the minimum-move guarantee
# holds) while dominating plain Manhattan, so A* expands far fewer states.
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
