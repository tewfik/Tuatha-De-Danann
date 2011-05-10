#!/usr/bin/env python
# -*- coding: UTF8 -*-

import sys
import pygame
import pickle
from area import Area
from pygame.locals import *

SQUARE_SIZE = 32
HEIGHT = 24
WIDTH = 32
TITLE = 'Tuatha Dé Danann'

class Render():
    """
    """

    def __init__(self, height, width, depth, title):
        """
        """
        pygame.init()
        self.height = height
        self.width = width
        self.window = pygame.display.set_mode((width*SQUARE_SIZE, height*SQUARE_SIZE), 0, depth)
        pygame.display.set_caption(title)


    def run(self):
        """
        """
        clock = pygame.time.Clock()
        alt = False
        ret = False
        while(True):
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.__del__()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_LALT:
                        alt = True
                    if event.key == K_RETURN:
                        if alt == True:
                            print 'enter'
                            pygame.display.toggle_fullscreen()
                elif event.type == KEYUP:
                    if event.key == K_LALT:
                        alt = False
            pygame.display.update()
            clock.tick(40)


    def draw_world(self):
        pos = pygame.Rect(0, 0, SQUARE_SIZE, SQUARE_SIZE)
        for j in xrange(0, self.height):
            pos.top = j * SQUARE_SIZE
            for i in xrange(0, self.width):
                pos.left = i * SQUARE_SIZE
                self.window.blit(self.area.tiles[self.area.map[j][i]], pos)


    def load_map(self, path):
        """
        """
        f_map = open('forest_1.map', 'r')
        self.area = pickle.load(f_map)
        self.area.load_tiles()


    def __del__(self):
        """
        """
        pygame.quit()


if __name__ == '__main__':
    display = Render(HEIGHT, WIDTH, 32, TITLE)
    display.load_map('')
    display.draw_world()
    display.run()
