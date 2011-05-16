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
        self.round_state = None
        self.alt = False


    def run(self):
        """
        Get the events currently in the queue and add new event to the send queue.
        """
        while not self.render.r_queue.empty():
            process(self.render.r_queue.get().split(':'))

        for event in pygame.event.get():
            if event.type == QUIT:
                self.render.__del__()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_LALT:
                    self.alt = True
                elif event.key == K_RETURN:
                    if self.alt == True:
                        pygame.display.toggle_fullscreen()
                elif self.round_state == 'CHOICE':
                        pos = self.render.l_entities[self.render.me].pos
                    if event.key == K_UP:
                        pos[1] -= 1
                        self.render.s_queue.put('MOVE:'+pos[0]+':'+pos[1])
                    elif event.key == K_RIGHT:
                        pos[0] += 1
                        self.render.s_queue.put('MOVE:'+pos[0]+':'+pos[1])
                    elif event.key == K_DOWN:
                        pos[1] += 1
                        self.render.s_queue.put('MOVE:'+pos[0]+':'+pos[1])
                    elif event.key == K_LEFT:
                        pos[0] -= 1
                        self.render.s_queue.put('MOVE:'+pos[0]+':'+pos[1])
                    elif event.key == K_z:
                        pos[1] -= 1
                        self.render.s_queue.put('ATTACK:attack:'+pos[0]+':'+pos[1])
                    elif event.key == K_d:
                        pos[0] += 1
                        self.render.s_queue.put('ATTACK:attack:'+pos[0]+':'+pos[1])
                    elif event.key == K_s:
                        pos[1] += 1
                        self.render.s_queue.put('ATTACK:attack:'+pos[0]+':'+pos[1])
                    elif event.key == K_q:
                        pos[0] -= 1
                        self.render.s_queue.put('ATTACK:attack:'+pos[0]+':'+pos[1])
            elif event.type == KEYUP:
                if event.key == K_LALT:
                    self.alt = False


    def process(self, cmd):
        """
        Process a command from Dana.

        Arguments:
        - `cmd`: command from Dana.
        """
        if cmd[0] == 'ROUND_START':
            self.round_state = 'CHOICE'
        elif cmd[0] == 'END_ROUND':
            self.round_state = None
        elif cmd[0] == 'END_CHOICE':
            self.round_state = None
        elif cmd[0] == 'BEGIN_ACTION':
            self.round_stat = 'ACTION '+str(cmd[1])
        elif cmd[0] == 'MOVE':
            self.render.l_entities[cmd[1]].move((cmd[2], cmd[3]),1)
        elif cmd[0] == 'ATTACK':
            self.render.l_entities[cmd[1]].play_anim(cmd[2])
        elif cmd[0] == 'ENTITY':
            f = open('data/'+cmd[1]+'.cfg')
            data = f.readline().split('**')
            f.clos()
            register_entity((cmd[3], cmd[4]), data[0], data[1], cmd[2], data[2])
        elif cmd[0] == 'YOU':
            self.render.me = cmd[1]
