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
        - `menu_font`: the font to use for menus.
        - `banner_font`: the font to use for banners.
        - `speech_font`: the font to use for speech bubbles.
        - `fps_render`: a boolean telling render to display fps or not.
        - `grid_render`: a boolean telling render to display the grid or not.
        - `menu`: a boolean telling render to display the menu or not.
        - `l_entities`: list of entities currently on the map.
        - `UI`: the UI handler.
        - `s_queue`: the queue used to send commands to Dana.
        - `r_queue`: the queue used to receive commands from Dana.
        - `me`: uid of the entity controlled by the player.
        - `dest_square`: The square the player wants to move to.
        - `clock`: A pygame timer.
        - `bubbles`: A dictionnary of all bubbles currently displaying.
        - `cursor`: current cursor used.
        """
        pygame.init()
        self.font = pygame.font.SysFont(None, 24)
        self.menu_font = pygame.font.SysFont(None, 16)
        self.banner_font = pygame.font.SysFont(None, 128)
        self.speech_font = pygame.font.SysFont("Monospace", 12)
        self.speech_font.set_bold(True)
        self.fps_render = False
        self.grid_render = False
        self.menu = False
        self.banner_fight = False
        self.l_entities = entity.List()
        self.UI = ui.UI(self)
        self.s_queue = send_queue
        self.r_queue = receive_queue
        self.me = None
        self.dest_square = None
        self.clock = pygame.time.Clock()
        self.bubbles = {}

        self.window = pygame.display.set_mode((WIDTH, HEIGHT), 0)
        pygame.display.set_caption(TITLE)
        self.cursor = "arrow"
        self.use_cursor(ARROW)
        self.s_queue.put('GET_ENTITIES')


    def run(self):
        """
        Main programm's loop (process, display and inputs).
        """
        gear = pygame.image.load("sprites/gear.png")
        while(True):
            self.UI.run()
            self.draw_world()
            self.draw_entities()
            self.draw_overlay()
            self.window.blit(gear, (WIDTH - 18, 2))

            pygame.display.flip()
            self.clock.tick(FPS)


    def draw_overlay(self):
        """
        """
        # fps displaying
        if self.fps_render:
            self.text("%1.1f" % self.clock.get_fps(), top = 2, right = WIDTH - 18)

        # battle state displaying
        self.text(self.UI.round_state, left = 10, top = 10)

        if self.banner_fight:
            self.window.fill(BEIGE, (0, 200, WIDTH, HEIGHT - 400))
            self.text("FIGHT !", font=self.banner_font, centerx=WIDTH / 2, centery=HEIGHT / 2, color=RED)

        # Speech bubbles
        del_uid = None
        for uid in self.bubbles:
            bubble = self.bubbles[uid]
            ent = self.l_entities[bubble[0]]
            pos = (ent.pixel_pos[0] + ent.width, ent.pixel_pos[1])
            pygame.draw.polygon(self.window, WHITE, ((pos[0] - 5, pos[1] + 10), (pos[0] + 40, pos[1] - 20), (pos[0] + 15, pos[1] - 20)))
            pygame.draw.ellipse(self.window, WHITE, (pos[0] - 10, pos[1] - 50, 100, 50))
            self.text(bubble[1], self.speech_font, top=pos[1] - 35, left=pos[0] + 5, alias=False)
            bubble[2] -= 1
            if bubble[2] <= 0:
                del_uid = uid
        if del_uid is not None:
            del self.bubbles[del_uid]

        # Menu display
        if self.menu:
            menu_x = (WIDTH - MENU_WIDTH) / 2
            menu_y = (HEIGHT - MENU_HEIGHT) / 2
            self.window.fill(GREY, (menu_x, menu_y, MENU_WIDTH, MENU_HEIGHT))

            X = menu_x + MENU_WIDTH - 10
            Y = menu_y + 9
            pygame.draw.polygon(self.window, RED, ((X - 2, Y), (X - 6, Y - 4), (X - 4, Y - 6), (X, Y - 2), (X + 4, Y - 6), (X + 6, Y - 4),
                                                   (X + 2, Y), (X + 6, Y + 4), (X + 4, Y + 6), (X, Y + 2), (X - 4, Y + 6), (X - 6, Y + 4)))
            self.window.fill(WHITE, (menu_x + 30, menu_y + 50, 10, 10))
            self.window.fill(WHITE, (menu_x + 30, menu_y + 90, 10, 10))
            if self.grid_render:
                self.window.fill(BLACK, (menu_x + 32, menu_y + 52, 6, 6))
            if self.fps_render:
                self.window.fill(BLACK, (menu_x + 32, menu_y + 92, 6, 6))

            self.text("Afficher la grille.", self.menu_font, top=menu_y + 50, left=menu_x + 50)
            self.text("Afficher les IPS.", self.menu_font, top=menu_y + 90, left=menu_x + 50)


    def text(self, msg, font=None, top=None, right=None, left=None, bottom=None, centerx=None, centery=None, color=(0, 0, 0), alias=True):
        """
        """
        if font is None:
            font = self.font
        text = font.render(msg, alias, color)
        text_Rect = text.get_rect()

        if top is not None:
            text_Rect.top = top
        elif bottom is not None:
            text_Rect.bottom = bottom
        else:
            text_Rect.centerx = centerx
        if right is not None:
            text_Rect.right = right
        elif left is not None:
            text_Rect.left = left
        else:
            text_Rect.centery = centery

        self.font = pygame.font.SysFont(None, 24)
        self.window.blit(text, text_Rect)


    def draw_world(self):
        """
        Display the ground's tiles'.
        """
        for j in xrange(0, ROWS):
            top = j * SQUARE_SIZE
            for i in xrange(0, COLUMNS):
                left = i * SQUARE_SIZE
                self.window.blit(self.area.tiles[self.area[j][i]], (left, top))
        if self.grid_render:
            for i in xrange(1, COLUMNS):
                pygame.draw.line(self.window, (50, 50, 50), (i * SQUARE_SIZE, 0), (i * SQUARE_SIZE, HEIGHT))
            for i in xrange(1, ROWS):
                pygame.draw.line(self.window, (50, 50, 50), (0, i * SQUARE_SIZE), (WIDTH, i * SQUARE_SIZE))
        if self.dest_square is not None:
            self.window.fill(BLUE, self.dest_square)


    def register_entity(self, pos, width, height, max_hp, hp, faction, uid, anim_path):
        """
        Register a New graphic entity to the world.

        Arguments:
        - `pos`: a tuple (x, y) giving the coordinates where to spawn the entity.
        - `width`: the width of the entity (used for display only).
        - `height`: the height of the entity (used for display only).
        - `max_hp`: max hp of the entity.
        - `hp`: current hp of the entity.
        - `faction`: the identifier of the faction the entity belongs to.
        - `uid`: the unique id of the entity (int).
        - `anim_path`: the anim file of the entity.
        """
        self.l_entities.add_entity(pos, width, height, max_hp, hp, faction, uid, anim_path)


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
                self.draw_entity_HUD(entity.faction, entity.hp, entity.max_hp, entity.pixel_pos, entity.height, entity.width)
                self.window.blit(image, entity.pixel_pos)


    def draw_entity_HUD(self, faction, hp, max_hp, pos, height, width):
        """
        """
        if faction != NEUTRE:
            # select circle
            ellipse_Rect = (pos[0] + (width - SQUARE_SIZE)/ 2, pos[1] + height - 3 * SQUARE_SIZE / 4, SQUARE_SIZE, 3 * SQUARE_SIZE / 4)
            pygame.draw.ellipse(self.window, FACTION_COLOR[faction], ellipse_Rect , 2)

            # health bar
            self.window.fill((0, 0, 0, 200), (pos[0] + (width- SQUARE_SIZE) / 2 + 2, pos[1] - 10, SQUARE_SIZE - 4, 6))
            hp_ratio = hp/float(max_hp)
            self.window.fill(GREEN, (pos[0] + (width - SQUARE_SIZE) / 2 + 2, pos[1] - 10, round(hp_ratio*(SQUARE_SIZE - 4)), 6))
            pygame.draw.rect(self.window, FACTION_COLOR[faction], (pos[0] + (width - SQUARE_SIZE) / 2 + 1, pos[1] - 11,
                                                                             SQUARE_SIZE - 2, 8), 1)


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


    def use_cursor(self, name):
        """
        """
        self.cursor, cursor = name
        hotspot = None
        for y in range(len(cursor)):
            for x in range(len(cursor[y])):
                if cursor[y][x] in ['x', ',', 'O']:
                    hotspot = x,y
                    break
            if hotspot != None:
                break
        if hotspot == None:
            raise Exception("No hotspot specified for cursor !")
        s = []
        for line in cursor:
            s.append(line.replace('x', 'X').replace(',', '.').replace('O', 'o'))
        curs, mask = pygame.cursors.compile(s)
        size = len(cursor[0]), len(cursor)
        pygame.mouse.set_cursor(size, hotspot, curs, mask)



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
