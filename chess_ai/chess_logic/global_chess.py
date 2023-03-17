"""

    Global Variable Class for tracking Chess Variables

"""
import yaml

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

def convert_fen_to_board(fen_string: str, file_dim: int, rank_dim: int, piece_numbers: dict) -> list:
    board_array = [0] * rank_dim * file_dim

    #Get the piece positions from the fen string
    split_string = fen_string.split(" ")
    piece_positions = split_string[0]
    piece_ranks = split_string[0].split("/")

    #Go through the ranks
    rank_index = 0
    for rank in piece_ranks:

        #Go through the files
        file_index = 0
        string_index = 0
        while file_index < file_dim and string_index < len(rank):
            piece = rank[string_index]

            if piece.isdigit() is False:
                board_array[rank_index * file_dim + file_index] = get_piece_value(piece, piece_numbers)
                file_index += 1
                string_index += 1
            else:
                file_index += int(piece)
                string_index += 1
        
        rank_index += 1
    return board_array 

def convert_board_to_fen(board: list, file_dim: int, rank_dim: int, piece_numbers: dict) -> str:
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

    return rank_str

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

def move_piece(rank_i_old: int, file_i_old: int, rank_i_new: int, file_i_new: int, env):
    board_position_old = rank_i_old * env.chess.board_files + file_i_old
    board_position_new = rank_i_new * env.chess.board_files + file_i_new

    if board_position_old < len(env.chess.board) and board_position_new < len(env.chess.board):
        
        #Get Move String
        new_move = get_move_str(rank_i_old, file_i_old, rank_i_new, file_i_new, env)

        #Update Piece on board
        env.chess.board[board_position_new] = env.chess.board[board_position_old]
        env.chess.board[board_position_old] = 0

        #Get New FEN String
        new_board = convert_board_to_fen(env.chess.board, env.chess.board_files, env.chess.board_ranks, env.chess.piece_numbers)

        print(f"New Move: {new_move}")
        print(f"New Board: {new_board}")

        #If current position in history is less than the present and new move, remove all updates after history_position and update from there
        if len(env.chess.history) - 1 > env.chess.history_position:
            while len(env.chess.history) - 1 > env.chess.history_position:
                env.chess.history.pop()
        env.chess.history.append((new_move, new_board))
        env.chess.history_position = len(env.chess.history) - 1

#Global Variable Class
class GlobalChess:
    def __init__(self,
                 board_files: int = 8,
                 board_ranks: int = 8,
                 board: list =  [],
                 piece_numbers: dict = {},
    *args, **kwargs) -> None:
        self.board_files = board_files
        self.board_ranks = board_ranks
        self.board = board
        self.history = []
        self.history_position = 0
        self.piece_numbers = piece_numbers

    def set_from_yaml(self, yaml_path: str) -> "GlobalChess":
        with open(yaml_path, "r") as f:
            yaml_settings = yaml.safe_load(f)
            settings = yaml_settings['CHESS']

            #Save Chess Values
            self.board_files = settings['BOARD_FILES']
            self.board_ranks = settings['BOARD_RANKS']
            self.piece_numbers = settings['PIECE_NUMBERS']
            self.board = convert_fen_to_board(settings['BOARD'], self.board_files, self.board_ranks, self.piece_numbers)
            self.history.append((None, settings['BOARD']))

        return self