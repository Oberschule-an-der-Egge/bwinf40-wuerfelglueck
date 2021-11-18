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
from pathlib import Path
from models import Player, Game
from models_verbose import Player, Game


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
        game.play_round()
        # if input('Play another round? [Y/n] ') != "":
        #     cmd = False

    print(f'{game.winner} has won the game!')
    return game.winner


if __name__ == '__main__':
    players_list = setup(read_input())

    for g in range(200):
        winner = do_simulation(players_list[0], players_list[1])
        winner.wins += 1
    print(f'Player 1 wins {players_list[0].wins}')
    print(f'Player 2 wins {players_list[1].wins}')

    # do_simulation(players_list[1], players_list[2])
    # do_simulation(players_list[2], players_list[3])

    # for idx, player in enumerate(players_list):
    #     # Let every dice play against every other dice
    #     idx += 1
    #     print(f"Round {idx}")
    #     while idx in range(len(players_list)):
    #         do_simulation(player, players_list[idx])
    #         idx += 1
