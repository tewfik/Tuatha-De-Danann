#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Render config
ROWS = 24
COLUMNS = 32
SQUARE_SIZE = 32
HEIGHT = ROWS * SQUARE_SIZE
WIDTH = COLUMNS * SQUARE_SIZE
TITLE = 'Tuatha dé Danann'
FPS = 40

# Factions
NEUTRE = 0
ALLY = 1
ENNEMY = 2

# Colors
RED = (200, 0, 0)
BLUE = (0, 0, 150)
GREEN = (0, 200, 0)
GREY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Factions' color
FACTION_COLOR = {NEUTRE : GREY, ALLY : BLUE, ENNEMY : RED}

# Menu config
MENU_WIDTH = 500
MENU_HEIGHT = 300

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
          "      XX.XX       .     ",
          "       XX.XX       ..   ",
          "        XX.XX      ..   ",
          "         XX.XX    ...   ",
          "          XX.XX  ...    ",
          "           XX.XX...     ",
          "            XXX...      ",
          "             X...       ",
          "             ...X.      ",
          "            ... .X.     ",
          "           ...   .X.    ",
          "        .....     .X..  ",
          "         ...       .XX. ",
          "                   .XX. ",
          "                    ..  ",
          "                        ",
          "                        ",
          "                        ",))
