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
from itertools import chain
from operator import attrgetter
from pathlib import Path


def read_input(filename='wuerfel0.txt'):
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
        self.id = 0
        self.owner = owner
        self.moves_to_goal = 39
        self.position = None
        self.set_id()

    def set_id(self):
        if self.owner is Pawn.previous_owner:
            Pawn.counter += 1
        else:
            Pawn.counter = 1
        Pawn.previous_owner = self.owner
        self.id = Pawn.counter

    def reset_moves_to_goal(self):
        self.moves_to_goal = 39

    def __repr__(self):
        return f'\"Pawn {self.owner.id}-{self.id}\"'


class Game:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p1.startpos = 0
        self.p2 = p2
        self.p2.startpos = 20
        self.board = [None] * 40
        self.base = []
        self.round = 1
        self.winner = None

        for pawn in chain(self.p1.pawn_list, self.p2.pawn_list):
            self.base.append(pawn)
        self.activate_pawn(self.p1)
        self.activate_pawn(self.p2)

    def play_round(self):
        self.one_turn(self.p1)
        self.one_turn(self.p2)
        print('-- Gameboard:', self.board)
        self.round += 1

    def one_turn(self, player):
        roll = player.roll_dice()
        print(f'-- {player} rolls', roll)

        while roll == 6:
            if self.is_position_blocked(player.startpos):
                self.clear_position(player, roll, player.startpos)
                continue
            elif not self.activate_pawn(player):
                # No pawns left in base
                self.move_pawn(player, roll)
            roll = player.roll_dice()
            print(f'-- {player} rolls', roll)

        self.move_pawn(player, roll)

    def is_position_blocked(self, position):
        if self.board[position]:
            return True
        return False

    def clear_position(self, player, roll, position):
        print('-- Clearing position...')
        pawn = self.board[position]
        if pawn.owner is player:
            self.move_pawn(player, roll, pawn=pawn)
        else:
            self.throw_out_pawn(pawn)

    def move_pawn(self, player, roll, pawn=None):
        if not pawn:
            pawn = min(player.pawn_list, key=attrgetter('moves_to_goal'))
        idx = self.board.index(pawn)
        new_idx = idx + roll
        if self.is_end_of_board(new_idx):
            new_idx = new_idx - len(self.board)  # e.g. 43 (0-based) - 40 (1-based) = 3 -> 0,1,2,3 (0-based)
        if self.is_position_blocked(new_idx):
            self.clear_position(player, roll, new_idx)
        else:
            print('-- Moving', pawn, 'by', roll)
            self.board[idx] = None
            self.board[new_idx] = pawn
            pawn.moves_to_goal -= roll

    def throw_out_pawn(self, pawn):
        idx = self.board.index(pawn)
        self.board[idx] = None
        self.base.append(pawn)
        pawn.reset_moves_to_goal()
        print('-- Threw out', pawn)

    def activate_pawn(self, player):
        for pawn in player.pawn_list:
            if pawn in self.base:
                self.base.remove(pawn)
                self.board[player.startpos] = pawn
                print('-- Activated', pawn)
                return True
        print('!! No pawns in base')
        return False

    def is_end_of_board(self, position):
        if position > (len(self.board) - 1):
            return True
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

    while game.round <= 10:
        game.play_round()


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
