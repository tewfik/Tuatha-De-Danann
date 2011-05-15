#!/usr/bin/env python
# -*- coding: UTF8 -*-

import sys
import pygame
from pygame.locals import *
import pickle
sys.path.append("../shared/")
from area import Area
import entity

SQUARE_SIZE = 32


class Render():
    """
    Render engine.

    Display entities, map and catch mouse and keyboard input to transfer them to the event handler.
    """

    def __init__(self, height, width, depth, title, fps):
        """
        Initialize the window's display.

        Attributes:
        - `height`: the height of the window (given in square, size in pixel of each square given by SQUARE_SIZE).
        - `width`: the width of the window (given in square).
        - `depth`: the color depth.
        - `title`: set the caption in windowed mode.
        - `fps`: set the frame rate (caution : increasing the frame rate increase the game's speed).
        """
        pygame.init()
        self.font = pygame.font.SysFont(None, 24)
        self.fps = fps
        self.height = height
        self.width = width
        self.l_entities = entity.List()
        self.window = pygame.display.set_mode((width*SQUARE_SIZE, height*SQUARE_SIZE), 0, depth)
        pygame.display.set_caption(title)


    def run(self):
        """
        Main programm's loop (currently run at 40Fps).
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
                            pygame.display.toggle_fullscreen()
                elif event.type == KEYUP:
                    if event.key == K_LALT:
                        alt = False

            self.draw_world()
            self.draw_entities()
            text = self.font.render(str(clock.get_fps()), False, (0, 0, 0))
            text_Rect = text.get_rect()
            text_Rect.right = self.width*SQUARE_SIZE - 10
            text_Rect.top = 10
            self.window.blit(text, text_Rect)

            pygame.display.update()
            clock.tick(self.fps)


    def draw_world(self):
        """
        Display the ground's tiles'.
        """
        pos = pygame.Rect(0, 0, SQUARE_SIZE, SQUARE_SIZE)
        for j in xrange(0, self.height):
            pos.top = j * SQUARE_SIZE
            for i in xrange(0, self.width):
                pos.left = i * SQUARE_SIZE
                self.window.blit(self.area.tiles[self.area.map[j][i]], pos)

    def register_entity(self, pos, width, height, uid, anim_path):
        """
        Register a New graphic entity to the world.
        """
        self.l_entities.add_entity(pos, width, height, uid, anim_path)


    def remove_entity(self, uid):
        """
        """
        self.l_entities.remove_entity(uid)


    def draw_entities(self):
        """
        Draw every entities on the map in their current state of animation.
        """
        for uid in self.l_entities.entities:
            image = self.l_entities.entities[uid].update()
            pos = self.l_entities.entities[uid].get_hitbox()
            self.window.blit(image, pos)


    def load_map(self, path):
        """
        Load the map and entities' informations from a file.

        Attributes:
        - `path`: the path to the save file of the map to load.
        """
        f_map = open(path, 'r')
        self.area = pickle.load(f_map)
        self.area.load_tiles()
        f_map.close()


    def __del__(self):
        """
        Unload the display and exit the programm.
        """
        pygame.quit()
