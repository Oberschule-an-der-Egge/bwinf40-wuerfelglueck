from pathlib import Path


def read_input(filename='wuerfel0.txt'):
    """ Beispieldatei einlesen
    Die Zeilen in Integer und List umwandeln und Zeilenumbrüche mit .strip() entfernen.
    Default ist das Aufgabenbeispiel parkplatz0.txt.
    """
    file = Path('beispieldaten', filename)
    with open(file, 'r') as file_in:
        dice_total = file_in.readline().strip()
        dice = [line.strip() for line in file_in.readlines()]

    print(dice_total)
    print(dice)

    return


if __name__ == '__main__':
    read_input()
