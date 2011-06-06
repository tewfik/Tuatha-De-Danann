#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../shared/")
from collections import deque
import pygame
from pygame.locals import *
from locales import *
from astar import Astar

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
        - `buffer_pa`: a list storing actions before sending them to Dana.
        - `chat_history`: a list storing chat log.
        - `names`: list of clients nicknames.
        - `map`: client-side map impassable square.
        """
        self.render = render
        self.round_state = None
        self.confirm = False
        self.alt = False
        self.spec = False
        self.fight = {}
        self.pa = 0
        self.buffer_pa = deque()
        self.chat_history = []
        self.names = {}
        self.map = [[0]*COLUMNS for i in xrange(ROWS)]
        f = open("../shared/village.collide", 'r')
        for i in xrange(ROWS):
            line = f.readline()[:-1]
            row = line.split(' ')
            for j in xrange(COLUMNS):
                self.map[i][j] = int(row[j])
        f.close()


    def run(self):
        """
        Get the events currently in the queue and add new event to the send queue.
        """
        while not self.render.r_queue.empty():
            cmd = self.render.r_queue.get()
            self.process(cmd.split(':'))

        if self.round_state == 'RENDER':
            if self.render.end_anims():
                if self.pa in self.fight:
                    self.do_actions(self.pa)
                    self.pa += 1
                else:
                    self.round_state = 'NEXT_ROUND'
                    self.render.s_queue.put('RENDER_OK')
                    self.pa = 0
                    self.render.banner_next = True

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
                elif event.key == K_RETURN and self.round_state not in ('LOSE', 'WIN'):
                    if self.render.chat[0]:
                        self.render.chat[1].strip()
                        if self.render.chat[1]:
                            self.render.s_queue.put('CHAT_MSG:%s' % self.render.chat[1])
                        self.render.chat = [False, '', 0]
                    else:
                        self.render.chat[0] = True
                elif self.render.chat[0]:
                    if event.key in DICT:
                        self.render.chat[1] += DICT[event.key]
                    elif event.key == K_BACKSPACE:
                        self.render.chat[1] = self.render.chat[1][:-1]
            elif event.type == KEYUP:
                if event.key == K_LALT:
                    self.alt = False
            elif self.round_state in ('LOSE', 'WIN'):
                return
            else:
                self.mouse_event(event)


    def mouse_event(self, event):
        """
        """
        if event.type == MOUSEBUTTONDOWN:
            mouse_pos = (event.pos[0] / SQUARE_SIZE, event.pos[1] / SQUARE_SIZE)
            if self.mouse_over((WIDTH - 18, 0, 18, 18), event.pos):
                self.render.menu = not self.render.menu
            elif not self.render.menu and event.button == 1:
                if self.round_state == 'CHOICE' and not self.spec and self.render.l_entities[self.render.me].alive:
                    if self.reachable(mouse_pos, MELEE_RANGE) and self.entity_on(mouse_pos) is not None:
                        if self.entity_on(mouse_pos).alive and self.render.target is None:
                            self.buffer_pa.append('ATTACK:attack:%d:%d' % mouse_pos)
                            self.render.target = self.render.l_entities.get_by_pos(mouse_pos)
                    elif self.mouse_over((20, HEIGHT - 40, 90, 20), event.pos):
                        self.buffer_pa.clear()
                        self.render.path = None
                        self.render.target = None
                    elif self.mouse_over((20, HEIGHT - 70, 90, 20), event.pos):
                        while len(self.buffer_pa):
                            self.render.s_queue.put(self.buffer_pa.popleft())
                        self.render.s_queue.put("CONFIRM_CHOICE")
                        self.confirm = True
                    elif self.render.path is None and self.reachable(mouse_pos, MOVE_DIST):
                        self.buffer_pa.append('MOVE:%d:%d' % mouse_pos)
                        start_pos = self.render.l_entities[self.render.me].pos
                        self.render.path = (Astar(self.get_collide_map(), start_pos, mouse_pos, [0], [BLOCK]))
                elif self.round_state == 'PLAYERS_CONNECTION' and self.mouse_over(((WIDTH - 200)/2,
                     (HEIGHT - 50)/2, 200, 50), event.pos) and not self.render.rdy:
                    self.render.rdy = True
                    self.render.s_queue.put("READY_TO_PLAY")
            else:
                menu_x = (WIDTH - MENU_WIDTH) / 2
                menu_y = (HEIGHT - MENU_HEIGHT) / 2
                if self.mouse_over((menu_x + 30, menu_y + 50, 10, 10), event.pos):
                    self.render.grid_render = not self.render.grid_render
                elif self.mouse_over((menu_x + 30, menu_y + 90, 10, 10), event.pos):
                    self.render.fps_render = not self.render.fps_render
                elif self.mouse_over((menu_x + MENU_WIDTH - 16, menu_y + 3, 13, 13), event.pos):
                    self.render.menu = not self.render.menu
                elif self.mouse_over((menu_x + 410, menu_y + 270, 82, 20), event.pos):
                    pygame.event.post(pygame.event.Event(QUIT, {}))
        elif event.type == MOUSEMOTION and self.render.me is not None:
            mouse_pos = (event.pos[0] / SQUARE_SIZE, event.pos[1] / SQUARE_SIZE)
            if self.reachable(mouse_pos, MELEE_RANGE) and self.entity_on(mouse_pos) is not None and self.round_state == 'CHOICE':
                if self.entity_on(mouse_pos).alive:
                    self.render.use_cursor(SWORD)
            elif self.render.cursor != ARROW[0]:
                self.render.use_cursor(ARROW)


    def get_collide_map(self):
        """
        """
        map = [[0]* COLUMNS for i in xrange(ROWS)]
        for i in xrange(ROWS):
            for j in xrange(COLUMNS):
                map[i][j] = self.map[i][j]
        for entity in self.render.l_entities.values():
            x = entity.pos[0]
            y = entity.pos[1]
            if x > 0 and x < COLUMNS and y > 0 and y < ROWS:
                map[y][x] = BLOCK
        return map

    def reachable(self, pos, range):
        """
        """
        entity = self.render.l_entities[self.render.me]
        if self.map[pos[1]][pos[0]] == BLOCK:
            return False
        elif abs(entity.pos[0] - pos[0]) + abs(entity.pos[1] - pos[1]) <= range:
            return True
        else:
            return False

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
        return self.render.l_entities.get_by_pos(pos)


    def is_facing(self, entity, pos):
        """
        """
        dir = (entity.pos[0] - pos[0], entity.pos[1] - pos[1])
        if dir[1] > 0:
            return 'up'
        if dir[0] > 0:
            return 'left'
        if dir[0] < 0:
            return 'right'
        else:
            return 'down'


    def process(self, cmd):
        """
        Process a command from Dana.

        Arguments:
        - `cmd`: command from Dana.
        """
        if cmd[0] == 'ROUND_START':
            self.fight = {}
            self.round_state = 'CHOICE'
            self.render.start_choice = pygame.time.get_ticks()
            self.confirm = False
            self.render.banner_next = False
        elif cmd[0] == 'END_ROUND':
            self.round_state = 'NEXT_ROUND'
        elif cmd[0] == 'END_CHOICE':
            self.round_state = 'WAIT_ACTIONS'
            self.render.path = None
            self.render.target = None
            self.render.banner_fight = True
            self.buffer_pa.clear()
        elif cmd[0] == 'RENDER':
            self.round_state = 'RENDER'
            self.render.banner_fight = False
        elif cmd[0] == 'BATTLE_STATE':
            self.round_state = cmd[1].upper()
            if self.round_state != 'PLAYERS_CONNECTION':
                self.spec = True
        elif cmd[0] == 'ENTITY' or cmd[0] == 'NEW_ENTITY':
            f = open('data/'+cmd[1]+'.cfg')
            data = f.readline().split('**')
            f.close()
            self.names[cmd[3]] = cmd[4]
            try:
                self.render.l_entities[int(cmd[3])] = ((int(cmd[5]), int(cmd[6])), int(data[0]), int(data[1]), int(cmd[7]), int(cmd[8]),
                                                       int(cmd[2]), data[2])
            except ValueError as e:
                print(e)
        elif cmd[0] == 'YOU':
            self.render.me = int(cmd[1])
            self.render.s_queue.put("GET_BATTLE_STATE")
        elif cmd[0] == 'CHAT_MSG':
            self.render.bubbles[int(cmd[1])] = [int(cmd[1]), cmd[2], BUBBLE_TTL]
            self.chat_history.append(self.names[cmd[1]] + ' : ' + cmd[2])
            if len(self.chat_history) > HISTORY_SIZE:
                del self.chat_history[0]
        elif cmd[0] in ('ATTACK', 'MOVE', 'EFFECT'):
            if int(cmd[1]) in self.fight:
                self.fight[int(cmd[1])].append(cmd)
            else:
                self.fight[int(cmd[1])] = [cmd]
        elif cmd[0] == 'SET':
            if cmd[1] == 'nickname':
                self.names[cmd[2]] = cmd[3]
        elif cmd[0] == 'END_GAME':
            self.render.banner_fight = False
            self.render.banner_next = False
            if self.render.l_entities[self.render.me].faction == int(cmd[1]):
                self.round_state = 'WIN'
            else:
                self.round_state = 'LOSE'


    def do_actions(self, pa):
        """
        """
        for cmd in self.fight[pa]:
            if cmd[0] == 'MOVE':
                try:
                    self.render.l_entities[int(cmd[2])].move(dest=(int(cmd[3]), int(cmd[4])), speed=1)
                except ValueError as e:
                    print(e)
            elif cmd[0] == 'ATTACK':
                try:
                    entity = self.render.l_entities[int(cmd[2])]
                    entity.play_anim(name=cmd[3]+'_'+self.is_facing(entity, (int(cmd[4]), int(cmd[5]))), loop=False)

                    target = self.entity_on((int(cmd[4]), int(cmd[5])))
                    uid = self.render.get_uid(target)
                    if cmd[3] == 'attack':
                        self.render.effect(type='blow', id=int(cmd[2]), target_id=uid)
                    elif cmd[3] == 'pyrotechnic':
                        self.render.effect(type='pyrotechnic', id=int(cmd[2]), target_id=uid)
                except ValueError as e:
                    print(e)
            elif cmd[0] == 'EFFECT':
                self.render.effect(type=cmd[3], id=int(cmd[2]), target_id=int(cmd[4]), params=cmd[5:])
        del self.fight[pa]
