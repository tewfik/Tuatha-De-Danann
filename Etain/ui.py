#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pygame
from pygame.locals import *

class UI():
    """
    Class used for the User Interface.

    its run() method take care of mouse and keayboard input.
    """

    def __init__(self, render):
        """
        Initialize the UI and the Key which will bond to actions.

        Attributes:
        - `render`: the main render object used for display.
        - `alt`: Boolean representing the state of the LEFT_ALT key.
        """
        self.render = render
        self.alt = False


    def run(self):
        """
        Get the event currently in the queue.
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
