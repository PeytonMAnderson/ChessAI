from .chess_base_moves import get_base_moves
from .chess_utils import get_piece_value

def get_king_position(king_value, env) -> tuple | None:
    rank_i = 0
    file_i = 0
    for piece in env.chess.board:

        #Check if piece at position is the required king
        if piece == king_value:
            return rank_i, file_i
        
        #Adjust rank and file
        if file_i >= env.chess.board_files - 1:
            rank_i += 1
            file_i = 0
        else:
            file_i += 1
        
    return None

def get_piece_values_for_color(is_white: bool, env) -> list:
    piece_values = []
    piece_types_black = ['p', 'n', 'b', 'r', 'q', 'k']
    piece_types_white = ['P', 'N', 'B', 'R', 'Q', 'K']
    types = piece_types_white if is_white else piece_types_black
    for type in types:
        piece_values.append(get_piece_value(type, env.chess.piece_numbers))
    return piece_values

def get_all_piece_locations(is_white: bool, env) -> list:
    #Get all locations for pieces of the team
    pieces_list = []
    piece_types = get_piece_values_for_color(is_white, env)
    rank_i = 0
    file_i = 0
    for piece in env.chess.board:

        #Check if current piece is a member of the team
        if piece_types.count(piece):
            pieces_list.append((rank_i, file_i))

        #Increase rank and file
        if file_i >= env.chess.board_files - 1:
            rank_i += 1
            file_i = 0
        else:
            file_i += 1
    return pieces_list

def get_all_moves(is_white: bool, env) -> list:
    #Get all pieces for team and get all of their moves
    pieces_list = get_all_piece_locations(is_white, env)
    moves_list = []
    for piece_r, piece_f in pieces_list:
        moves_list = moves_list + get_base_moves(piece_r, piece_f, env)
    return moves_list        

def check_all_moves_for_check(rank_i: int, file_i: int, is_white: bool, env) -> bool:
    #Get all the moves of the other team and see if a move causes check
    moves_list = get_all_moves( not is_white, env)
    for move in moves_list:
        if move == (rank_i, file_i):
            return True
    return False
    
def check_for_check(king_value, env) -> bool:
    #Check for check by checking all moves of other team
    king_pos = get_king_position(king_value, env)
    is_white = True if int(king_value / 10) == env.chess.piece_numbers['WHITE'] else False
    if king_pos is not None:
        return check_all_moves_for_check(king_pos[0], king_pos[1], is_white, env)
    print("WARNING: Unable to determine King Position")
    return False