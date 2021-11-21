import random
import string
from copy import deepcopy
from itertools import chain
from operator import attrgetter


class Player:
    """ Erzeugt für jeden Würfel ein eindeutig identifizierbares Spieler-Objekt
    dem vier Spielfiguren zugeordnet werden.
    """
    counter = 1

    def __init__(self, dice):
        self.id = Player.counter
        self.dice = dice
        self.games_played = 0
        self.wins = 0
        self.draws = 0
        self.pawn_list = []
        for _ in range(4):
            new_pawn = Pawn(owner=self)
            self.pawn_list.append(new_pawn)
        Player.counter += 1

    def roll_dice(self):
        return random.choice(self.dice)

    def __repr__(self):
        return f'\"Player {self.id} (d{len(self.dice)})\"'


class Pawn:
    """ Erzeugt für jedes Spieler-Objekt vier eindeutig identifizierbare Spielfiguren-Objekte
    (z.B. 1a, 1b, 1c, 1d)
    """
    counter = 1
    previous_owner = None

    def __init__(self, owner):
        self.id = ''
        self.owner = owner
        self.moves_to_goal = 100  # set to 39 with activate_pawn
        self.position = None
        self.set_id()

    def set_id(self):
        if self.owner is Pawn.previous_owner:
            Pawn.counter += 1
        else:
            Pawn.counter = 1
        Pawn.previous_owner = self.owner
        self.id = string.ascii_lowercase[Pawn.counter - 1]

    def __repr__(self):
        return f'{self.owner.id}{self.id}'


class Game:
    """ Erzeugt ein 'Mensch-ärgere-dich-nicht' Spiel für zwei Spieler.
    Das Model des Spielfelds besteht aus Start/B-Feldern (base), den Lauffeldern (board) und den Zielfeldern (goal).
    """
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p1.startpos = 0
        self.p1.endpos = 39
        self.p1.goal = [None] * 4
        self.p2 = p2
        self.p2.startpos = 20
        self.p2.endpos = 19
        self.p2.goal = [None] * 4
        self.base = []
        self.board = [None] * 40
        self.round = 1
        self.winner = None
        self.recursion_terminator = dict()

        for pawn in chain(self.p1.pawn_list, self.p2.pawn_list):
            self.base.append(pawn)
        self.activate_pawn(self.p1)
        self.activate_pawn(self.p2)

    def play_round(self):
        print(f'======== ROUND {self.round} ===========')
        for player in [self.p1, self.p2]:
            self.one_turn(player)
            if self.winner:
                return
        self.round += 1
        print_board(self)

    def one_turn(self, player):
        roll = player.roll_dice()
        print(f'++ {player} rolls', roll)

        while roll == 6:
            if self.has_pawn_in_base(player):
                if self.is_position_blocked(player.startpos):
                    self.clear_position(player, roll, player.startpos)
                else:
                    self.activate_pawn(player)
            else:
                self.move_pawn_on_board(player, roll)
            roll = player.roll_dice()
            print(f'++ {player} rolls', roll)

        self.move_pawn_on_board(player, roll)

        if None not in player.goal:
            self.winner = player

    def is_position_blocked(self, position):
        if self.board[position]:
            return True
        return False

    def clear_position(self, player, roll, position):
        print(f'-- Clearing position [{position}]...')

        # Bei manchen Würfeln bleiben die letzten beiden Spielfiguren for dem vollen Ziel stecken
        if self.recursion_terminator.get(self.round):
            if self.recursion_terminator[self.round] > 5:
                print(f'-- Terminated recursion...')
                return
            self.recursion_terminator[self.round] += 1
        else:
            self.recursion_terminator[self.round] = 1
        print(self.recursion_terminator)

        pawn = self.board[position]
        if pawn.owner is player:
            self.move_pawn_on_board(player, roll, pawn=pawn)
        else:
            self.throw_out_pawn(pawn)
            if position == player.startpos:
                self.activate_pawn(player)
            else:
                self.move_pawn_on_board(player, roll)

    def select_pawn_to_move(self, pawn_list):
        return

    def move_pawn_on_board(self, player, roll, pawn=None):
        if pawn in self.base:
            return
        pawns_on_board = [p for p in player.pawn_list if p not in self.base]
        if pawns_on_board:
            if not pawn:
                pawn = min(pawns_on_board, key=attrgetter('moves_to_goal'))
            if pawn in player.goal:
                self.move_pawn_within_goal(player, roll)
                return
        else:
            return
        idx = self.board.index(pawn)
        new_idx = idx + roll
        # Hat das Ende des modellierten Spielfelds erreicht
        if self.is_end_of_board(new_idx):
            new_idx = new_idx - len(self.board)  # 36 + 5 = 41 > [1]; 41 - 40 = 1
        # Hat die Zielfelder erreicht
        if roll > pawn.moves_to_goal:  # Feld vor dem Zielfeld == 0
            success = self.move_pawn_into_goal(pawn, roll, player)
            if not success:
                alt_pawn = sorted(player.pawn_list, key=attrgetter('moves_to_goal'))[1]
                print(f'-- Selected alternativ pawn {alt_pawn}')
                if pawn is alt_pawn or alt_pawn in player.goal:
                    return
                self.move_pawn_on_board(player, roll, pawn=alt_pawn)
        else:
            if self.is_position_blocked(new_idx):
                self.clear_position(player, roll, new_idx)
            else:
                self.board[idx] = None
                self.board[new_idx] = pawn
                pawn.moves_to_goal -= roll
                print(f'-- Moving {pawn} by {roll}. To goal: {pawn.moves_to_goal}')

    def throw_out_pawn(self, pawn):
        idx = self.board.index(pawn)
        self.board[idx] = None
        self.base.append(pawn)
        pawn.moves_to_goal = 100
        print('-- Threw out', pawn)

    def has_pawn_in_base(self, player):
        for pawn in player.pawn_list:
            if pawn in self.base:
                return True
        return False

    def activate_pawn(self, player):
        for pawn in player.pawn_list:
            if pawn in self.base:
                self.base.remove(pawn)
                pawn.moves_to_goal = 39
                self.board[player.startpos] = pawn
                print('-- activated', pawn)
                return

    def is_end_of_board(self, position):
        if position > (len(self.board) - 1):
            return True
        return False

    def move_pawn_into_goal(self, pawn, roll, player):
        moves_in_goal = roll - pawn.moves_to_goal
        if moves_in_goal > 4:
            print(f'-- {pawn} cannot move into goal: Roll too high')
            return False
        idx_board = self.board.index(pawn)
        idx_goal = moves_in_goal - 1
        if player.goal[idx_goal]:
            print(f'-- {pawn} cannot move into goal: goal[{idx_goal}] blocked')
            success = self.move_pawn_within_goal(player, roll)
            if success:
                print(f'-- Moved pawns within goal instead')
                return True
            return False
        self.board[idx_board] = None
        pawn.moves_to_goal = 100 + idx_goal
        player.goal[idx_goal] = pawn
        print(f'-- Moving {pawn} into goal[{idx_goal}]')
        return True

    def move_pawn_within_goal(self, player, roll):
        if roll > 3:
            return False
        for idx, element in enumerate(player.goal):
            if element is not None:
                # element ist Spielfigur
                if idx in [0, 1, 2]:
                    try:
                        if not player.goal[idx+roll]:
                            player.goal[idx] = None
                            player.goal[idx+roll] = element
                            return True
                    except IndexError:
                        pass
                if idx in [1, 2, 3]:
                    try:
                        if not player.goal[idx-roll]:
                            player.goal[idx] = None
                            player.goal[idx-roll] = element
                            return True
                    except IndexError:
                        pass
        return False


def print_board(game):
    p1 = ['__'] * 4
    p2 = ['__'] * 4
    for idx, p in zip(range(4), game.p1.pawn_list):
        p1[idx] = p if p in game.base else '__'
    for idx, p in zip(range(4), game.p2.pawn_list):
        p2[idx] = p if p in game.base else '__'

    g1 = ['..'] * 4
    g2 = ['..'] * 4
    for idx, p in enumerate(game.p1.goal):
        g1[idx] = p if p is not None else '..'
    for idx, p in enumerate(game.p2.goal):
        g2[idx] = p if p is not None else '..'

    b = deepcopy(game.board)
    for idx, dot in enumerate(b):
        if dot is None:
            b[idx] = '__'
        else:
            b[idx] = dot

    print(f'            {b[38]} {b[39]} {b[0]}       {p1[0]} {p1[1]}')
    print(f'            {b[37]} {g1[0]} {b[1]}       {p1[2]} {p1[3]}')
    print(f'            {b[36]} {g1[1]} {b[2]}')
    print(f'            {b[35]} {g1[2]} {b[3]}')
    print(f'{b[30]} {b[31]} {b[32]} {b[33]} {b[34]} {g1[3]} {b[4]} {b[5]} {b[6]} {b[7]} {b[8]}')
    print(f'{b[29]}                            {b[9]}')
    print(f'{b[28]} {b[27]} {b[26]} {b[25]} {b[24]} {g2[3]} {b[14]} {b[13]} {b[12]} {b[11]} {b[10]}')
    print(f'            {b[23]} {g2[2]} {b[15]}')
    print(f'            {b[22]} {g2[1]} {b[16]}')
    print(f'{p2[0]} {p2[1]}       {b[21]} {g2[0]} {b[17]}')
    print(f'{p2[2]} {p2[3]}       {b[20]} {b[19]} {b[18]}')
    print()
