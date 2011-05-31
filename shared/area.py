#!/usr/bin/env python
# -*- coding: UTF8 -*-

import sys
import pickle
from random import randint
import pygame
from pygame.locals import *

SQUARE_SIZE = 32
COLUMNS = 32
ROWS = 24

VOID = 0
GRASS = 1
DIRT = 2
MIXED = 3
WATER = 4

T_BRUSHES = 3
T_TALL_GRASS = 4
T_GRASS = 0
T_WATER = 18
T_WATER_CURVE = 19
T_DIRT = 17
T_DIRT_R = 5
T_DIRT_L = 6
T_DIRT_U = 7
T_DIRT_D = 8
T_DIRT_DR = 9
T_DIRT_DL = 10
T_DIRT_UL = 11
T_DIRT_UR = 12
T_DIRT_GDR = 13
T_DIRT_GDL = 14
T_DIRT_GUL = 15
T_DIRT_GUR = 16

class Area():
    """
    Object defining area of a map.
    """

    def __init__(self):
        """
        Area initialize it's internal representation of the map.

        Attributes:
        - `map`: array defining the map with the tiles' code.
        - `tiles`: list of pygame Surface corresponding to the tiles' code.
        """
        self.map = []
        self.tiles = {}


    def __getitem__(self, row):
        """
        Allow the user to get a row of the map with area[row].

        Arguments:
        - `row`: index of the row to return.
        """
        return self.map[row]


    def load_tiles(self):
        """
        Load all tiles' image used in this area in memory.
        """
        for line in self.map:
            for tile in line:
                if not tile in self.tiles:
                    self.tiles[tile] = pygame.image.load('tiles/'+str(tile)+'.png')


if __name__ == '__main__':
    pygame.init()
    area = Area()
    if len(sys.argv) < 2:
        print 'usage: ./area.py <source>'
        sys.exit()

    area.map = [[0]* COLUMNS for x in xrange(ROWS)]
    map = [[0]* COLUMNS for x in xrange(ROWS)]
    f = open(sys.argv[1], 'r')
    for i in xrange(0, ROWS):
        line = f.readline()[:-1]
        row = line.split(' ')
        for j in xrange(0, COLUMNS):
            map[i][j] = int(row[j])
    f.close()

    for i in xrange(0, ROWS):
        for j in xrange(0, COLUMNS):
            if i <= 0:
                up = VOID
            else:
                up = map[i - 1][j]
            if i >= ROWS - 1:
                down = VOID
            else:
                down = map[i + 1][j]
            if j <= 0:
                left = VOID
            else:
                left = map[i][j - 1]
            if j >= COLUMNS - 1:
                right = VOID
            else:
                right = map[i][j + 1]
            if map[i][j] == GRASS:
                if randint(0, 50):
                    area.map[i][j] = T_GRASS
                elif randint(0, 2):
                    area.map[i][j] = T_BRUSHES
                else:
                    area.map[i][j] = T_TALL_GRASS
            elif map[i][j] == WATER:
                if up == WATER and left in (WATER, VOID) and right == GRASS and down == GRASS:
                    area.map[i][j] = T_WATER_CURVE
                else:
                    area.map[i][j] = T_WATER
            elif map[i][j] == MIXED:
                MIXEDV = (MIXED, VOID)
                DIRTM = (DIRT, MIXED)
                # Sides of the road
                if up in DIRTM and down == GRASS and left in MIXEDV and right in MIXEDV:
                    area.map[i][j] = T_DIRT_U
                elif up in MIXEDV and down in MIXEDV and left == GRASS and right in DIRTM:
                    area.map[i][j] = T_DIRT_R
                elif up == GRASS and down in DIRTM and left in MIXEDV and right in MIXEDV:
                    area.map[i][j] = T_DIRT_D
                elif up in MIXEDV and down in MIXEDV and left in DIRTM and right == GRASS:
                    area.map[i][j] = T_DIRT_L

                # Corners of the road
                elif up == GRASS and down in MIXEDV and left == GRASS and right in MIXEDV:
                    area.map[i][j] = T_DIRT_DR
                elif up == GRASS and down in MIXEDV and left in MIXEDV and right == GRASS:
                    area.map[i][j] = T_DIRT_DL
                elif up in MIXEDV and down == GRASS and left in MIXEDV and right == GRASS:
                    area.map[i][j] = T_DIRT_UL
                elif up in MIXEDV and down == GRASS and left == GRASS and right in MIXEDV:
                    area.map[i][j] = T_DIRT_UR

                # Curves of the road
                elif map[i + 1][j + 1] == GRASS:
                    area.map[i][j] = T_DIRT_GDR
                elif map[i + 1][j - 1] == GRASS:
                    area.map[i][j] = T_DIRT_GDL
                elif map[i - 1][j - 1] == GRASS:
                    area.map[i][j] = T_DIRT_GUL
                elif map[i - 1][j + 1] == GRASS:
                    area.map[i][j] = T_DIRT_GUR

                # Center of the road
                else:
                    area.map[i][j] = T_DIRT
            elif map[i][j] == DIRT:
                area.map[i][j] = T_DIRT
            else:
                area.map[i][j] = T_GRASS

    mapname = raw_input("map name : ")
    f_map = open(mapname+'.map', 'w')
    pickle.dump(area, f_map)
    f_map.close()
