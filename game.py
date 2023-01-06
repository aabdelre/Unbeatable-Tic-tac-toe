import copy, time, pygame, sys, numpy as np

WIDTH, HEIGHT = 600, 600
SIZE = (WIDTH, HEIGHT)
LINE_WIDTH = 8
SQ_SIZE = WIDTH // 3
BG_COLOR = (20, 170, 156)
LINE_COLOR = (23, 145, 135)
X_COLOR = (66, 66, 66)
O_COLOR = (239, 231, 200)
WHITE = (255, 255, 255)

def switch_truns(turn):
    assert turn in ['X', 'O']
    return 'X' if turn == 'O' else 'O'

class GameMove():
    def __init__(self, r : int, c : int, player):
        self.pair = (r, c)
        self.player = player
    
    def __str__(self) -> str:
        return "{} placing at {}".format(self.player, self.pair)
    
    def __repr__(self) -> str:
        return "({} {})".format(self.pair[0], self.pair[1])

    def __eq__(self, other):
        return self.pair == other.pair and self.player == other.player
    
    def __hash__(self):
        return hash(self.__str__())

class GameState():
    def __init__(self, current = 'X', default_board = [['E'] * 3 for _ in range(3)]):
        self.board = default_board
        self.current = current
        self.move_number = 0
        self.last_move = None

    def full_board(self):
        for row in self.board:
            for entry in row:
                if entry == 'E':
                    return False
        return True
    
    def empty_sq(self, row, col):
        return self.board[row][col] == 'E'

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
            if result:
                return result
        result = self.check_digonal()
        return result if result else 'd' if self.full_board() else 'n'
        
    def game_over(self):
        return self.available_moves() == [] or self.evaluate() != 'n'

    def board_empty(self):
        return len(self.available_moves()) == 9

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

    SECONDS_PER_PLAYER = 50.0

    def __init__(self, x, o, screen, x_name = 'X', o_name = 'O', verbose = True, lose_when_out_of_time = False):
        self.x_player = x
        self.o_player = o
        self.verbose = verbose

        self.x_name = x_name
        self.o_name = o_name

        self.x_time = TicTacToeGame.SECONDS_PER_PLAYER
        self.o_time = TicTacToeGame.SECONDS_PER_PLAYER

        self.lose_when_out_of_time = lose_when_out_of_time
        self.board = GameState()
        self.screen = screen

    def log(self, *args):
        if self.verbose:
            print(*args)

    def draw_board(self, screen):
        tile_size = WIDTH / 3
        tile_origin = (0, 0)
        tiles = []
        moveFont = pygame.font.Font(None, 60)
        for i in range(3):
            row = []
            for j in range(3):
                rect = pygame.Rect(
                    tile_origin[0] + j * tile_size,
                    tile_origin[1] + i * tile_size,
                    tile_size, tile_size
                )
                pygame.draw.rect(self.screen, LINE_COLOR, rect, 3)

                if self.board.board[i][j] != 'E':
                    color = X_COLOR if self.board.board[i][j] == 'X' else O_COLOR
                    move = moveFont.render(self.board.board[i][j], True, color)
                    moveRect = move.get_rect()
                    moveRect.center = rect.center
                    screen.blit(move, moveRect)
                row.append(rect)
            tiles.append(row)
    
    def show_wins(self, screen):
        ### Horixontal wins
        for row in range(3):
            if self.board.board[row][0] == self.board.board[row][1] == self.board.board[row][2] != 'E':
                color = X_COLOR if self.board.board[row][0] == 'X' else O_COLOR
                iPos = (20, row * SQ_SIZE + SQ_SIZE // 2)
                fPos = (WIDTH - 20, row * SQ_SIZE + SQ_SIZE // 2)
                pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
        
        ### Vertical wins
        for col in range(3):
            if self.board.board[0][col] == self.board.board[1][col] == self.board.board[2][col] != 'E':
                color = X_COLOR if self.board.board[0][col] == 'X' else O_COLOR
                iPos = (col * SQ_SIZE + SQ_SIZE // 2, 20)
                fPos = (col * SQ_SIZE + SQ_SIZE // 2, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
        
        ### Main diagonal
        if self.board.board[0][0] == self.board.board[1][1] == self.board.board[2][2] != 'E':
            color = X_COLOR if self.board.board[0][0] == 'X' else O_COLOR
            iPos = (20, 20)
            fPos = (WIDTH - 20, HEIGHT - 20)
            pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)

        ### Reverse diagonal
        if self.board.board[2][0] == self.board.board[1][1] == self.board.board[0][2] != 'E':
            color = X_COLOR if self.board.board[2][0] == 'X' else O_COLOR
            iPos = (20, HEIGHT - 20)
            fPos = (WIDTH - 20, 20)
            pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)

        self.draw_board(self.screen)
        pygame.display.update()

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

        while True:
            user_click = None

            if self.board.current == 'X':
                player = self.x_player
                time_left = self.x_time
            else:
                player = self.o_player
                time_left = self.o_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    row, col = event.pos
                    row, col = col, row
                    row //= SQ_SIZE
                    col //= SQ_SIZE
                    if self.board.empty_sq(row, col):
                        user_click = (row, col)
                        
            self.draw_board(self.screen)
            pygame.display.update()
        
            start_time = time.time()
            if user_click != None or str(player) != "Human Player":
                move = player.make_move(self.board, time_left, user_click) ### Need to implement a player class

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

            if self.board.game_over():
                self.draw_board(self.screen)
                self.show_wins(self.screen)
                pygame.display.update()
                break

        winner = self.board.winner() 
        res = "Winner is " + winner + '!' if winner != 'draw' else "It's a Tie!"
        self.log(res)
        time.sleep(2)
        return self.board.winner()