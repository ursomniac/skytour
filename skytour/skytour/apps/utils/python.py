from itertools import chain
import math
def grid_and_transpose_list(l, cols=5, transpose=True, null=True, debug=True):
    rows = math.ceil(len(l) / cols)
    if debug:
        print("COLS: ", cols, " ROWS: ", rows)
    init =  \
        [[None for x in range(cols)] for y in range(rows)] \
        if transpose else \
        [[None for x in range(rows)] for y in range(cols)]
    if debug:
        print("M: ", init)
    row = 0
    col = 0
    idx = 0
    for idx in range(len(l)):
        item = l[idx]
        if debug:
            print(f"IDX: {idx} ROW: {row} COL: {col} ITEM: {item}")
        init[row][col] = item
        if transpose:
            if idx % rows == rows - 1:
                col += 1
                row = 0
            else:
                row += 1
        else:
            if idx % cols == cols - 1:
                row += 1
                col = 0
            else:
                col += 1
    if debug:
        print(f"GRID: ", init)

    flat = list(chain.from_iterable(init))
    if debug:
        print("FLAT: ", flat)
    # remove None
    if not null:
        final = [x for x in flat if x is not None]
        if debug:
            print("FINAL: ", final)
        return final
    return flat
