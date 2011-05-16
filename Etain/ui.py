#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pygame
from pygame.locals import *

class UI():
    """
    """

    def __init__(self, render):
        """
        """
        self.render = render
        self.alt = False


    def run(self):
        """
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.render.__del__()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_LALT:
                    self.alt = True
                if event.key == K_RETURN:
                    if self.alt == True:
                        pygame.display.toggle_fullscreen()
            elif event.type == KEYUP:
                if event.key == K_LALT:
                    self.alt = False
