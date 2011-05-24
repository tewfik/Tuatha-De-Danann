#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pygame
from pygame.locals import *
from locales import *

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
        - `spec`: A boolean setting whever the client can play or is a spectator.
        - `fight`: A dictionnary which contains the actions to perform during render phase.
        - `pa`: the current action being executed.
        - `frame_render`: the current frame number.
        """
        self.render = render
        self.round_state = None
        self.alt = False
        self.spec = False
        self.fight = {}
        self.pa = 0
        self.frame_render = FPS


    def run(self):
        """
        Get the events currently in the queue and add new event to the send queue.
        """
        while not self.render.r_queue.empty():
            self.process(self.render.r_queue.get().split(':'))

        if self.round_state == 'RENDER':
            self.frame_render += 1
            if self.frame_render >= FPS:
                self.frame_render = 0
                if self.pa in self.fight:
                    self.do_actions(self.pa)
                    self.pa += 1
                else:
                    self.round_state = 'NEXT_ROUND'
                    self.render.s_queue.put('RENDER_OK')

        if not self.spec:
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
                            self.render.grid_render = not self.render.grid_render
                        elif event.key == K_r:
                            self.render.fps_render = not self.render.fps_render
                elif event.type == KEYUP:
                    if event.key == K_LALT:
                        self.alt = False
                else:
                    self.mouse_event(event)


    def mouse_event(self, event):
        """
        """
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = (event.pos[0] / SQUARE_SIZE, event.pos[1] / SQUARE_SIZE)
            if self.mouse_over((WIDTH - 18, 0, 18, 18), event.pos):
                self.render.menu = not self.render.menu
            elif not self.render.menu:
                if event.button == 1 and self.round_state == 'CHOICE':
                    if self.entity_on(mouse_pos):
                        self.render.s_queue.put('ATTACK:attack:%d:%d' % mouse_pos)
                    else:
                        self.render.s_queue.put('MOVE:%d:%d' % mouse_pos)
                        self.render.dest_square = (mouse_pos[0] * SQUARE_SIZE, mouse_pos[1] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            else:
                menu_x = (WIDTH - MENU_WIDTH) / 2
                menu_y = (HEIGHT - MENU_HEIGHT) / 2
                if self.mouse_over((menu_x + 30, menu_y + 50, 10, 10), event.pos):
                        self.render.grid_render = not self.render.grid_render
                elif self.mouse_over((menu_x + 30, menu_y + 90, 10, 10), event.pos):
                        self.render.fps_render = not self.render.fps_render
                elif self.mouse_over((menu_x + MENU_WIDTH - 16, menu_y + 3, 13, 13), event.pos):
                        self.render.menu = not self.render.menu
        elif event.type == MOUSEMOTION:
            mouse_pos = (event.pos[0] / SQUARE_SIZE, event.pos[1] / SQUARE_SIZE)
            if self.entity_on(mouse_pos):
                self.render.use_cursor(SWORD)
            elif self.render.cursor != ARROW[0]:
                self.render.use_cursor(ARROW)


    def mouse_over(self, rect, pos):
        """
        """
        if pos[0] >= rect[0] and pos[0] <= rect[0] + rect[2] and pos[1] >= rect[1] and pos[1] <= rect[1] + rect[3]:
               return True
        else:
            return False


    def entity_on(self, pos):
        """
        """
        result = False
        for entity in self.render.l_entities.get_layer(pos[1]).values():
            if entity.pos[0] == pos[0]:
                result = True
                break
        return result


    def process(self, cmd):
        """
        Process a command from Dana.

        Arguments:
        - `cmd`: command from Dana.
        """
        if cmd[0] == 'ROUND_START':
            self.round_state = 'CHOICE'
        elif cmd[0] == 'END_ROUND':
            self.round_state = 'NEXT_ROUND'
        elif cmd[0] == 'END_CHOICE':
            self.round_state = 'WAIT_ACTIONS'
            self.render.dest_square = None
            self.render.banner_fight = True
        elif cmd[0] == 'RENDER':
            self.round_state = 'RENDER'
            self.render.banner_fight = False
            # TODO(Mika) : lancer l'affichage du combat'
        elif cmd[0] == 'BATTLE_STATE':
            self.round_state = cmd[1].upper()
            if self.round_state != 'PLAYERS_CONNECTIONS':
                self.spec = True
        elif cmd[0] == 'ENTITY' or cmd[0] == 'NEW_ENTITY':
            f = open('data/'+cmd[1]+'.cfg')
            data = f.readline().split('**')
            f.close()
            try:
                self.render.register_entity(pos=(int(cmd[4]), int(cmd[5])), width=int(data[0]), height=int(data[1]),max_hp=int(cmd[6]),
                                            hp=int(cmd[7]), faction=int(cmd[2]), uid=int(cmd[3]), anim_path=data[2])
            except ValueError as e:
                print(e)
        elif cmd[0] == 'YOU':
            self.render.me = int(cmd[1])
            self.render.s_queue.put("GET_BATTLE_STATE")
        elif cmd[0] in ('ATTACK', 'MOVE', 'EFFECT'):
            try:
                self.fight[int(cmd[1])].append(cmd)
            except ValueError as e:
                print(e)


    def do_actions(self, pa):
        """
        """
        for cmd in self.fight[pa]
            if cmd[0] == 'MOVE':
               try:
                    self.render.l_entities[int(cmd[2])].move(dest=(int(cmd[3]), int(cmd[4])), speed=1)
                except ValueError as e:
                    print(e)
            elif cmd[0] == 'ATTACK':
                try:
                    self.render.l_entities[int(cmd[2])].play_anim(name=cmd[3], loop=False)
                except ValueError as e:
                    print(e)
        del self.fight[pa]
