

class ChessUtils:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def get_piece_number_on_board(self, rank_i: int, file_i: int, board: list, board_files_count: int) -> int:
        """Get the piece number at board[rank_i * board_files_count + file_i] (rank_i, file_i) from the board list.

            Returns: piece number at that location.
        """
        board_position = rank_i * board_files_count + file_i
        if board_position < len(board):
            return board[board_position]
        print("WARNING: Location on board is out of range.")
        return 0

    def get_piece_number_from_str(self, letter: str, piece_numbers: dict) -> int:
        """Get the piece number from the letter of a FEN string.

            Valid letters: 'pnbrqkPNBRQK'
            Calculation: piece_type + piece_color * 10

            Returns: piece number of the indicated letter.
        """
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
        else:
            return 0
    
    def get_is_white_from_piece_number(self, piece_value: int, piece_numbers: dict) -> bool:
        """Get if the color of the piece value is white.

            Returns: True if piece is white, else False if piece is black
        """
        return True if int(piece_value / 10) == piece_numbers['WHITE'] else False
    
    def get_str_from_piece_type(self, piece_value: int, piece_numbers: dict, is_white: bool) -> str | None:
        """Get letter of piece type. Works for white (Uppercase) and black(Lowercase) from is_white input.

            Valid letters: 'pnbrqkPNBRQK'
            Calculation: piece_value % 10 == piece_type

            Returns: Letter of piece or None if piece does not exist.
        """
        if piece_value % 10 == piece_numbers['NONE']:
            return None
        elif piece_value % 10 == piece_numbers['PAWN']:
            return 'P' if is_white else 'p'
        elif piece_value % 10 == piece_numbers['KNIGHT']:
            return 'N' if is_white else 'n'
        elif piece_value % 10 == piece_numbers['BISHOP']:
            return 'B' if is_white else 'b'
        elif piece_value % 10 == piece_numbers['ROOK']:
            return 'R' if is_white else 'r'
        elif piece_value % 10 == piece_numbers['QUEEN']:
            return 'Q' if is_white else 'q'
        elif piece_value % 10 == piece_numbers['KING']:
            return 'K' if is_white else 'k'
        else:
            return None
        
    def get_str_from_piece_number(self, piece_value: int, piece_numbers: dict) -> str | None:
        """Calculates the letter of piece type. Determines if piece is white then calls: get_str_from_piece_type.

            Valid letters: 'pnbrqkPNBRQK'
            Calculation:    int(piece_value / 10) == piece_color
                            piece_value % 10 == piece_type

            Returns: Letter of piece or None if piece does not exist.
        """
        if piece_value % 10 == piece_numbers['NONE']:
            return None
        if self.get_is_white_from_piece_number(piece_value, piece_numbers):
            return self.get_str_from_piece_type(piece_value, piece_numbers, True)
        else:
            return self.get_str_from_piece_type(piece_value, piece_numbers, False)
    
    def get_file_from_number(self, file_index: int) -> str:
        """Get the file letter from the file index.

            Returns: Letter of current file.
        """
        return chr(ord('a') + file_index)

    def get_number_from_file(self, file_str: str) -> int:
        """Get the file index from the file letter.

            Returns: Index of current file.
        """
        return ord(file_str) - ord('a')
    
    def get_rank_from_number(self, rank_index: int, board_rank_count: int) -> str:
        """Get the rank str from the rank index.

            Returns: str of current rank.
        """
        return str(board_rank_count - rank_index)
    
    def get_number_from_rank(self, rank_str: str, board_rank_count: int) -> int:
        """Get the rank index from the rank str.

            Returns: Index of current rank.
        """
        return board_rank_count - int(rank_str)
    
    def get_position_from_rank_file(self, rank_file_str: str, board_rank_count: int) -> tuple | None:
        """Get the position (rank_i, file_i) from the rank file strings.

            Returns: Tuple (rank_i, file_i) of the rank_file_str.
        """
        if len(rank_file_str) == 2:
            file = rank_file_str[0]
            rank = rank_file_str[1]
            return self.get_number_from_rank(rank, board_rank_count), self.get_number_from_file(file)
        return None
    
    def convert_fen_to_board(self, fen_string: str, file_dim: int, rank_dim: int, piece_numbers: dict) -> list:
        """Reads a FEN string can parses data from the string.
                Calculates:
                    Board: Piece Locations
                    Turn: White or Black turn
                    Castling: Castling Availability as str
                    En passant: En passant Availability as str
                    Half Move: Half Move number
                    Full Move: Full Move number
            
            returns list[ Board, Turn, Castling, enpassant, half_move, full_move ]
        """
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
                        board_array[rank_index * file_dim + file_index] = self.get_piece_number_from_str(piece, piece_numbers)
                    file_index += 1
                    string_index += 1
                else:
                    file_index += int(piece)
                    string_index += 1
            rank_index += 1

        #Get Turn
        is_white = True if turn is None or turn == 'w' else False

        return [ board_array, is_white, castle_avail, enpassant, half_move, full_move ]

    def convert_board_to_fen(self, 
            board: list, 
            whites_turn: bool,
            castling_avail: str,
            en_passant_avail: str,
            half_move: int,
            full_move: int,
            file_dim: int, 
            rank_dim: int, 
            piece_numbers: dict
        ) -> str:
        """Reads a board and converts board into a FEN string.
                Calculates:
                    Board: Piece Locations
                    whites_turn: White or Black turn
                    castling_avail: Castling Availability as str
                    en_passant_avail: En passant Availability as str
                    half_move: Half Move number
                    full_move: Full Move number
            
            returns list[ Board, Turn, Castling, enpassant, half_move, full_move ]
        """
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
                s = self.get_str_from_piece_number(board_value, piece_numbers)

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
        color_str = "w" if whites_turn else "b"
        return rank_str + " " + color_str + " " + castling_avail + " " + en_passant_avail + " " + str(half_move) + " " + str(full_move)