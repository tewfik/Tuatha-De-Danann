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
            self.process(self.render.r_queue.get().split(':'))

        for event in pygame.event.get():
            if event.type == QUIT:
                self.render.__del__()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_LALT:
                    self.alt = True
                elif self.alt == True:
                    if event.key == K_RETURN:
                        pygame.display.toggle_fullscreen()
                    elif event.key == K_g:
                        self.render.grid_render = True
                    elif event.key == K_r:
                        self.render.fps_render = True
                elif self.round_state == 'CHOICE':
                    pos = list(self.render.l_entities[self.render.me].pos)
                    if event.key == K_UP:
                        pos[1] -= 1
                        self.render.s_queue.put('MOVE:'+str(pos[0])+':'+str(pos[1]))
                    elif event.key == K_RIGHT:
                        pos[0] += 1
                        self.render.s_queue.put('MOVE:'+str(pos[0])+':'+str(pos[1]))
                    elif event.key == K_DOWN:
                        pos[1] += 1
                        self.render.s_queue.put('MOVE:'+str(pos[0])+':'+str(pos[1]))
                    elif event.key == K_LEFT:
                        pos[0] -= 1
                        self.render.s_queue.put('MOVE:'+str(pos[0])+':'+str(pos[1]))
                    elif event.key == K_z:
                        pos[1] -= 1
                        self.render.s_queue.put('ATTACK:attack:'+str(pos[0])+':'+str(pos[1]))
                    elif event.key == K_d:
                        pos[0] += 1
                        self.render.s_queue.put('ATTACK:attack:'+str(pos[0])+':'+str(pos[1]))
                    elif event.key == K_s:
                        pos[1] += 1
                        self.render.s_queue.put('ATTACK:attack:'+str(pos[0])+':'+str(pos[1]))
                    elif event.key == K_q:
                        pos[0] -= 1
                        self.render.s_queue.put('ATTACK:attack:'+str(pos[0])+':'+str(pos[1]))
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
            self.round_state = ''
        elif cmd[0] == 'END_CHOICE':
            self.round_state = 'RENDER BATTLE'
        elif cmd[0] == 'BEGIN_ACTION':
            self.round_stat = 'ACTION '+str(cmd[1])
        elif cmd[0] == 'MOVE':
            print 'caracter position'
            try:
                self.render.l_entities[int(cmd[1])].move(dest=(int(cmd[2]), int(cmd[3])), speed=1)
            except ValueError as e:
                print(e)
        elif cmd[0] == 'ATTACK':
            try:
                self.render.l_entities[int(cmd[1])].play_anim(name=cmd[2])
            except ValueError as e:
                print(e)
        elif cmd[0] == 'ENTITY':
            f = open('data/'+cmd[1]+'.cfg')
            data = f.readline().split('**')
            f.close()
            try:
                self.render.register_entity(pos=(int(cmd[3]), int(cmd[4])), width=int(data[0]), height=int(data[1]), hp=int(cmd[5]),
                                            uid=int(cmd[2]), anim_path=data[2])
            except ValueError as e:
                print(e)
        elif cmd[0] == 'YOU':
            self.render.me = int(cmd[1])
