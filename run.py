import random
from game import *

class RandomPlayer():
    def __init__(self, turn):
        assert turn in ['X', 'O']
        self.turn = turn
    
    def __str__(self):
        return "Random Player"
    
    def make_move(self, state, remaining_time, user_click):
        available = state.available_moves()
        return random.choice(available)   

class HumanPlayer():
    def __init__(self, turn):
        assert turn in ['X', 'O']
        self.turn = turn

    def __str__(self):
        return "Human Player"

    def make_move(self, state, remaining_time, user_click):
        available = state.available_moves()
        print("----- {}'s turn -----".format(state.current))
        print("Remaining time: {:0.2f}".format(remaining_time))
        print("Available Moves are:", available)
        #move = input("What's your move in 'r, c': ").split(',')
        move = user_click
        
        move = GameMove(move[0], move[1], state.current)
        if move in available:
            print(move)
            return move

class SearchNode():
    def __init__(self, state, depth, move):
        self.game_state = state
        self.depth = depth
        self.move = move

    def is_terminal(self):
        return self.game_state.game_over()

    def utility2(self, turn):
        if self.game_state.winner() == turn:
            return sys.maxsize
        elif self.game_state.winner() == switch_truns(turn):
            return -sys.maxsize
        else:
            return 0

    def utility(self, turn):
        if self.game_state.winner() == turn:
            return sys.maxsize
        elif self.game_state.winner() == switch_truns(turn):
            return -sys.maxsize
        elif self.game_state.winner() == 'd':
            return 0
        else:
            value = 0
            ### 3 Rows
            turn_incrementer = 1
            opp_turn_incrementer = 1
            for row in self.game_state.board:
                for entry in row:
                    turn_incrementer *= 10 if entry == turn else turn_incrementer
                    opp_turn_incrementer *= 10 if entry == switch_truns(turn) else opp_turn_incrementer
                value += (turn_incrementer - opp_turn_incrementer)
                turn_incrementer = 1
                opp_turn_incrementer = 1
            ### 3 Columns
            transposed_board = np.transpose(self.game_state.board)
            turn_incrementer = 1
            opp_turn_incrementer = 1
            for row in transposed_board:
                for entry in row:
                    turn_incrementer *= 10 if entry == turn else turn_incrementer
                    opp_turn_incrementer *= 10 if entry == switch_truns(turn) else opp_turn_incrementer
                value += (turn_incrementer - opp_turn_incrementer)
                turn_incrementer = 1
                opp_turn_incrementer = 1
            ### Main Diagonal
            turn_incrementer = 1
            opp_turn_incrementer = 1
            diagonal = [self.game_state.board[i][i] for i in range(len(self.game_state.board))]
            for entry in diagonal:
                turn_incrementer *= 10 if entry == turn else turn_incrementer
                opp_turn_incrementer *= 10 if entry == switch_truns(turn) else opp_turn_incrementer
            value += (turn_incrementer - opp_turn_incrementer)
            # Reverse Diagonal
            turn_incrementer = 1
            opp_turn_incrementer = 1
            rev_diagonal = [self.game_state.board[i][len(self.game_state.board) - i - 1] for i in range(len(self.game_state.board))]
            for entry in rev_diagonal:
                turn_incrementer *= 10 if entry == turn else turn_incrementer
                opp_turn_incrementer *= 10 if entry == switch_truns(turn) else opp_turn_incrementer
            value += (turn_incrementer - opp_turn_incrementer)
            return value
            
class MinMaxPlayer():
    def __init__(self, turn):
        assert turn in ['X', 'O']
        self.turn = turn

    def __str__(self):
        return "MiniMax"

    def make_move(self, state, remaining_time, user_click):
        node = SearchNode(state, 0, None)
        best = self.minimax(node, 9, node.game_state.current)
        #print(best)
        #best[1].player = state.current
        return best[1]
    
    def minimax(self, node, depth, player):
        if node.is_terminal():
            return (node.utility2(self.turn), None)

        if player == self.turn:
            #print("Max playing")
            best = (-sys.maxsize, None)
            moves = node.game_state.available_moves()
            for move in moves:
                new_state = node.game_state.apply_move(move)
                new_node = SearchNode(new_state, node.depth + 1, move)
                #print(best, possible_move)
                eval = self.minimax(new_node, depth - 1, switch_truns(player))[0]
                if eval > best[0]:
                    best = (eval, move)            
            return best

        else:
            #print("Min playing")
            best = (sys.maxsize, None)
            moves = node.game_state.available_moves()
            for move in moves:
                new_state = node.game_state.apply_move(move)
                new_node = SearchNode(new_state, node.depth + 1, move)
                eval = self.minimax(new_node, depth - 1, switch_truns(player))[0]
                if eval < best[0]:
                    best = (eval, move)
            return best

def main():
    player1, player2 = sys.argv[1], sys.argv[2]
    player1 = MinMaxPlayer('X') if player1 == 'm' else HumanPlayer('X') if player1 == 'h' else RandomPlayer('X')
    player2 = MinMaxPlayer('O') if player2 == 'm' else HumanPlayer('O') if player2 == 'h' else RandomPlayer('O')

    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    screen.fill(BG_COLOR)
    pygame.display.set_caption("TIC-TAC-TOE")
    img = pygame.image.load('tic-tac-toe.png')
    pygame.display.set_icon(img)

    game = TicTacToeGame(player1, player2, screen,
                        x_name = str(player1), o_name = str(player2),
                        verbose = True,
                        lose_when_out_of_time = False)

    game.play_game()
    
if __name__ == "__main__":
    main()