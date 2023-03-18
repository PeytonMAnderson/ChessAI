

def check_if_in_bounds(rank_i: int, file_i: int, env):
    #Check if location is out of bounds
    if rank_i < 0 or rank_i >= env.chess.board_ranks:
        return False
    elif file_i < 0 or file_i >= env.chess.board_files:
        return False
    return True
    
def check_if_blocked(rank_i: int, file_i: int, board: list, env):

    #Check if location is out of bounds
    in_bounds = check_if_in_bounds(rank_i, file_i, env)
    if in_bounds is False:
        return True
    piece_value = board[rank_i * env.chess.board_files + file_i]

    if piece_value != 0:
        return True
    else:
        return False
    
def check_if_capturable(rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list, env):
    moving_piece_value =  board[rank_i_old * env.chess.board_files + file_i_old]
    captured_piece_value =  board[rank_i_new * env.chess.board_files + file_i_new]
    moving_is_white = True if int(moving_piece_value / 10 ) == env.chess.piece_numbers['WHITE'] else False
    captured_is_white = True if int(captured_piece_value / 10 ) == env.chess.piece_numbers['WHITE'] else False
    if moving_is_white == captured_is_white:
        return False
    return True

def check_if_open(rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list, env):
    if check_if_in_bounds(rank_i_new, file_i_new, env) is False:
        return False
    if check_if_blocked(rank_i_new, file_i_new, board, env):
        if check_if_capturable(rank_i_old, file_i_old, rank_i_new, file_i_new, board, env):
            return True
        else:
            return False
    else:
        return True

def check_pawn_moves(rank_i_old: int, file_i_old: int, board: list, env):
    piece_value = board[rank_i_old * env.chess.board_files + file_i_old]
    valid_moves = []

    #Add Basic Move
    new_rank_diff = -1 if int(piece_value / 10 ) == env.chess.piece_numbers['WHITE'] else 1
    if int(piece_value / 10 ) == env.chess.piece_numbers['WHITE']:
        if check_if_blocked(rank_i_old + new_rank_diff, file_i_old, board, env) is False:
            valid_moves.append((rank_i_old + new_rank_diff, file_i_old))
    else:
        if check_if_blocked(rank_i_old + new_rank_diff, file_i_old, board, env) is False:
            valid_moves.append((rank_i_old + new_rank_diff, file_i_old))

    #Check if left is a piece to take
    new_r, new_f = rank_i_old + new_rank_diff, file_i_old - 1
    if check_if_blocked(new_r, new_f, board, env) is True and check_if_in_bounds(new_r, new_f, env) is True:
        if check_if_capturable(rank_i_old, file_i_old, new_r, new_f, board, env):
            valid_moves.append((new_r, new_f))

    #Check if right is a piece to take
    new_r, new_f = rank_i_old + new_rank_diff, file_i_old + 1
    if check_if_blocked(new_r, new_f, board, env)  is True and check_if_in_bounds(new_r, new_f, env) is True:
        if check_if_capturable(rank_i_old, file_i_old, new_r, new_f, board, env):
            valid_moves.append((new_r, new_f))

    #Add Starting double move
    if rank_i_old == env.chess.board_ranks - (env.chess.board_ranks - 1) and int(piece_value / 10 ) == env.chess.piece_numbers['BLACK']:
        if check_if_blocked(rank_i_old + 2, file_i_old, board, env) is False and check_if_blocked(rank_i_old + 1, file_i_old, board, env) is False:
            valid_moves.append((rank_i_old + 2, file_i_old))
    elif rank_i_old == env.chess.board_ranks - 2 and int(piece_value / 10 ) == env.chess.piece_numbers['WHITE']:
        if check_if_blocked(rank_i_old - 2, file_i_old, board, env) is False and check_if_blocked(rank_i_old - 1, file_i_old, board, env) is False:
            valid_moves.append((rank_i_old - 2, file_i_old))

    return valid_moves

def check_knight_moves(rank_i_old: int, file_i_old: int, board: list, env):
    valid_moves = []

    #Check top right 1
    r, f = rank_i_old + 2, file_i_old + 1
    if check_if_open(rank_i_old, file_i_old, r, f, board, env):
        valid_moves.append((r, f))
    #Check top right 2
    r, f = rank_i_old + 1, file_i_old + 2
    if check_if_open(rank_i_old, file_i_old, r, f, board, env):
        valid_moves.append((r, f))

    #Check top left 1
    r, f = rank_i_old + 2, file_i_old - 1
    if check_if_open(rank_i_old, file_i_old, r, f, board, env):
        valid_moves.append((r, f))
    #Check top left 2
    r, f = rank_i_old + 1, file_i_old - 2
    if check_if_open(rank_i_old, file_i_old, r, f, board, env):
        valid_moves.append((r, f))

    #Check bottom right 1
    r, f = rank_i_old - 2, file_i_old + 1
    if check_if_open(rank_i_old, file_i_old, r, f, board, env):
        valid_moves.append((r, f))
    #Check bottom right 2
    r, f = rank_i_old - 1, file_i_old + 2
    if check_if_open(rank_i_old, file_i_old, r, f, board, env):
        valid_moves.append((r, f))

    #Check bottom left 1
    r, f = rank_i_old - 2, file_i_old - 1
    if check_if_open(rank_i_old, file_i_old, r, f, board, env):
        valid_moves.append((r, f))
    #Check bottom left 2
    r, f = rank_i_old - 1, file_i_old - 2
    if check_if_open(rank_i_old, file_i_old, r, f, board, env):
        valid_moves.append((r, f))

    return valid_moves


def check_bishop_moves(rank_i_old: int, file_i_old: int, board: list, env):
    valid_moves = []

    #Check top right
    blocked = False
    r, f = rank_i_old, file_i_old
    while blocked is False:
        r += 1
        f += 1
        if check_if_in_bounds(r, f, env) is False:
            blocked = True
        elif check_if_blocked(r, f, board, env):
            if check_if_capturable(rank_i_old, file_i_old, r, f, board,  env):
                valid_moves.append((r, f))
            blocked = True
        else:
            valid_moves.append((r, f))

    #Check top left
    blocked = False
    r, f = rank_i_old, file_i_old
    while blocked is False:
        r += 1
        f -= 1
        if check_if_in_bounds(r, f, env) is False:
            blocked = True
        elif check_if_blocked(r, f, board, env):
            if check_if_capturable(rank_i_old, file_i_old, r, f, board, env):
                valid_moves.append((r, f))
            blocked = True
        else:
            valid_moves.append((r, f))

    #Check bottom right
    blocked = False
    r, f = rank_i_old, file_i_old
    while blocked is False:
        r -= 1
        f += 1
        if check_if_in_bounds(r, f, env) is False:
            blocked = True
        elif check_if_blocked(r, f, board, env):
            if check_if_capturable(rank_i_old, file_i_old, r, f, board, env):
                valid_moves.append((r, f))
            blocked = True
        else:
            valid_moves.append((r, f))

    #Check bottom left
    blocked = False
    r, f = rank_i_old, file_i_old
    while blocked is False:
        r -= 1
        f -= 1
        if check_if_in_bounds(r, f, env) is False:
            blocked = True
        elif check_if_blocked(r, f, board, env):
            if check_if_capturable(rank_i_old, file_i_old, r, f, board, env):
                valid_moves.append((r, f))
            blocked = True
        else:
            valid_moves.append((r, f))

    return valid_moves

def check_rook_moves(rank_i_old: int, file_i_old: int, board: list, env):
    valid_moves = []

    #Check right
    blocked = False
    r, f = rank_i_old, file_i_old
    while blocked is False:
        f += 1
        if check_if_in_bounds(r, f, env) is False:
            blocked = True
        elif check_if_blocked(r, f, board, env):
            if check_if_capturable(rank_i_old, file_i_old, r, f, board, env):
                valid_moves.append((r, f))
            blocked = True
        else:
            valid_moves.append((r, f))

    #Check left
    blocked = False
    r, f = rank_i_old, file_i_old
    while blocked is False:
        f -= 1
        if check_if_in_bounds(r, f, env) is False:
            blocked = True
        elif check_if_blocked(r, f, board, env):
            if check_if_capturable(rank_i_old, file_i_old, r, f, board, env):
                valid_moves.append((r, f))
            blocked = True
        else:
            valid_moves.append((r, f))
    
    #Check up
    blocked = False
    r, f = rank_i_old, file_i_old
    while blocked is False:
        r += 1
        if check_if_in_bounds(r, f, env) is False:
            blocked = True
        elif check_if_blocked(r, f, board, env):
            if check_if_capturable(rank_i_old, file_i_old, r, f, board, env):
                valid_moves.append((r, f))
            blocked = True
        else:
            valid_moves.append((r, f))

    #Check down
    blocked = False
    r, f = rank_i_old, file_i_old
    while blocked is False:
        r -= 1
        if check_if_in_bounds(r, f, env) is False:
            blocked = True
        elif check_if_blocked(r, f, board, env):
            if check_if_capturable(rank_i_old, file_i_old, r, f, board, env):
                valid_moves.append((r, f))
            blocked = True
        else:
            valid_moves.append((r, f))

    return valid_moves

def check_queen_moves(rank_i_old: int, file_i_old: int, board: list, env):
    bishop_moves = check_bishop_moves(rank_i_old, file_i_old, board, env)
    rook_moves = check_rook_moves(rank_i_old, file_i_old, board, env)
    return bishop_moves + rook_moves


def check_king_moves(rank_i_old: int, file_i_old: int, board: list, env):
    valid_moves = []

    ro, fo = rank_i_old - 1, file_i_old - 1
    for ri in range(3):
        for fi in range(3):
            r, f = ro + ri, fo + fi
            if check_if_in_bounds(r, f, env) is False:
                continue
            if check_if_blocked(r, f, board, env) is True:
                if check_if_capturable(rank_i_old, file_i_old, r, f, board, env):
                    valid_moves.append((r, f))
            else:
                valid_moves.append((r, f))
    
    return valid_moves

def get_piece_type_function(rank_i_old: int, file_i_old: int, board: list, env):
    piece_value = board[rank_i_old * env.chess.board_files + file_i_old]

    #Check piece type
    if piece_value % 10 == env.chess.piece_numbers['NONE']:
        return None
    elif piece_value % 10 == env.chess.piece_numbers['PAWN']:
        return check_pawn_moves
    elif piece_value % 10 == env.chess.piece_numbers['KNIGHT']:
        return check_knight_moves
    elif piece_value % 10 == env.chess.piece_numbers['BISHOP']:
        return check_bishop_moves
    elif piece_value % 10 == env.chess.piece_numbers['ROOK']:
        return check_rook_moves
    elif piece_value % 10 == env.chess.piece_numbers['QUEEN']:
        return check_queen_moves
    elif piece_value % 10 == env.chess.piece_numbers['KING']:
        return check_king_moves
    else:
        return None
    
def get_base_moves(rank_i_old: int, file_i_old: int, board: list, env):
    piece_function = get_piece_type_function(rank_i_old, file_i_old, board, env)
    if piece_function is not None:
        valid_moves = piece_function(rank_i_old, file_i_old, board, env)
        if valid_moves is not None:
            return valid_moves
    return []

def base_move(rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, board: list, env) -> list:
    #Returns a board with a move
    board_position_old = rank_i_old * env.chess.board_files + file_i_old
    board_position_new = rank_i_new * env.chess.board_files + file_i_new
    new_board = board.copy()

    if board_position_old < len(new_board) and board_position_new < len(new_board):
        new_board[board_position_new] = new_board[board_position_old]
        new_board[board_position_old] = 0

    return new_board