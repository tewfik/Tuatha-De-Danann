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
        self.current_frame = 0
        self.frame_elapsed = 0
        self.ttl = ttl
        self.dead = False
        self.frames = []
        self.type = None
        if type == 'dmg':
            self.current_frame = -1
            self.type = 'dmg'
            self.pos = (pos[0] - 50 , pos[1] - 15)
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
        else:
            f = open('data/' + type + '.particle', 'r')
            data = f.readline().split('**')
            f.close()
            self.pos = (pos[0] - int(data[0])/2 , pos[1] - int(data[1])/2)
            self.frame_rate = int(data[2])
            for path in data[3:-1]:
                sprite = pygame.image.load('sprites/' + path)
                self.frames.append(sprite)


    def update(self):
        if self.type == 'dmg':
            if self.current_frame == self.ttl - 1:
                self.dead = True
            else:
                self.current_frame += 1
            if self.current_frame < self.ttl / 4:
                return self.frames[self.current_frame]
            else :
                return self.frames[self.ttl/4]
        else:
            self.frame_elapsed += 1
            if self.frame_elapsed >= self.frame_rate:
                self.frame_elapsed = 0
                if self.current_frame < len(self.frames) - 1:
                    self.current_frame += 1
                else:
                    self.dead = True
            return self.frames[self.current_frame]
