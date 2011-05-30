#!/usr/bin/env python
# -*- coding: utf-8 -*-

import locales
import pygame
from pygame.locals import *

class Particle:
    """
    """

    def __init__(self, type, params, TTL, pos):
        self.current_frame = -1
        self.dead = False
        self.pos = (pos[0] - 50 , pos[1] - 15)
        if type == 'dmg':
            msg = '- ' + params[0]
            frame = []
            for i in xrange(TTL):
                font = pygame.font.SysFont(None, i * 30.0 / TTL)
                frame.append(pygame.Surface((100, 50), HWSURFACE, SRCALPHA))
                text = font.render(msg, True, RED)
                text_Rect = text.get_Rect()
                text_Rect.center = (50, 25)
                frame[i].blit(text, text_Rect)


    def update(self):
        if self.current_frame == TTL:
            self.dead = True
        else:
            self.current_frame += 1
        return frame[self.current_frame]
