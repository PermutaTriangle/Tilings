def compress_dict(blocks):
    new_blocks = compress_dict_rows(blocks)
    new_blocks = compress_dict_columns(new_blocks)
    return new_blocks


def compress_dict_columns(blocks):
    new_blocks = dict()

    points_by_i_coord = sorted(blocks.keys(), key=lambda x: x[0])

    new_i = 0
    for ind, (i, j) in enumerate(points_by_i_coord):
        if ind != 0 and points_by_i_coord[ind][0] != points_by_i_coord[ind - 1][0]:
            new_i += 1
        new_blocks[(new_i, j)] = blocks[(i, j)]
    return new_blocks


def compress_dict_rows(blocks):
    new_blocks = dict()

    points_by_j_coord = sorted(blocks.keys(), key=lambda x: x[1])

    new_j = 0
    for ind, (i, j) in enumerate(points_by_j_coord):
        if ind != 0 and points_by_j_coord[ind][1] != points_by_j_coord[ind - 1][1]:
            new_j += 1
        new_blocks[(i, new_j)] = blocks[(i, j)]
    return new_blocks



if __name__ == "__main__":
    blocks = compress_dict({(0, 1): None, (4, 8): "Hello", (1, 5): "It's me", (9, 0): None, (3, 1): None})
    print(sorted(blocks.keys(), key= lambda x: x[0]))
    print(sorted(blocks.keys(), key=lambda x: x[1]))
    print(blocks)
