import os
import pygame

pygame.init()
info = pygame.display.Info()

# Valori inițiale
WIDTH = info.current_w
HEIGHT = info.current_h
BOARD_SIZE = HEIGHT - 100
ROWS = 8
COLS = 8
SQ_SIZE = BOARD_SIZE // ROWS

OFFSET_X = (WIDTH - BOARD_SIZE) // 2
OFFSET_Y = (HEIGHT - BOARD_SIZE) // 2

def update_offsets(new_w, new_h):
    global WIDTH, HEIGHT, BOARD_SIZE, SQ_SIZE, OFFSET_X, OFFSET_Y
    WIDTH, HEIGHT = new_w, new_h
    BOARD_SIZE = HEIGHT - 100 
    SQ_SIZE = BOARD_SIZE // 8
    OFFSET_X = (WIDTH - BOARD_SIZE) // 2
    OFFSET_Y = (HEIGHT - BOARD_SIZE) // 2

# Culori
LIGHT_SQUARE = (235, 235, 208)
DARK_SQUARE = (119, 149, 86)

# Căi Asset-uri
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIECES_PATH = os.path.join(BASE_DIR, "assets", "pieces")
STOCKFISH_PATH = "/home/paul/Desktop/chessgame/bin/stockfish"