"""
SPIELREGELN (AUSZUG):

Jeder Spieler erhält vier Steine seiner Farbe.
Einen Stein stellt er auf das Feld A seiner Farbe, die übrigen drei werden auf die gleichfarbigen B-Felder gesetzt.
Es wird reihum 1x gewürfelt, wer die höchste Zahl würfelt, beginnt.

So lange noch weitere Steine auf den B-Feldern warten, darf keine eigene Figur auf dem A-Feld stehen bleiben.

Wer eine 6 würfelt, hat nach seinem Zug einen weiteren Wurf frei. Erzielt er dabei wieder eine 6, darf er erneut nach dem Ziehen würfeln.
Bei einer 6 muss man einen neuen Stein ins Spiel bringen, so lange noch Spielfiguren auf den eigenen B-Feldern stehen.
Ist das Feld A noch von einer anderen eigenen Spielfigur besetzt, muss dieser Stein erst mit der 6 weitergezogen werden.

„Wer mehrere Spielsteine auf der Laufbahn stehen hat, muss mit dem
vordersten Stein ziehen, der gezogen werden kann.“

Auch die Zielfelder werden beim Vorrücken einzeln gezählt. (Wer also beispielsweise direkt vor seiner Zielfeldreihe steht,
kommt mit einer 1 nur auf das Feld a, mit einer 2 nur auf das Feld b usw.; Spielsteine können übersprungen werden.)
"""
import random
import string
from copy import deepcopy
from itertools import chain
from operator import attrgetter
from pathlib import Path


def read_input(filename='wuerfel1.txt'):
    """ Beispieldatei einlesen
    Die Zeilen in Integer und List umwandeln und Zeilenumbrüche mit .strip() entfernen.
    Default ist das Aufgabenbeispiel parkplatz0.txt.
    """
    file = Path('beispieldaten', filename)
    with open(file, 'r') as file_in:
        dice_total = file_in.readline().strip()
        dice_list = [line.strip().split() for line in file_in.readlines()]
        for num, dice in enumerate(dice_list):
            dice_list[num] = [int(element) for element in dice]

    print(dice_total)
    print('dice_list', dice_list)

    return dice_list


class Player:
    counter = 1

    def __init__(self, dice):
        self.id = Player.counter
        self.dice = dice
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

        for pawn in chain(self.p1.pawn_list, self.p2.pawn_list):
            self.base.append(pawn)
        self.activate_pawn(self.p1)
        self.activate_pawn(self.p2)

    def play_round(self):
        for player in [self.p1, self.p2]:
            self.one_turn(player)
            if self.winner:
                return
        self.round += 1

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
        # Has reached the end of modelled board
        if self.is_end_of_board(new_idx):
            new_idx = new_idx - len(self.board)  # e.g. 43 (0-based) - 40 (1-based) = 3 -> 0,1,2,3 (0-based)
        # Has reached the goal strip
        if roll > pawn.moves_to_goal:  # place before goal == 0
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
        # Todo: Might do something to move more strategically, if dice has no 1
        if roll > 3:
            return False
        for idx, position in enumerate(player.goal):
            try:
                if isinstance(position, Pawn) and not player.goal[idx+roll]:
                    player.goal[idx] = None
                    player.goal[idx + roll] = position
                    return True
            except IndexError:
                continue
        return False


def setup(dice_list):
    players_list = []

    for dice in dice_list:
        faces = dice.pop(0)
        new_player = Player(dice=dice)
        players_list.append(new_player)

    return players_list


def do_simulation(player1, player2):
    print(f"{player1} vs {player2}")
    game = Game(player1, player2)

    # cmd = True
    while not game.winner:
    # while cmd is True and not game.winner:
        print(f'======== ROUND {game.round} ===========')
        game.play_round()
        print_board(game)
        # if input('Play another round? [Y/n] ') != "":
        #     cmd = False


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


if __name__ == '__main__':
    players_list = setup(read_input())

    do_simulation(players_list[0], players_list[1])
    # do_simulation(players_list[1], players_list[2])
    # do_simulation(players_list[2], players_list[3])

    # for idx, player in enumerate(players_list):
    #     # Let every dice play against every other dice
    #     idx += 1
    #     print(f"Round {idx}")
    #     while idx in range(len(players_list)):
    #         do_simulation(player, players_list[idx])
    #         idx += 1
