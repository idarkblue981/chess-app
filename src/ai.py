import chess
import chess.engine
from settings import STOCKFISH_PATH

class ChessAI:
    def __init__(self, elo=1400):
        """
        Inițializează motorul Stockfish și setează nivelul ELO.
        """
        try:
            # Pornim procesul Stockfish
            self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH, timeout = 20)
            
            # Configurăm Stockfish să joace la un anumit nivel ELO
            self.engine.configure({
                "UCI_LimitStrength": True,
                "UCI_Elo": elo
            })
            print(f"Robotul a pornit cu succes (ELO: {elo})")
        except Exception as e:
            print(f"Eroare critică la pornirea Stockfish: {e}")
            self.engine = None

    def get_move(self, board):
        """
        Cere robotului cea mai bună mutare pentru poziția curentă.
        """
        if self.engine and not board.is_game_over():
            # Îi dăm robotului un timp scurt de gândire (4 secunde)
            # Suficient pentru ca jocul să fie fluid
            result = self.engine.play(board, chess.engine.Limit(time=4))
            return result.move
        return None

    def quit(self):
        """
        Închide procesul Stockfish corect la finalul jocului.
        """
        if self.engine:
            self.engine.quit()