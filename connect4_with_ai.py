import math
import random


import numpy as np
import pygame
import sys

from numpy.ma.core import floor

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

ROW_COUNT = 6
COLUMN_COUNT = 7

WINDOW_LENGTH = 4

PLAYER = 0
AI = 1

SQUARESIZE = 100

def create_board():
    board_matrix = np.zeros((ROW_COUNT,COLUMN_COUNT))
    return board_matrix

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[5][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))
    # print(board)

def winning_move(board, piece):
    # hor
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT-3):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # ver
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # pos slope
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT-3):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    # neg slope
    for r in range(ROW_COUNT-3):

        for c in range(COLUMN_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            if board[r][c] == 0:
                pygame.draw.circle(screen, BLACK,(int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            else:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    pygame.display.update()

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    # score center
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # score positive slope
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # score negative slope
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def minmax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return None, 100000000000
            elif winning_move(board, PLAYER_PIECE):
                return None, -100000000000
            else:
                return None, 0
        else:
            return None, score_position(board, AI_PIECE)

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minmax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else: # minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minmax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col

            beta = min(beta, value)
            if alpha >= beta:
                break

        return column, value

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)

    return valid_locations

def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -80000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col

    return best_col

board = create_board()
game_over = False
turn = random.randint(PLAYER,AI)

pygame.init()

width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) *  SQUARESIZE

size = (width, height)

RADIUS = int(SQUARESIZE/2-5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

print_board(board)

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0,width,SQUARESIZE))
            posx = event.pos[0]

            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

            pygame.display.update()


        if event.type == pygame.MOUSEBUTTONDOWN:
            print(event.pos)
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))

            if turn == 0:
                posx = event.pos[0]
                col = int(floor(posx/SQUARESIZE))
                # col = int(input("Player 1 make your selection(0-6):"))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render("Player 1 wins!!", 1 , RED)
                        screen.blit(label, (20, 10))
                        print("Player 1 WINS!!")
                        game_over = True

                    turn = turn + 1
                    turn = turn % 2

                    print_board(board)
                    draw_board(np.flip(board, 0))

    if turn==AI and not game_over:

        # col = random.randint(0, COLUMN_COUNT-1)
        # col = int(input("Player 2 make your selection(0-6):"))
        # col = pick_best_move(board, AI_PIECE)
        col = minmax(board, 6, -math.inf, math.inf, True)[0]
        print(col)

        if is_valid_location(board, col):
            # pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = myfont.render("Player 2 wins!!", 1, YELLOW)
                screen.blit(label, (20, 10))
                print("Player 2 WINS!!")
                game_over = True

            print_board(board)
            draw_board(np.flip(board, 0))

            turn = turn + 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)



