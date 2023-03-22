

class ChessUtils:
    def __init__(self, piece_values: dict, *args, **kwargs) -> None:
        self.piece_values = piece_values

    def _calc_piece_value(self, piece_str: str = None, piece_type: str = None, is_white: bool = None) -> int | None:
        """Calculate the piece value from the piece string alone or piece_type and is_white together.

            *Note: Both are same speed.

            Returns: Numerical value of the piece using the piece_values dict.
        """
        if  piece_str is not None:
            if piece_str.isupper():
                strings_upper = [("PAWN","P"), ("KNIGHT","N"), ("BISHOP","B"), ("ROOK","R"), ("QUEEN","Q"), ("KING","K")]
                for value, key in strings_upper:
                    if key == piece_str:
                        return self.piece_values[value] + self.piece_values["WHITE"] * 10
            else:
                strings_lower = [("PAWN","p"), ("KNIGHT","n"), ("BISHOP","b"), ("ROOK","r"), ("QUEEN","q"), ("KING","k")]
                for value, key in strings_lower:
                    if key == piece_str:
                        return self.piece_values[value] + self.piece_values["BLACK"] * 10
        #Calculate from piece type and color
        elif piece_type is not None and is_white is not None:
            strings = [("PAWN","p"), ("KNIGHT","n"), ("BISHOP","b"), ("ROOK","r"), ("QUEEN","q"), ("KING","k")]
            for value, key in strings:
                if key == piece_type:
                    color_value = self.piece_values["WHITE"] * 10 if is_white else self.piece_values["BLACK"] * 10
                    return self.piece_values[value] + color_value 
        return None

    def _calc_piece_str(self, piece_value: int = None, piece_type: str = None, is_white: bool = None) -> str | None:
        """Calculate the piece string from the piece value alone or piece_type and is_white together.

            *Note: Piece type and is_white is faster.

            Returns: Piece str using piece_values dict as a guide.
        """
        #Calculate from piece value
        if  piece_value is not None:
            strings = [("PAWN","p"), ("KNIGHT","n"), ("BISHOP","b"), ("ROOK","r"), ("QUEEN","q"), ("KING","k")]
            white = True if int(piece_value / 10) == self.piece_values['WHITE'] else False
            for key, value in strings:
                if piece_value % 10 == self.piece_values[key]:
                    return value.capitalize() if white else value
                
        #Calculate from piece type and color
        elif piece_type is not None and is_white is not None:
            return piece_type.capitalize() if is_white else piece_type
        return None
    
    def _calc_piece_type_color(self, piece_value: int = None, piece_str: str = None) -> tuple:
        """Calculates the piece_type and is_white value from piece_value or piece_str.

            *Note: piece_str is faster.

            Returns tuple: (Piece Type, Piece Color)
        """
        if piece_value is not None:
            strings_upper = [("PAWN","P"), ("KNIGHT","N"), ("BISHOP","B"), ("ROOK","R"), ("QUEEN","Q"), ("KING","K")]
            is_white = True if int(piece_value / 10) == self.piece_values['WHITE'] else False
            for key, value in strings_upper:
                if piece_value % 10 == self.piece_values[key]:
                    return value, is_white
        elif piece_str is not None:
            is_white = True if piece_str.isupper() else False
            piece_type = piece_str.capitalize()
            return piece_type, is_white 
        return None, None
    
    def get_file_from_number(self, file_index: int, board_file_count: int = None, perspective: str = "WHITE") -> str:
        """Get the file letter from the file index.
            Returns: Letter of current file.
        """
        if perspective == "BLACK":
            return chr(ord('a') + board_file_count - file_index - 1)
        else:
            return chr(ord('a') + file_index)

    def get_number_from_file(self, file_str: str) -> int:
        """Get the file index from the file letter.
            Returns: Index of current file.
        """
        return ord(file_str) - ord('a')
    
    def get_rank_from_number(self, rank_index: int, board_rank_count: int, perspective: str = "WHITE") -> str:
        """Get the rank str from the rank index.
            Returns: str of current rank.
        """
        if perspective == "BLACK":
            return str(rank_index + 1)
        else:
            return str(board_rank_count - rank_index)
    
    def get_number_from_rank(self, rank_str: str, board_rank_count: int) -> int:
        """Get the rank index from the rank str.
            Returns: Index of current rank.
        """
        return board_rank_count - int(rank_str)