"""

    Global Variable Class for tracking Chess Variables

"""
import yaml

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

        return self