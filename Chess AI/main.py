import chess
import chess.polyglot
from trans_table import TranspositionTable as tbl
# import logging
# from chess.engine import PlayResult, Limit
# import random
# # from lib.engine_wrapper import MinimalEngine, MOVE
# from typing import Any
# logger = logging.getLogger(__name__)

class daxattack:

    def __init__(self, board):
        self.board=chess.Board()
        self.board.starting_fen=board
        self.message=''
        self.depth=3
        self.best_eval=0
        self.piece_tables = {
            chess.PAWN: [
                0, 0, 0, 0, 0, 0, 0, 0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5, 5, 10, 25, 25, 10, 5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, -5, -10, 0, 0, -10, -5, 5,
                5, 10, 10, -20, -20, 10, 10, 5,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            chess.KNIGHT: [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50
            ],
            
            chess.BISHOP: [
                -20,-10,-10,-10,-10,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -20,-10,-10,-10,-10,-10,-10,-20
            ],
            chess.ROOK: [
                0,  0,  0,  0,  0,  0,  0,  0,
                5, 10, 10, 10, 10, 10, 10,  5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                -5,  0,  0,  0,  0,  0,  0, -5,
                0,  0,  0,  5,  5,  0,  0,  0
            ],
            chess.QUEEN: [
                -20,-10,-10, -5, -5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5,  5,  5,  5,  0,-10,
                -5,  0,  5,  5,  5,  5,  0, -5,
                0,  0,  5,  5,  5,  5,  0, -5,
                -10,  5,  5,  5,  5,  5,  0,-10,
                -10,  0,  5,  0,  0,  0,  0,-10,
                -20,-10,-10, -5, -5,-10,-10,-20
            ],
            chess.KING: [
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -20,-30,-30,-40,-40,-30,-30,-20,
                -10,-20,-20,-20,-20,-20,-20,-10,
                20, 20,  0,  0,  0,  0, 20, 20,
                20, 30, 10,  0,  0, 10, 30, 20
            ],
            }
        self.opening_book = {
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": "e2e4",
                "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "e7e5",
                
            }

    def recieve_command(self, command):
        pass
    def material(self):
        white = self.board.occupied_co[chess.WHITE]
        black = self.board.occupied_co[chess.BLACK]
        return (
            50*(chess.popcount(white & self.board.pawns) - chess.popcount(black & self.board.pawns)) +
            300 * (chess.popcount(white & self.board.knights) - chess.popcount(black & self.board.knights)) +
            300 * (chess.popcount(white & self.board.bishops) - chess.popcount(black & self.board.bishops)) +
            500 * (chess.popcount(white & self.board.rooks) - chess.popcount(black & self.board.rooks)) +
            900 * (chess.popcount(white & self.board.queens) - chess.popcount(black & self.board.queens))
        )

    def best_move(self, maximizing_player: bool):
        best_move = None

        if maximizing_player:
            def func(x, y):
                return x > y
        else:
            def func(x, y):
                return x < y
        moves = str(self.board.legal_moves)
        moves=str(moves)[38:-2]
        moves=list(moves.split(', '))
        ordered_moves= self.order(moves)
        o1 = ordered_moves[:len(ordered_moves)//2]
        o2 = ordered_moves[len(ordered_moves)//2:]
        best_value = -1000000 if maximizing_player else 1000000
        for move in o1:
            if '#' in move:
                return move
            self.board.push_san(move)
            eval = self.alpha_beta_max(2, -100000000, 1000000000)
            self.board.pop()
            if "k" in move:
                eval*=(1/2)
            if func(eval, best_value):
                best_value = eval
                best_move = move
            print(move,eval)
        return best_move
    

    def alpha_beta_max(self, depth, alpha, beta):
        if depth == 0 or self.board.is_game_over():
            return (self.material() + self.evaluation())
        moves = str(self.board.legal_moves)
        moves=str(moves)[38:-2]
        moves=list(moves.split(', '))
        ordered_moves= self.order(moves)
        for move in ordered_moves:
            self.board.push_san(move) 
            score = self.alpha_beta_min(depth-1,alpha,beta)
            self.board.pop()
            if(score >= beta):
                return beta
            if(score>alpha):
                alpha = score
        return alpha

    def alpha_beta_min(self, depth, alpha, beta):
        if depth == 0 or self.board.is_game_over():
            return -(self.material() + self.evaluation())
        moves = str(self.board.legal_moves)
        moves=str(moves)[38:-2]
        moves=list(moves.split(', '))
        ordered_moves= self.order(moves)
        for move in ordered_moves:
            self.board.push_san(move) 
            score = self.alpha_beta_max(depth-1,alpha,beta)
            self.board.pop()
            if(score <= alpha):
                return alpha
            if(score<beta):
                beta = score
        return beta


    def quiescence_search(self, alpha, beta, delta):
        stand_pat = (self.evaluation() + self.material())  # Evaluate the current position
        if stand_pat >= beta:
            return beta

        if stand_pat > alpha:
            alpha = stand_pat
        moves = str(self.board.legal_moves)
        moves=str(moves)[38:-2]
        moves=list(moves.split(', '))
        ordered_moves=[]
        for move in moves:
            try:
                d = self.board.parse_san(move)
                if self.board.is_capture(d) or self.board.is_check():
                    ordered_moves.append(move)
            except chess.InvalidMoveError:
                pass

        # Check if there are no captures or checks, return the stand-pat score
        if ordered_moves is None:
            return stand_pat
        for move in ordered_moves:
            self.board.push_san(move)  # Make the move
            score = -self.quiescence_search(-beta, -alpha, delta)  # Recursively search the position
            self.board.pop()  # Undo the move
            if score >= beta:
                return beta

            if score > alpha:
                alpha = score
            
            if alpha >= beta - delta:
                break

        return alpha
    
    def evaluation(self):
        eval = 0
        board_state = self.board.piece_map()
        for square, piece in board_state.items():
            piece_type = piece.piece_type
            color = piece.color
            if color == chess.WHITE:
                eval += self.piece_tables[piece_type][63-square]
                # self.pos_table[square]=(self.piece_tables[piece_type][63-(square)])
            else:
                eval -= self.piece_tables[piece_type][63-chess.square_mirror(square)]
                # self.pos_table[square]=(self.piece_tables[piece_type][63-chess.square_mirror(square)])
        return eval

    def order(self, moves):
        ordered_moves = []
        for move in moves:
            d = self.board.parse_san(move)
            if self.board.is_capture(d) or self.board.is_check():
                ordered_moves.append(move)
        non_captures_and_checks = [move for move in moves if move not in ordered_moves]
        ordered_moves.extend(non_captures_and_checks)
        return ordered_moves

    
    def search(self):
        a = self.board.turn
        try:
                move = str(chess.polyglot.MemoryMappedReader("Project/baron30.bin").weighted_choice(self.board))
                move=move[-7:-3]
                # if self.board.fen() in self.opening_book:
                #     move = (self.opening_book[self.board.fen()])
                self.board.push(chess.Move.from_uci(move))
                print()
                print("Ai played",move)
                print(self.board)
                print(self.evaluation()+self.material())
          

        except KeyError:
                self.best_eval=0
                move = self.best_move(a)
                self.board.push_san(move)
                print()
                print("Ai played",move)
                print(self.board)
                print(self.evaluation()+self.material())
   
        except IndexError:
                self.best_eval=0
                move = self.best_move(a)
                self.board.push_san(move)
                print()
                print("Ai played",move)
                print(self.board)
                print(self.evaluation()+self.material())


    def prompt_user_move(self):
        while True:
            user_move = input("Enter your move in UCI format (e.g., 'e2e4'): ")
            try:
                self.board.push(chess.Move.from_uci(user_move))
                print(self.board)
                break
            except chess.InvalidMoveError:
                print("Invalid move. Try again.")
                self.play_game()
            except AssertionError: 
                print("Invalid move. Try again.")
                self.play_game()

    def Is_Endgame(self):
        self.piece_tables[chess.KING]= [-50,-40,-30,-20,-20,-30,-40,-50,
                                        -30,-20,-10,  0,  0,-10,-20,-30,
                                        -30,-10, 20, 30, 30, 20,-10,-30,
                                        -30,-10, 30, 40, 40, 30,-10,-30,
                                        -30,-10, 30, 40, 40, 30,-10,-30,
                                        -30,-10, 20, 30, 30, 20,-10,-30,
                                        -30,-30,  0,  0,  0,  0,-30,-30,
                                        -50,-30,-30,-30,-30,-30,-30,-50]
        

    def play_game(self):
        while not self.board.is_game_over():
            
            self.prompt_user_move()
            if not self.board.is_game_over():
                self.search()
            else:
                print('game over')
    
    def play_self(self):
        while not self.board.is_game_over():
            
            if not self.board.is_game_over():
                if self.board.fullmove_number>=30:
                    self.Is_Endgame()
                self.search()
            else:
                print('game over')
   



if __name__=="__main__":
    a='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    dax_attack = daxattack(a)
    dax_attack.play_game()
    
    

    