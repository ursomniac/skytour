from itertools import chain
import math
def grid_and_transpose_list(l, cols=5, transpose=True, null=True, debug=False):
    rows = math.ceil(len(l) / cols)
    init =  \
        [[None for x in range(cols)] for y in range(rows)] \
        if transpose else \
        [[None for x in range(rows)] for y in range(cols)]
    row = 0
    col = 0
    idx = 0
    for idx in range(len(l)):
        item = l[idx]
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
    flat = list(chain.from_iterable(init))
    # remove None
    if not null:
        final = [x for x in flat if x is not None]
        return final
    return flat
