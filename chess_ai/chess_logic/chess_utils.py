

def get_piece_on_board(rank_i: int, file_i: int, env):
    board_position = rank_i * env.chess.board_files + file_i
    if board_position < len(env.chess.board):
        return env.chess.board[board_position]
    print("WARNING: Location on board is out of range.")
    return 0

def get_piece_value(letter: str, piece_numbers: dict) -> int:
    
    #Black Pieces
    if letter == 'p':
        return piece_numbers['PAWN'] + piece_numbers['BLACK'] * 10
    elif letter == 'n':
        return piece_numbers['KNIGHT'] + piece_numbers['BLACK'] * 10
    elif letter == 'b':
        return piece_numbers['BISHOP'] + piece_numbers['BLACK'] * 10
    elif letter == 'r':
        return piece_numbers['ROOK'] + piece_numbers['BLACK'] * 10
    elif letter == 'q':
        return piece_numbers['QUEEN'] + piece_numbers['BLACK'] * 10
    elif letter == 'k':
        return piece_numbers['KING'] + piece_numbers['BLACK'] * 10

    #White Pieces
    elif letter == 'P':
        return piece_numbers['PAWN'] + piece_numbers['WHITE'] * 10
    elif letter == 'N':
        return piece_numbers['KNIGHT'] + piece_numbers['WHITE'] * 10
    elif letter == 'B':
        return piece_numbers['BISHOP'] + piece_numbers['WHITE'] * 10
    elif letter == 'R':
        return piece_numbers['ROOK'] + piece_numbers['WHITE'] * 10
    elif letter == 'Q':
        return piece_numbers['QUEEN'] + piece_numbers['WHITE'] * 10
    elif letter == 'K':
        return piece_numbers['KING'] + piece_numbers['WHITE'] * 10

    #Else this is not a piece
    else:
        return 0
    
def get_is_white(piece_value: int, piece_numbers: dict) -> bool:
    return True if int(piece_value / 10) == piece_numbers['WHITE'] else False
    
def get_piece_type_str(piece_value: int, piece_numbers: dict, upper_case: bool) -> str | None:
    
    #Check piece type
    if piece_value % 10 == piece_numbers['NONE']:
        return None
    elif piece_value % 10 == piece_numbers['PAWN']:
        return 'P' if upper_case else 'p'
    elif piece_value % 10 == piece_numbers['KNIGHT']:
        return 'N' if upper_case else 'n'
    elif piece_value % 10 == piece_numbers['BISHOP']:
        return 'B' if upper_case else 'b'
    elif piece_value % 10 == piece_numbers['ROOK']:
        return 'R' if upper_case else 'r'
    elif piece_value % 10 == piece_numbers['QUEEN']:
        return 'Q' if upper_case else 'q'
    elif piece_value % 10 == piece_numbers['KING']:
        return 'K' if upper_case else 'k'
    else:
        return None
    
def get_piece_str(piece_value: int, piece_numbers: dict) -> str:

    #If there is no piece
    if piece_value % 10 == piece_numbers['NONE']:
        return None
    #Check if black or white
    white = True if int(piece_value / 10) == piece_numbers['WHITE'] else False
    #White
    if white:
        return get_piece_type_str(piece_value, piece_numbers, True)
    #Black
    else:
        return get_piece_type_str(piece_value, piece_numbers, False)
    
def get_file_from_number(file_index: int) -> str:
    return chr(ord('a') + file_index)

def get_number_from_file(file_str: str) -> int:
    return ord(file_str) - ord('a')

def convert_fen_to_board(fen_string: str, file_dim: int, rank_dim: int, piece_numbers: dict) -> list:
    board_array = [0] * rank_dim * file_dim

    #Get the piece positions from the fen string
    split_string = fen_string.split(" ")
    piece_positions = split_string[0]
    turn = split_string[1] if len(split_string) >= 2 else None
    castle_avail = split_string[2] if len(split_string) >= 3 else None
    enpassant = split_string[3] if len(split_string) >= 4 else None
    half_move = split_string[4] if len(split_string) >= 5 else None
    full_move = split_string[5] if len(split_string) >= 6 else None

    #Go through the ranks
    piece_ranks = piece_positions.split("/")
    rank_index = 0
    for rank in piece_ranks:

        #Go through the files
        file_index = 0
        string_index = 0
        while file_index < file_dim and string_index < len(rank):
            piece = rank[string_index]

            if piece.isdigit() is False:
                if len(board_array) > rank_index * file_dim + file_index:
                    board_array[rank_index * file_dim + file_index] = get_piece_value(piece, piece_numbers)
                file_index += 1
                string_index += 1
            else:
                file_index += int(piece)
                string_index += 1
        rank_index += 1

    #Get Turn
    is_white = True if turn is None or turn == 'w' else False

    return [ board_array, is_white, castle_avail, enpassant, half_move, full_move ]

def convert_board_to_fen(board: list, file_dim: int, rank_dim: int, piece_numbers: dict, env) -> str:
    rank_index = 0
    file_index = 0

    rank_str = ""
    #Go Through ranks
    while rank_index < rank_dim:

        #Go Through Files
        file_str_total = ""
        file_str_prev = ''
        file_index = 0
        while file_index < file_dim:

            #Get value from board
            board_value = board[rank_index * file_dim + file_index]
            s = get_piece_str(board_value, piece_numbers)

            #If value is a string or a number
            if s is not None:
                file_str_prev = s
                file_str_total = file_str_total + s

            else:
                #If Previous str was also a digit, increment instead of adding new
                if file_str_prev.isdigit():
                    prev_digit = int(file_str_prev)
                    file_str_total = file_str_total.removesuffix(file_str_prev)
                    file_str_prev = str(prev_digit + 1)
                    file_str_total = file_str_total + str(prev_digit + 1)
                
                #New Space, add 1 as beginning digit
                else:
                    file_str_prev = "1"
                    file_str_total = file_str_total + "1"

            #Increment File
            file_index += 1
        
        #Add Rank to rank String
        if len(rank_str) > 0:
            rank_str = rank_str + "/" + file_str_total
        else:
            rank_str = file_str_total

        #Increment Rank
        rank_index += 1
    
    #Add Active color:
    color_str = "w" if env.chess.whites_turn else "b"

    return rank_str + " " + color_str

def get_move_str(rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, env):
    board_position_old = rank_i_old * env.chess.board_files + file_i_old
    board_position_new = rank_i_new * env.chess.board_files + file_i_new

    #Get the pieces that are moving and the captured piece
    moving_piece = env.chess.board[board_position_old]
    destination_piece = env.chess.board[board_position_new]

    #Determin if a capture happened
    capture_string = ""
    if destination_piece != 0:
        capture_string = "x"

    #Get the destination rank and file
    destination_rank_str: str = str(env.chess.board_ranks - rank_i_new)
    destination_file_str: str = get_file_from_number(file_i_new)
    moving_piece_file_str: str = ''
    moving_piece_str: str = get_piece_type_str(moving_piece, env.chess.piece_numbers, True)

    #Show file from for certain cases
    if moving_piece_str == 'P' and capture_string == 'x':
        moving_piece_file_str = get_file_from_number(file_i_old)

    #Remove the P if it was a Pawn
    if moving_piece_str == 'P':
        moving_piece_str = ''

    #Return the entire Move string
    return moving_piece_file_str + moving_piece_str + capture_string + destination_file_str + destination_rank_str

def get_position_from_move_str(move_str: str, env) -> tuple | None:
    if move_str is None:
        return None
    rank = move_str[len(move_str)-1]
    file = move_str[len(move_str)-2]

    file_i = get_number_from_file(file)
    rank_i = env.chess.board_ranks - int(rank)



    print((rank_i, file_i))
    return rank_i, file_i