import random
from math import inf
from collections import OrderedDict

import othello_ai
import Othello_Core
import connect_ai


def safe_int(string):
    try:
        if string.startswith('0x'):
            return int(string[2:], 16)
        elif string.startswith('0b'):
            return int(string[2:], 2)
        else:
            return int(string)
    except ValueError:
        out = 0
        for x in string:
            out ^= ord(x)
        return out


def safe_float(string):
    try:
        return float(string)
    except ValueError:
        return random.random()


class Game(object):
    max_players = 2
    min_players = 2
    def __init__(self, user):
        self.uid = user.id

    def make_move(self, move):
        pass

    def repr_game_state(self):
        pass

    def calculate_best_move(self):
        pass

    def __hash__(self):
        return int(self.uid)

class GoFish(Game):
    max_players = 10
    def __init__(self, user, db):
        super().__init__(user)

        


class Othello(Game):
    def __init__(self, user, db):
        super().__init__(user)

        self.my_color = Othello_Core.BLACK
        self.player_color = Othello_Core.WHITE
        self.next_player = self.player_color
        self.core = othello_ai.Strategy()
        self.board = self.core.initial_board()
        self.gametype = "othello"
        self.tMatrix = othello_ai.load_matrix('nmatrix.pkl')

        self.inv_rows = dict(enumerate('_abcdefgh'))
        self.good_rows = {v: k for k, v in self.inv_rows.items()}

        self.db = db

    def make_move(self, move):
        if len(move) != 2:
            return "Move should be a 2 character string"
        pt1 = move[0]
        pt2 = move[1]
        if pt1.isdigit() and pt1 != '0' and pt2.isalpha() and pt2 in self.good_rows:
            move = int(pt1)*10+self.good_rows[pt2]
        elif pt2.isdigit() and pt2 != '0' and pt1.isalpha() and pt1 in self.good_rows:
            move = int(pt2)*10+self.good_rows[pt1]
        else:
            return "Move has invalid format, should look like `1a` or `a1`"
        good_move = self.core.make_move(move, self.next_player, self.board)
        if not good_move:
            return "Move invalid, please go again"
        self.next_player = self.core.next_player(self.board, self.next_player)
        return False

    def repr_game_state(self):
        return OrderedDict([
            ("Board", "```" + self.core.print_board(self.board) + "```"),
            ("Score", f"{self.board.count(self.my_color)} ({self.my_color}, me) - {self.board.count(self.player_color)} ({self.player_color}, you)"),
            ("Next to move", "You" if self.next_player == self.player_color else "Me")
        ])

    def calculate_best_move(self):
        board = self.board
        player = self.next_player
        tDict = {}
        spots_left = set(x for x in othello_ai.sq if board[x] == Othello_Core.EMPTY)
        startnode = [0, board, player, spots_left, [], None,
                     othello_ai.find_all_brackets(board, player, spots_left, self.core), -1, -1,
                     player + ''.join(board)]

        depth = safe_int(self.db[self.uid, self.gametype, 'ai_depth'])

        best_move = othello_ai.abprune(startnode, self.core, 0, depth, self.tMatrix, -inf, inf, player, tDict)[1]

        return str(best_move // 10)+self.inv_rows[best_move % 10]

class Connect(Game):
    def __init__(self, user, db):
        super().__init__(user)

        self.db = db
        self.gametype = "connect"
        game = connect_ai.Game(None)

        game.BOARD_W = safe_int(self.db[self.uid, self.gametype, 'width'])
        if game.BOARD_W < 1:
            game.BOARD_W = 9

        game.BOARD_H = safe_int(self.db[self.uid, self.gametype, 'height'])
        if game.BOARD_H < 1:
            game.BOARD_H = 6

        game.reset()
        self.game = game

        self.my_color = 'X'
        self.player_color = 'O'
        self.next_player = self.player_color

    def make_move(self, move):
        move = safe_int(move)-1
        if 0 <= move < self.game.BOARD_W and self.game.next_height[move] >= 0:
            self.game.place_update(move, self.next_player)
            self.next_player = 'XO'[self.next_player == 'X']

            win = connect_ai.check_win(self.game)
            if win:
                self.next_player = None
                if win == self.my_color:
                    return "I won!"
                elif win == self.player_color:
                    return "You won!"
                else:  # win == "T"
                    return "Tie!"

            return False
        else:
            return f"Move {move} is invalid, please go again"

    def repr_game_state(self):
        return OrderedDict([
            ("Board", "```"+str(self.game)+"\n"+"".join(str(x+1).ljust(2) for x in range(self.game.BOARD_W))+"```"),
            ("Next to move", "You" if self.next_player == self.player_color else "Me")
        ])

    def calculate_best_move(self):
        depth = safe_int(self.db[self.uid, self.gametype, 'ai_depth'])
        if 1 > depth or self.game.BOARD_H*self.game.BOARD_W < depth:
            depth = 4
        best_outcome, col = self.game.minimax('XO'[self.next_player == 'X'], 0, depth)

        return str(col+1)
