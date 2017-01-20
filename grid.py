class Grid:
    def __init__(self, table=None, rules=None):
        if table == None:
            table = list([])
        if rules == None:
            rules = dict({})
        self.table = table
        self.rules = rules
        self.size = len(table)

    def __repr__(self):
        return '<{0} size={1} numRules={2}>'.format(type(self).__name__, self.size, len(self.rules))
    def __str__(self):
        ret = 'Table:\n'
        ret += '\n'.join([str(i) for i in self.table])
        if len(self.rules) > 0:
            ret += '\nRules:\n'
            ret += '\n'.join([str(i) + ' -> ' + self.rules[i] for i in self.rules])
        return ret

class GridSet:
    def __init__(self, grids=None):
        if grids == None:
            grids = list([])
        if not all([type(i) == Grid for i in grids]):
            print('ERRORORORRORORORO')
        self.grids = grids
        self.size = len(grids)

    def __repr__(self):
        return '<{0} size={1}>'.format(type(self).__name__, self.size)
    def __str__(self):
        return '\n'.join(['\tEntry {0} in GridSet:\n{1}'.format(str(i), str(el)) for i, el in enumerate(self.grids)])

if __name__ == '__main__':
    g = Grid([['', 'o'], ['o', '']], { 1: 'Av([[1, 2]])', 2: 'Av([[2, 3, 1]])' })
    print(g)
    print(g.__repr__())
    g = GridSet([['', 'o'], ['o', '']], { 1: 'Av([[1, 2]])', 2: 'Av([[2, 3, 1]])' })
    print(g)
    print(g.__repr__())
