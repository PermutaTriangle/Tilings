from re import split
from grid import Grid, GridSet

def gridsFromFile(file_name):
    grids = []
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
            # Parse each line
            for i in split(r'\n', item):
                if i.startswith('+'):
                    continue
                if i.startswith('|'):
                    table.append(i.strip().split('|')[1:-1])
                else:
                    num, rule = i.split(': ')
                    rules[num] = rule
            grids.append(Grid(table, rules))
    return GridSet(grids)

if __name__ == '__main__':
    print(gridsFromFile('ex9_output.txt'))
