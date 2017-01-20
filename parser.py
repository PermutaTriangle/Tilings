from re import split
from Tiling import Tile, Tiling

from Permuta import Perm, PermSet

def tilingsFromFile(file_name):
    tilings = []
    with open(file_name) as f:
        s = f.read()

        # Split on 123124:\n0101010100110101010 to find all rule blocks on the form
        # +-+-+-+-+
        # | |o| | |
        # +-+-+-+-+
        # | | | |o|
        # +-+-+-+-+
        # | | |1| |
        # +-+-+-+-+
        # |o| | | |
        # +-+-+-+-+
        # 1: Av([[2, 1]])
        for i, el in enumerate(split(r'\d+:\n[01]+', s)[1:]):
            # We always take the first rule in a block, they are seperated by two newlines
            item = el.strip().split('\n\n')[0]
            table = []
            rules = {}
            rule = {}
            # Parse each line
            for i in split('\n', item):
                if i.startswith('+'):
                    continue
                if i.startswith('|'):
                    table.append(i.strip().split('|')[1:-1])
                else:
                    num, rule = i.split(': ')
                    rules[num] = rule
            for i in range(len(table)):
                for j in range(len(table[i])):
                    char = table[i][j]
                    if char == 'X':
                        rule[(i, j)] = 'self'
                    elif char.isnumeric():
                        rule[(i, j)] = rules.get(char, None)
                    elif char == 'o':
                        rule[(i, j)] = 'p'
            tilings.append((table,rules))
    return tilings

if __name__ == '__main__':
    print(gridsFromFile('ex9_output.txt'))
