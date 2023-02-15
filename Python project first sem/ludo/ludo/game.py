from collections import namedtuple, deque
import random
from .painter import PaintBoard
Pawn = namedtuple("Pawn", "index colour id")
class Player():
    def __init__(self, colour, name=None, choose_pawn_delegate=None):  
        self.colour = colour
        self.choose_pawn_delegate = choose_pawn_delegate
        self.name = name
        if self.name is None and self.choose_pawn_delegate is None:
            self.name = "computer"
        self.finished = False
        self.pawns = [Pawn(i, colour, colour[0].upper() + str(i)) for i in range(1, 5)]

    def __str__(self):                                            
        return "{}({})".format(self.name, self.colour)

    def choose_pawn(self, pawns):   
        if len(pawns) == 1:
            index = 0
        elif len(pawns) > 1:
            if self.choose_pawn_delegate is None:
                index = random.randint(0, len(pawns) - 1)
            else:
                index = self.choose_pawn_delegate()
        return index


class Board():
    bs = 56                    
    Colorpos = 7             
    corder = ['yellow', 'blue', 'red', 'green']
    quarter = 14   
    def __init__(self):
        Board.COLOUR_START = {colour: 1 + index * Board.quarter for index, colour in enumerate(Board.corder)}       
        Board.COLOUR_END = {
            colour: index * Board.quarter
            for index, colour in enumerate(Board.corder)}
        Board.COLOUR_END['yellow'] = Board.bs
        self.pawns_possiotion = {}
        self.painter = PaintBoard()
        self.board_pool_position = (0, 0)

    def set_pawn(self, pawn, position):
        self.pawns_possiotion[pawn] = position

    def put_pawn_on_board_pool(self, pawn):
        self.set_pawn(pawn, self.board_pool_position)

    def is_pawn_on_board_pool(self, pawn):
        return self.pawns_possiotion[pawn] == self.board_pool_position

    def put_pawn_on_starting_square(self, pawn):
        start = Board.COLOUR_START[pawn.colour.lower()]
        position = (start, 0)
        self.set_pawn(pawn, position)

    def can_pawn_move(self, pawn, rolled_value):
        common_poss, private_poss = self.pawns_possiotion[pawn]
        if private_poss + rolled_value > self.Colorpos:
            return False
        return True

    def move_pawn(self, pawn, rolled_value):
        common_poss, private_poss = self.pawns_possiotion[pawn]
        end = self.COLOUR_END[pawn.colour.lower()]
        if private_poss > 0:
            private_poss += rolled_value
        elif common_poss <= end and common_poss + rolled_value > end:
            private_poss += rolled_value - (end - common_poss)
            common_poss = end
        else:
            common_poss += rolled_value
            if common_poss > self.bs:
                common_poss = common_poss - self.bs
        position = common_poss, private_poss
        self.set_pawn(pawn, position)

    def does_pawn_reach_end(self, pawn):
        common_poss, private_poss = self.pawns_possiotion[pawn]
        if private_poss == self.Colorpos:
            return True
        return False

    def get_pawns_on_same_postion(self, pawn):
        position = self.pawns_possiotion[pawn]
        return [curr_pawn for curr_pawn, curr_postion in self.pawns_possiotion.items() if position == curr_postion]

    def paint_board(self):
        positions = {}
        for pawn, position in self.pawns_possiotion.items():
            common, private = position
            if not private == Board.Colorpos:
                positions.setdefault(position, []).append(pawn)
        return self.painter.paint(positions)


class Die():
    MIN = 1
    MAX = 6
    @staticmethod
    def throw():
        return random.randint(Die.MIN, Die.MAX)


class Game():
    def __init__(self):
        self.players = deque()              
        self.standing = []
        self.board = Board()
        self.finished = False
        self.rolled_value = None
        self.curr_player = None
        self.allowed_pawns = []
        self.picked_pawn = None
        self.index = None
        self.jog_pawns = []

    def add_palyer(self, player):
        self.players.append(player)
        for pawn in player.pawns:
            self.board.put_pawn_on_board_pool(pawn)

    def get_available_colours(self):
        used = [player.colour for player in self.players]
        available = set(self.board.corder) - set(used)
        return sorted(available)

    def _get_next_turn(self):
        if not self.rolled_value == Die.MAX:
            self.players.rotate(-1)
        return self.players[0]

    def get_pawn_from_board_pool(self, player):
        for pawn in player.pawns:
            if self.board.is_pawn_on_board_pool(pawn):
                return pawn

    def get_allowed_pawns_to_move(self, player, rolled_value):
        allowed_pawns = []
        if rolled_value == Die.MAX:
            pawn = self.get_pawn_from_board_pool(player)
            if pawn:
                allowed_pawns.append(pawn)
        for pawn in player.pawns:
            if not self.board.is_pawn_on_board_pool(pawn) and\
                    self.board.can_pawn_move(pawn, rolled_value):
                allowed_pawns.append(pawn)
        return sorted(allowed_pawns, key=lambda pawn: pawn.index)

    def get_board_pic(self):
        return self.board.paint_board()

    def _jog_foreign_pawn(self, pawn):
        pawns = self.board.get_pawns_on_same_postion(pawn)
        for p in pawns:
            if p.colour != pawn.colour:
                self.board.put_pawn_on_board_pool(p)
                self.jog_pawns.append(p)

    def _make_move(self, player, pawn):
        if self.rolled_value == Die.MAX and\
                self.board.is_pawn_on_board_pool(pawn):
            self.board.put_pawn_on_starting_square(pawn)
            self._jog_foreign_pawn(pawn)
            return
        self.board.move_pawn(pawn, self.rolled_value)
        if self.board.does_pawn_reach_end(pawn):
            player.pawns.remove(pawn)
            if not player.pawns:
                self.standing.append(player)
                self.players.remove(player)
                if len(self.players) == 1:
                    self.standing.extend(self.players)
                    self.finished = True
        else:
            self._jog_foreign_pawn(pawn)

    def play_turn(self, ind=None, rolled_val=None):
        self.jog_pawns = []
        self.curr_player = self._get_next_turn()
        if rolled_val is None:
            self.rolled_value = Die.throw()
        else:
            self.rolled_value = rolled_val
        self.allowed_pawns = self.get_allowed_pawns_to_move(
            self.curr_player, self.rolled_value)
        if self.allowed_pawns:
            if ind is None:
                self.index = self.curr_player.choose_pawn(
                    self.allowed_pawns)
            else:
                self.index = ind
            self.picked_pawn = self.allowed_pawns[self.index]
            self._make_move(self.curr_player, self.picked_pawn)
        else:
            self.index = -1
            self.picked_pawn = None
