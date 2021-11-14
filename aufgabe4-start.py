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

    return


if __name__ == '__main__':
    read_input()
