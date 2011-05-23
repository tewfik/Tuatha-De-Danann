#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pygame
from pygame.locals import *
import pickle
sys.path.append("../shared/")
from area import Area
import entity
import ui
from locales import *


class Render():
    """
    Render engine.

    Display entities, map and catch mouse and keyboard input to transfer them to the event handler.
    """

    def __init__(self, send_queue, receive_queue):
        """
        Initialize the window's display.

        Attributes:
        - `font`: the font to use for texts.
        - `fps_render`: a boolean telling render to display fps or not.
        - `grid_render`: a boolean telling render to display the grid or not.
        - `l_entities`: list of entities currently on the map.
        - `UI`: the UI handler.
        - `s_queue`: the queue used to send commands to Dana.
        - `r_queue`: the queue used to receive commands from Dana.
        - `me`: uid of the entity controlled by the player.
        - `clock`: A pygame timer.
        """
        pygame.init()
        self.font = pygame.font.SysFont(None, 24)
        self.fps_render = False
        self.grid_render = False
        self.l_entities = entity.List()
        self.UI = ui.UI(self)
        self.s_queue = send_queue
        self.r_queue = receive_queue
        self.me = None
        self.clock = pygame.time.Clock()

        self.window = pygame.display.set_mode((WIDTH * SQUARE_SIZE, HEIGHT * SQUARE_SIZE), 0)
        pygame.display.set_caption(TITLE)
        self.s_queue.put('GET_ENTITIES')


    def run(self):
        """
        Main programm's loop (process, display and inputs).
        """

        while(True):
            self.UI.run()
            self.draw_world()
            self.draw_entities()
            self.draw_overlay()

            pygame.display.flip()
            self.clock.tick(FPS)


    def draw_overlay(self):
        """
        """
        if self.fps_render:
            # fps displaying
            text = self.font.render("%1.1f" % self.clock.get_fps(), False, (0, 0, 0))
            text_Rect = text.get_rect()
            text_Rect.right = WIDTH * SQUARE_SIZE - 18
            text_Rect.top = 2
            self.window.blit(text, text_Rect)
        # battle state displaying
        text = self.font.render(self.UI.round_state, False, (0, 0, 0))
        text_Rect = text.get_rect()
        text_Rect.left = 10
        text_Rect.top = 10
        self.window.blit(text, text_Rect)


    def draw_world(self):
        """
        Display the ground's tiles'.
        """
        for j in xrange(0, HEIGHT):
            top = j * SQUARE_SIZE
            for i in xrange(0, WIDTH):
                left = i * SQUARE_SIZE
                self.window.blit(self.area.tiles[self.area[j][i]], (left, top))
        if self.grid_render:
            for i in xrange(1, WIDTH):
                pygame.draw.line(self.window, (50, 50, 50), (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT * SQUARE_SIZE))
            for i in xrange(1, HEIGHT):
                pygame.draw.line(self.window, (50, 50, 50), (0, i * SQUARE_SIZE), (WIDTH * SQUARE_SIZE, i * SQUARE_SIZE))


    def register_entity(self, pos, width, height, hp, uid, anim_path):
        """
        Register a New graphic entity to the world.

        Arguments:
        - `pos`: a tuple (x, y) giving the coordinates where to spawn the entity.
        - `width`: the width of the entity (used for display only).
        - `height`: the height of the entity (used for display only).
        - `hp`: current and max hp of the entity.
        - `uid`: the unique id of the entity (int).
        - `anim_path`: the anim file of the entity.
        """
        self.l_entities.add_entity(pos, width, height, hp, uid, anim_path)


    def remove_entity(self, uid):
        """
        Remove a graphical entity from the world.
        """
        del self.l_entities[uid]


    def draw_entities(self):
        """
        Draw every entities on the map in their current state of animation.
        """
        for i in xrange(HEIGHT):
            layer = self.l_entities.get_layer(i)
            for entity in layer.values():
                image = entity.update()
                self.draw_entity_HUD(entity.faction_color, entity.hp, entity.max_hp, entity.pixel_pos, entity.height, entity.width)
                self.window.blit(image, entity.pixel_pos)


    def draw_entity_HUD(self, faction, hp, max_hp, pos, height, width):
        """
        """
        # select circle
        ellipse_Rect = (pos[0] + (width - SQUARE_SIZE)/ 2, pos[1] + height - 3 * SQUARE_SIZE / 4, SQUARE_SIZE, 3 * SQUARE_SIZE / 4)
        pygame.draw.ellipse(self.window, faction, ellipse_Rect , 2)

        # health bar
        self.window.fill((0, 0, 0, 200), (pos[0] + (width- SQUARE_SIZE) / 2 + 2, pos[1] - 10, SQUARE_SIZE - 4, 6))
        hp_ratio = hp/float(max_hp)
        self.window.fill((0, 200, 0), (pos[0] + (width - SQUARE_SIZE) / 2 + 2, pos[1] - 10, round(hp_ratio*(SQUARE_SIZE - 4)), 6))
        pygame.draw.rect(self.window, faction, (pos[0] + (width - SQUARE_SIZE) / 2 + 1, pos[1] - 11, SQUARE_SIZE - 2, 8), 1)


    def load_map(self, path):
        """
        Load the map and entities' informations from a file.

        Arguments:
        - `path`: the path to the save file of the map to load.
        """
        f_map = open(path, 'r')
        self.area = pickle.load(f_map)
        self.area.load_tiles()
        f_map.close()


    def play_music(self, path):
        """
        Load and play background music.

        Arguments:
        - `path`: path to the music file (ogg, wav, midi).
        """
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)


    def stop_music(self):
        """
        Stop the background music.
        """
        pygame.mixer.music.stop()


    def __del__(self):
        """
        Unload the display and exit the programm.
        """
        pygame.quit()
