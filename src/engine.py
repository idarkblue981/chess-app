import chess
import settings

class ChessEngine:
    def __init__(self):
        self.board = chess.Board()
        self.move_history_san = []
        self.selected_square = None
        self.legal_moves = []

    def get_square_under_mouse(self, mouse_pos):
        x, y = mouse_pos
        # valorile globale
        col = (x - settings.OFFSET_X) // settings.SQ_SIZE
        row = 7 - ((y - settings.OFFSET_Y) // settings.SQ_SIZE)
        
        if 0 <= col < 8 and 0 <= row < 8:
            return chess.square(col, row)
        return None

    """def handle_click(self, mouse_pos):
        square = self.get_square_under_mouse(mouse_pos)
        
        if square is None:
            return None

        if self.selected_square is not None:
            piece = self.board.piece_at(self.selected_square)
            
            if piece and piece.piece_type == chess.PAWN:
                dest_rank = chess.square_rank(square)
                if (piece.color == chess.WHITE and dest_rank == 7) or \
                   (piece.color == chess.BLACK and dest_rank == 0):
                    
                    move_test = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
                    if move_test in self.board.legal_moves:
                        self.move_history_san.append(self.board.san(move)) 
                        self.board.push(move)
                        self.selected_square = None
                        return "move"
                        from_sq = self.selected_square
                        self.selected_square = None 
                        return "promotion_needed", (from_sq, square)

            move = chess.Move(self.selected_square, square)
            
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                return "move"
            else:
                new_piece = self.board.piece_at(square)
                if new_piece and new_piece.color == self.board.turn:
                    self.selected_square = square
                else:
                    self.selected_square = None
        else:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square

        return None"""
    
    def handle_click(self, mouse_pos):
        square = self.get_square_under_mouse(mouse_pos)
        if square is None:
            return None

        if self.selected_square is not None:
            piece = self.board.piece_at(self.selected_square)
            
            if piece and piece.piece_type == chess.PAWN:
                dest_rank = chess.square_rank(square)
                if (piece.color == chess.WHITE and dest_rank == 7) or \
                   (piece.color == chess.BLACK and dest_rank == 0):
                    
                    move_test = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
                    if move_test in self.board.legal_moves:
                        from_sq = self.selected_square
                        self.selected_square = None 
                        return "promotion_needed", (from_sq, square)

            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.move_history_san.append(self.board.san(move)) 
                self.board.push(move)
                self.selected_square = None
                return "move"
            else:
                new_piece = self.board.piece_at(square)
                if new_piece and new_piece.color == self.board.turn:
                    self.selected_square = square
                else:
                    self.selected_square = None
        else:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square

        return None

    def is_game_over(self):
        return self.board.is_game_over()
