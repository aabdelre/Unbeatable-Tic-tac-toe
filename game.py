import copy, random, numpy as np

def switch_truns(turn):
    """Returns the other color"""
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
    def __init__(self, test_board = [['E'] * 3 for _ in range(3)]):
        self.board = test_board #[['E'] * 3 for _ in range(3)]
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
    
def main():
    #move = GameMove(1, 1, 'X')
    #print(move)
    test_board = [['X', 'X', 'X'],
                  ['E', 'O', 'X'],
                  ['X', 'O', 'E']]
    game = GameState(test_board)
    print(game)
    move = random.choice(game.available_moves())
    print(move)
    game = game.apply_move(move)
    print(game)
    #print(game.winner())

if __name__ == "__main__":
    main()
