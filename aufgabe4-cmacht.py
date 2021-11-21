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
from models import Player, Game, print_board
# from models_verbose import Player, Game


def read_input(filename='wuerfel1.txt'):
    """ Beispieldatei einlesen
    Die Zeilen in List umwandeln, Zeilenumbrüche mit .strip() entfernen.
    Anschließend die Zahlen von String->Integer konvertieren.
    Default ist das Aufgabenbeispiel wuerfel0.txt.
    """
    file = Path('beispieldaten', filename)
    with open(file, 'r') as file_in:
        dice_total = file_in.readline().strip()
        dice_list = [line.strip().split() for line in file_in.readlines()]
        for num, dice in enumerate(dice_list):
            dice_list[num] = [int(element) for element in dice]

    print(dice_list)

    return dice_list


def setup(dice_list):
    """ Spieler anlegen
    Lege ein Player-Objekt für jeden gegebenen Würfel an.
    """

    players_list = []
    for dice in dice_list:
        faces = dice.pop(0)
        new_player = Player(dice=dice)
        players_list.append(new_player)

    return players_list


def do_simulation(player1, player2):
    """ Führe ein Spiel zwischen zwei Spielern durch
    """
    # print(f"{player1} vs {player2}")
    game = Game(player1, player2)

    while not game.winner and game.round < 500:
        game.play_round()

    if game.round == 500:
        print("Played 500 rounds, stuck here:")
        print_board(game)

    # CMD Modus, um Schritt für Schritt durch ein Spiel zu gehen:
    # cmd = True
    # while cmd is True and not game.winner:
    #     game.play_round()
    #     if input('Play another round? [Y/n] ') != "":
    #         cmd = False

    # print(f'{game.winner} has won the game!')

    return game.winner


def play_pair_matches(player1, player2, games_per_pair):
    """ Simuliere eine gegebene Anzahl an Spielen
    Startspieler wechseln ab der Hälfte
    """
    switch = int(games_per_pair / 2)

    for count in range(games_per_pair):
        if count <= switch:
            winner = do_simulation(player1, player2)
        else:
            winner = do_simulation(player2, player1)
        player1.games_played += 1
        player2.games_played += 1
        if winner:
            winner.wins += 1


if __name__ == '__main__':
    players_list = setup(read_input())

    games_played = 0
    games_per_pair = 200
    games_per_player = games_per_pair * (len(players_list) - 1)

    # Jeder Spieler (Würfel) tritt gegen jeden anderen Würfel an
    # 1 vs 2/3/4/5, 2 vs 3/4/5, 3 vs 4/5, 4 vs 5
    for idx, player in enumerate(players_list):
        idx += 1
        while idx in range(len(players_list)):
            play_pair_matches(player, players_list[idx], games_per_pair)
            games_played += games_per_pair
            idx += 1

    print(f'Played {games_played} games.')
    for player in players_list:
        print(f'{player} with dice {player.dice} has won {player.wins} out of {player.games_played} games. ({(player.wins / player.games_played):.2f} win rate)')
