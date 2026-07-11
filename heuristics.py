def hamming_distance(state, goal_state):
    paired_tiles = zip(state, goal_state)
    misplaced_tiles_count = 0
    for s, g in paired_tiles:
        if s != g and s != 0:
            misplaced_tiles_count += 1
    return misplaced_tiles_count


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
