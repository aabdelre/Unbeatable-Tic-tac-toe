"""Observations: pretty hard to get a draw if two random players are matched up."""
import copy, time, random, sys, numpy as np

def switch_truns(turn):
    assert turn in ['X', 'O']
    return 'X' if turn == 'O' else 'O'

class GameMove():
    def __init__(self, r : int, c : int, player : str):
        self.pair = (r, c)
        self.player = player
    
    def __str__(self) -> str:
        return "{} placing at {}".format(self.player, self.pair)
    
    def __repr__(self) -> str:
        return "({} {})".format(self.pair[0], self.pair[1])

    def __eq__(self, other):
        return self.pair == other.pair and self.player == other.player
    
    def __hash__(self):
        return hash(self.__str__()) # Not sure if this how to do it yet

class GameState():
    def __init__(self, default_board = [['E'] * 3 for _ in range(3)]):
        self.board = default_board
        self.current = 'X'
        self.move_number = 0

    def full_board(self):
        for row in self.board:
            for entry in row:
                if entry == 'E':
                    return False
        return True
    
    def check_rows(self, board : list):
        """Takes board as a parameter since it is being transposed and stored board
        should not change."""
        for row in board:
            if len(set(row)) == 1 and row[0] != 'E':
                return row[0]
        return 0

    def check_digonal(self):
        if len(set([self.board[i][i] for i in range(len(self.board))])) == 1 and self.board[0][0] != 'E':
            return self.board[0][0]
        if len(set([self.board[i][len(self.board) - i - 1] for i in range(len(self.board))])) == 1 and self.board[0][len(self.board) - 1] != 'E':
            return self.board[0][len(self.board) - 1]
        return 0

    def evaluate(self):
        """d = draw, X = X won, Y = Y won, n = no one won yet"""
        for board in [self.board, np.transpose(self.board)]:
            result = self.check_rows(board)
            if result and result != 'E':
                return result
        #print("It's a diagonal win!")
        result = self.check_digonal()
        return result if result else 'd' if self.full_board() else 'n'
        
    def game_over(self):
        return self.available_moves() == [] or self.evaluate() != 'n'

    def winner(self):
        assert self.game_over()
        result = self.evaluate()
        return 'draw' if result == 'd' else 'X' if result == 'X' else 'O'

    def available_moves(self):
        protomoves = []
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == 'E':
                    protomoves.append((r, c))
        return [GameMove(r, c, self.current) for r, c in protomoves]

    def apply_move(self, move):
        r, c = move.pair
        assert r < 3 and c < 3 and c >= 0 and r >= 0 and self.current == move.player
        assert self.board[r][c] == 'E'

        new_state = copy.deepcopy(self)
        new_state.board[r][c] = move.player
        new_state.current = switch_truns(self.current)
        new_state.move_number += 1
        return new_state

    def __str__(self):
        res =  "    0   1   2  \n"
        res += "  +---+---+---+\n"
        for r in range(3):
            res += "{} |".format(r)
            for c in range(3):
                col = self.board[r][c]
                res += '   |' if col == 'E' else \
                       ' X |' if col == 'X' else \
                       ' O |'
            res += '\n'
            res += "  +---+---+---+\n"
        res += "==== STATUS ====\n"
        res += "Current Player: {}\n".format(self.current)
        return res
    
class TicTacToeGame():

    SECONDS_PER_PLAYER = 30.0

    def __init__(self, x, o, x_name = "X", o_name = "O", verbose = True, lose_when_out_of_time = False):
        self.x_player = x
        self.o_player = o
        self.verbose = verbose

        self.x_name = x_name
        self.o_name = o_name

        self.x_time = TicTacToeGame.SECONDS_PER_PLAYER
        self.o_time = TicTacToeGame.SECONDS_PER_PLAYER

        self.lose_when_out_of_time = lose_when_out_of_time
        self.board = GameState()

    def log(self, *args):
        if self.verbose:
            print(*args)

    def log_state(self):
        self.log(self.board)
        self.log("X Agent:", self.x_name)
        self.log("O Agent:", self.o_name)
        self.log("X Time: {:0.2f}".format(self.x_time))
        self.log("O Time: {:0.2f}".format(self.o_time))
        self.log("====================================")

    def play_game(self):

        self.log("_" * 40)
        self.log("X Agent:", self.x_name)
        self.log("O Agent:", self.o_name)
        self.log("_" * 40)
        self.log_state()

        while not self.board.game_over():
            if self.board.current == 'X':
                player = self.x_player
                time_left = self.x_time
            else:
                player = self.o_player
                time_left = self.o_time
        
            start_time = time.time()
            move = player.make_move(self.board, time_left) ### Need to implement a player class

            end_time = time.time()
            move_time = end_time - start_time

            if self.board.current == 'X':
                self.x_time -= move_time
            else:
                self.o_time -= move_time

            if self.lose_when_out_of_time and (self.x_time < 0 or self.o_time < 0):
                self.log("\n{}. {}".format(self.board.move_number, move))
                self.log_state()

                self.log("{} timed out!".format(self.board.current))
                self.log("Winner is", switch_truns(self.board.current))

                return switch_truns(self.board.current)[0] + "time"
        
            self.board = self.board.apply_move(move)
            self.log("\n{}. {}".format(self.board.move_number, move))
            self.log_state()

        self.log("Winner is", self.board.winner())
        return self.board.winner()

class RandomPlayer():
    def __init__(self, turn):
        assert turn in ['X', 'O']
        self.turn = turn
    
    def __str__(self):
        return "Random Player"
    
    def make_move(self, state, remaining_time):
        available = state.available_moves()
        return random.choice(available)   

class HumanPlayer():
    def __init__(self, turn):
        assert turn in ['X', 'O']
        self.turn = turn

    def __str__(self):
        return "Human Player"

    def make_move(self, state, remaining_time):
        available = state.available_moves()
        print("----- {}'s turn -----".format(state.current))
        print("Remaining time: {:0.2f}".format(remaining_time))
        print("Available Moves are:", available)
        move = input("What's your move in 'r, c': ").split(',')
        move = GameMove(int(move[0]), int(move[1]), state.current)
        if move in available:
            return move

class SearchNode():
    def __init__(self, state, depth, move):
        self.game_state = state
        self.depth = depth
        self.move = move

    def is_terminal(self):
        return self.game_state.game_over()

    def utility(self, turn):
        value = 0
        turn_incrementer = 1
        opp_turn_incrementer = 1
        for row in self.game_state.board:
            for entry in row:
                turn_incrementer *= 10 if entry == turn else turn_incrementer
                opp_turn_incrementer *= 10 if entry == turn else opp_turn_incrementer
            turn_incrementer = 1
            opp_turn_incrementer = 1
            value += turn_incrementer - opp_turn_incrementer

        turn_incrementer = 1
        opp_turn_incrementer = 1
        diagonal = [self.game_state.board[i][i] for i in range(len(self.game_state.board))]
        for entry in diagonal:
            turn_incrementer *= 10 if entry == turn else turn_incrementer
            opp_turn_incrementer *= 10 if entry == turn else opp_turn_incrementer
        value += turn_incrementer - opp_turn_incrementer

        turn_incrementer = 1
        opp_turn_incrementer = 1
        rev_diagonal = [self.game_state.board[i][len(self.game_state.board) - i - 1] for i in range(len(self.game_state.board))]
        for entry in rev_diagonal:
            turn_incrementer *= 10 if entry == turn else turn_incrementer
            opp_turn_incrementer *= 10 if entry == turn else opp_turn_incrementer
        value += turn_incrementer - opp_turn_incrementer
        return value
    
class MinMaxPlayer():
    def __init__(self, turn):
        assert turn in ["X", "O"]
        self.turn = turn

    def __str__(self):
        return "MiniMax"

    def make_move(self, state, remaining_time):
        node = SearchNode(state, 0, (None, None))
        return self.minimax(node, 7, node.game_state.current)[1]
    
    def minimax(self, node, depth, player):
        if depth == 0 or node.is_terminal():
            return (node.utility(self.turn), None)

        if player == self.turn:
            best = (-sys.maxsize, None)
            for move in node.game_state.available_moves():
                new_state = node.game_state.apply_move(move)
                new_node = SearchNode(new_state, node.depth + 1, move)
                best = (max(best[0], self.minimax(new_node, depth - 1, switch_truns(node.game_state.current))[0]), move)
            return best
    
        else:
            best = (sys.maxsize, None)
            for move in node.game_state.available_moves():
                new_state = node.game_state.apply_move(move)
                new_node = SearchNode(new_state, node.depth + 1, move)
                best = (min(best[0], self.minimax(new_node, depth - 1, switch_truns(node.game_state.current))[0]), move)
            return best

def main():
    #move = GameMove(1, 1, 'X')
    #print(move)
    #test_board = [['X', 'X', 'X'],
    #              ['E', 'O', 'X'],
    #              ['X', 'O', 'E']]
    game = TicTacToeGame(RandomPlayer('X'), MinMaxPlayer('O'),
                        x_name = "Random X", o_name = "Random O",
                        verbose = True,
                        lose_when_out_of_time = True)
    
    winner = game.play_game()

if __name__ == "__main__":
    main()
