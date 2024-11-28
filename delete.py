import numpy as np

WINDOW_LENGTH = 4

ROW_COUNT = 6
COLUMN_COUNT = 7

board = np.zeros((6,7))

for r in range(ROW_COUNT - 3):
    for c in range(COLUMN_COUNT - 3):
        for i in range(WINDOW_LENGTH):
            print((r+3-i, c+i), end=" ")
        print("||", end=" ")

print("")
print(board)
