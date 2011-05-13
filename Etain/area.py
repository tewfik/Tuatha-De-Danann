#!/usr/bin/env python
# -*- coding: UTF8 -*-

import pickle
import pygame
from pygame.locals import *

SQUARE_SIZE = 32
WIDTH = 32
HEIGHT = 24

class Area():
    """
    Object defining area of a map and the entities (NPC and non-living) on it.
    """

    def __init__(self):
        """
        Attributes:
        - `map`: array defining the map with the tiles' code.
        - `tiles`: list of pygame Surface corresponding to the tiles' code.
        """
        self.map = []
        self.tiles = [False]*128


    def load_tiles(self):
        """
        Load all tiles' image used in this area in memory.
        """
        for line in self.map:
            for tile in line:
                if not self.tiles[tile]:
                    self.tiles[tile] = pygame.image.load('tiles/'+str(tile)+'.png')


if __name__ == '__main__':
    pygame.init()
    area = Area()
    if len(sys.argv) < 2:
        print 'usage: ./area.py <source>'
        sys.exit()

    f = open(path, 'r')
    area.map = [[0]*HEIGHT]
    for i in xrange(0, HEIGHT):
        line = f.readline()
        area.map[i] = line.split(' ')
    f.close()

    f_map = open('forest_1.map', 'w')
    pickle.dump(area, f_map)
    f_map.close()
