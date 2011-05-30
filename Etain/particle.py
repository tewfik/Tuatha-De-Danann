#!/usr/bin/env python
# -*- coding: utf-8 -*-

from locales import *
import pygame
from pygame.locals import *

class Particle:
    """
    """

    def __init__(self, type, params, ttl, pos):
        font = pygame.font.SysFont(None, 60)
        font.set_bold(True)
        self.current_frame = -1
        self.ttl = ttl
        self.dead = False
        self.pos = (pos[0] - 50 , pos[1] - 15)
        self.frames = []
        if type == 'dmg':
            msg = '- ' + params[0]
            for i in xrange(self.ttl/4 + 1):
                surf = pygame.Surface((100, 50), HWSURFACE | SRCALPHA)
                self.frames.append(surf)
                text = font.render(msg, True, RED)
                text_Rect = text.get_rect()
                text = pygame.transform.smoothscale(text, (int(text_Rect.width / float(self.ttl/4) * (i + 1) + 10),
                                                           int(text_Rect.height / float(self.ttl/4) * (i + 1) + 10)))
                text_Rect = text.get_rect()
                text_Rect.center = (50, 25)
                self.frames[i].blit(text, text_Rect)


    def update(self):
        if self.current_frame == self.ttl - 1:
            self.dead = True
        else:
            self.current_frame += 1
        if self.current_frame < self.ttl / 4:
            return self.frames[self.current_frame]
        else :
            return self.frames[self.ttl/4]
