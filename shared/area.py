#!/usr/bin/env python
# -*- coding: UTF8 -*-

import sys
import pickle
import pygame
from pygame.locals import *

SQUARE_SIZE = 32
WIDTH = 32
HEIGHT = 24

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

        Attributes:
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

    f = open(sys.argv[1], 'r')
    area.map = [[0]* WIDTH for x in xrange(0,HEIGHT)]
    for i in xrange(0, HEIGHT):
        line = f.readline()[:-1]
        row = line.split(' ')
        for j in xrange(0, WIDTH):
            area.map[i][j] = int(row[j])
    f.close()

    mapname = raw_input("map name : ")
    f_map = open(mapname+'.map', 'w')
    pickle.dump(area, f_map)
    f_map.close()
