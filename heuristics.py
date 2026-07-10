def hamming_distance(state, goal_state):
    paired_tiles = zip(state, goal_state)
    misplaced_tiles_count = 0
    for s, g in paired_tiles:
        if s != g and s != 0:
            misplaced_tiles_count += 1
    return misplaced_tiles_count


def manhattan_distance(state, goal_state):
    return "work in progress"
