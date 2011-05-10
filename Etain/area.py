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
    """

    def __init__(self):
        self.map = []
        self.tiles = [False]*128


    def load_tiles(self):
        for line in self.map:
            for tile in line:
                if not self.tiles[tile]:
                    self.tiles[tile] = pygame.image.load('tiles/'+str(tile)+'.png')


if __name__ == '__main__':
    pygame.init()
    area = Area()

    area.map = [[0]*WIDTH for x in xrange(0, HEIGHT)]
    count = 0
    for j in xrange(0, HEIGHT):
        for i in xrange(0, WIDTH):
            area.map[j][i] = count
            count += 1
            if count > 10:
                count = 0

    f_map = open('forest_1.map', 'w')
    pickle.dump(area, f_map)
    f_map.close()
