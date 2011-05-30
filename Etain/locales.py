#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygame.locals import *

# Render config
ROWS = 24
COLUMNS = 32
SQUARE_SIZE = 32
HEIGHT = ROWS * SQUARE_SIZE
WIDTH = COLUMNS * SQUARE_SIZE
TITLE = 'Tuatha dé Danann'
FPS = 40

# Game
TIME_CHOICE = 5000.0

# Constantes
PI = 3.141593

# Chat
BUBBLE_TTL = FPS * 4
CHAT_WIDTH = WIDTH - 8
CHAT_HEIGHT = 217

# Factions
NEUTRE = 0
ALLY = 1
ENNEMY = 2

# Health bars
H_WIDTH = SQUARE_SIZE
H_HEIGHT = 8

# Colors
RED = (200, 0, 0)
BLUE = (0, 0, 150)
GREEN = (0, 200, 0)
BEIGE = (220, 220, 130)
GREY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Factions' color
FACTION_COLOR = {NEUTRE : GREY, ALLY : BLUE, ENNEMY : RED}

# Menu config
MENU_WIDTH = 500
MENU_HEIGHT = 300

# Dictionnary
DICT = {K_a : 'a', K_b : 'b', K_c : 'c', K_d : 'd', K_e : 'e', K_f : 'f', K_g : 'g', K_h : 'h', K_i : 'i', K_j : 'j', K_k : 'k', K_l : 'l',
        K_m : 'm', K_n : 'n', K_o : 'o', K_p : 'p', K_q : 'q', K_r : 'r', K_s : 's', K_t : 't', K_u : 'u', K_v : 'v', K_w : 'w', K_x : 'x',
        K_y : 'y', K_z : 'z', K_COMMA : ',', K_PERIOD : '.', K_EXCLAIM : '!', K_QUESTION : '?', K_SPACE : ' '}

# Cursor
ARROW = ("arrow",
         ("xX                      ",
          "X.X                     ",
          "X..X                    ",
          "X...X                   ",
          "X....X                  ",
          "X.....X                 ",
          "X......X                ",
          "X.......X               ",
          "X........X              ",
          "X.....XXXX              ",
          "X..X..X                 ",
          "X.X X..X                ",
          "XX  X..X                ",
          "     X..X               ",
          "     X..X               ",
          "      XX                ",
          "                        ",
          "                        ",
          "                        ",
          "                        ",
          "                        ",
          "                        ",
          "                        ",
          "                        "))
SWORD = ("sword",
         ("  XXX                   ",
          "  XxXX                  ",
          "  XX.XX                 ",
          "   XX.XX                ",
          "    XX.XX               ",
          "     XX.XX              ",
          "      XX.XX             ",
          "       XX.XX      ..    ",
          "        XX.XX      ..   ",
          "         XX.XX    ...   ",
          "          XX.XX  ...    ",
          "           XX.XX...     ",
          "            XXX...      ",
          "             X...       ",
          "             ...X.      ",
          "            ... .X.     ",
          "         . ...   .X.    ",
          "         ....     .X..  ",
          "          ..       .XX. ",
          "                   .XX. ",
          "                    ..  ",
          "                        ",
          "                        ",
          "                        ",))
