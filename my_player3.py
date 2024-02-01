import copy
import random

def find_empty_positions(current_board):
    empty_pos = []
    for row in range(len(current_board)):
        for col in range(len(current_board[row])):
            if current_board[row][col] == 0:
                empty_pos.append((row,col))
    return empty_pos

def find_neighbor(row, col):
    neighbors = []
    if row > 0:
        neighbors.append((row-1, col))
    if row < 4:
        neighbors.append((row+1, col))
    if col > 0:
        neighbors.append((row, col-1))
    if col < 4:
        neighbors.append((row, col+1))
    return neighbors

def find_same_color_neighbor(row, col, color, current_board):
    neighbors = find_neighbor(row, col)
    same_color_neighbor = []
    for neighbor_pos in neighbors:
        neighbor_row, neighbor_col = neighbor_pos
        if current_board[neighbor_row][neighbor_col] == color:
            same_color_neighbor.append(neighbor_pos)
    return same_color_neighbor


def find_connect_group(row, col, color, current_board):
    unvisited = [(row, col)]
    connect_group = []

    while unvisited:
        current_row, current_col = unvisited.pop()
        if (current_row, current_col) not in connect_group:
            connect_group.append((current_row, current_col))

        same_color_neighbors = find_same_color_neighbor(current_row, current_col, color, current_board)
        for neighbor_pos in same_color_neighbors:
            if neighbor_pos not in connect_group and neighbor_pos not in unvisited:
                unvisited.append(neighbor_pos)

    return connect_group

def check_liberty(row, col, color, current_board):
    liberty = []
    next_board = copy.deepcopy(current_board)
    next_board[row][col] = color
    connect_group = find_connect_group(row, col, color, next_board)
    for group_pos in connect_group:
        group_row, group_col = group_pos
        group_neighbor = find_neighbor(group_row, group_col)
        for group_neighbor_pos in group_neighbor:
            group_neighbor_row, group_neighbor_col = group_neighbor_pos
            if next_board[group_neighbor_row][group_neighbor_col] == 0 and group_neighbor_pos not in liberty:
                liberty.append(group_neighbor_pos)
    return liberty

def remove_suicide_moves(color, current_board):
    possible_moves = find_empty_positions(current_board)
    for possible_pos in possible_moves:
        possible_row, possible_col = possible_pos
        next_board = check_next_board(possible_row, possible_col, color, current_board)
        liberty = check_liberty(possible_row, possible_col, color, next_board)
        if not liberty and possible_pos in possible_moves:
            possible_moves.remove(possible_pos)
    return possible_moves

def find_all_connect_group(color, current_board):
    connect_group_set = set()
    same_color = []
    for row in range(len(current_board)):
        for col in range(len(current_board[row])):
            if current_board[row][col] == color:
                same_color.append((row,col))
    for same_color_pos in same_color:
        same_color_row, same_color_col = same_color_pos
        connect_group = find_connect_group(same_color_row, same_color_col, color, current_board)
        connect_group_as_set = frozenset(connect_group)
        connect_group_set.add(connect_group_as_set)
    result_as_list_of_lists = [list(group) for group in connect_group_set]
    return result_as_list_of_lists


def capture_after_move(row, col, color, current_board):
    captured = []
    next_board = copy.deepcopy(current_board)
    next_board[row][col] = color

    opponent_color = 3-color

    current_connect_group = find_all_connect_group(opponent_color, current_board)

    for group in current_connect_group:
        has_liberty = False
        for stone in group:
            stone_row, stone_col = stone
            liberty = check_liberty(stone_row, stone_col, opponent_color, next_board)
            if liberty:
                has_liberty = True
                break

        if not has_liberty:
            captured.extend(group)

    return captured


def check_next_board(row, col, color, current_board):
    next_board = copy.deepcopy(current_board)
    next_board[row][col] = color

    captured = capture_after_move(row, col, color, current_board)
    for captured_pos in captured:
        captured_row, captured_col = captured_pos
        next_board[captured_row][captured_col] = 0
    return next_board


def find_legal_moves(color, previous_board, current_board):
    possible_moves = remove_suicide_moves(color, current_board)
    legal_moves = []
    for possible_move_pos in possible_moves:
        possible_row, possible_col = possible_move_pos
        next_board = check_next_board(possible_row, possible_col, color, current_board)
        if next_board != previous_board:
            legal_moves.append(possible_move_pos)
    return legal_moves

def find_good_moves(color, previous_board, current_board):
    legal_moves = find_legal_moves(color, previous_board, current_board)
    good_moves = []
    for move in legal_moves:
        row, col = move
        captured = capture_after_move(row, col, color, current_board)
        if len(captured) >= 1:
            good_moves.append(move)
    if not good_moves:
        for move in legal_moves:
            row, col = move
            liberty = check_liberty(row, col, color, current_board)
            if len(liberty) >= 2:
                good_moves.append(move)

    return good_moves

def find_all_liberty(color, current_board):
    connect_group = find_all_connect_group(color, current_board)
    all_liberty = []
    for group in connect_group:
        row, col = group[0]
        liberty_group = check_liberty(row, col, color, current_board)
        for liberty_pos in liberty_group:
            if liberty_pos not in all_liberty:
                all_liberty.append(liberty_pos)
    return all_liberty

def check_connectedness(color, current_board):
    connect_group = find_all_connect_group(color, current_board)
    max_connectedness = 0
    for group in connect_group:
        connectedness = len(group)
        if connectedness > max_connectedness:
            max_connectedness = connectedness
    return max_connectedness

def evaluate_board(color, current_board):
    komi = 2.5
    my_score = 0
    opponent_score = 0

    opponent_color = 3-color

    my_liberty = find_all_liberty(color, current_board)
    opponent_liberty = find_all_liberty(opponent_color, current_board)

    my_connectedness = check_connectedness(color, current_board)
    opponent_connectedness = check_connectedness(opponent_color, current_board)

    for row in current_board:
        for cell in row:
            if cell == color:
                my_score += 1
            elif cell == opponent_color:
                opponent_score += 1

    if color == 2:
        my_score += komi
    if opponent_color == 2:
        opponent_score += komi

    return (my_score - opponent_score) - 2*len(opponent_liberty) + 0.5 * (my_connectedness - opponent_connectedness)


def minimax(previous_board, current_board, depth, alpha, beta, color, maximizing_player):
    if depth == 0:
        return evaluate_board(color, current_board), None

    legal_moves = find_good_moves(color, previous_board, current_board)
    if not legal_moves:
        return 0, ['PASS']

    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        for move in legal_moves:
            row, col = move
            next_board = check_next_board(row, col, color, current_board)
            eval, _ = minimax(current_board, next_board, depth-1, alpha, beta, 3-color, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in legal_moves:
            row, col = move
            next_board = check_next_board(row, col, color, current_board)
            eval, _ = minimax(current_board, next_board, depth-1, alpha, beta, 3-color, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

def find_best_move(color, previous_board, current_board):
    legal_moves = find_good_moves(color, previous_board, current_board)
    if (len(legal_moves) == 25) and color == 1:
        best_move = (2, 2)
    elif (len(legal_moves) == 24) and color == 2:
        if (2, 2) in legal_moves:
            best_move = (2, 2)
        else:
            best_move = random.choice((2, 3), (2, 1), (1, 2), (3, 2))
    else:
        best_score, best_move = minimax(previous_board, current_board, depth=2, alpha=float('-inf'), beta=float('inf'),
                                        color=color, maximizing_player=True)

    return best_move

def read_input():
    with open('input.txt') as file:
        file_lines = file.readlines()
        color = int(file_lines[0])
        previous_board = [[int(pos) for pos in row.strip('\n')] for row in file_lines[1:6]]
        current_board = [[int(pos) for pos in row.strip('\n')] for row in file_lines[6:11]]
        return color, previous_board, current_board

def output(next_move):
    with open('output.txt', 'w') as file:
        if next_move != "PASS":
            file.write(str(next_move[0]) + ',' + str(next_move[1]))
        else:
            file.write(next_move)

def run():
    color, previous_board, current_board = read_input()
    next_move = find_best_move(color, previous_board, current_board)
    output(next_move)

run()