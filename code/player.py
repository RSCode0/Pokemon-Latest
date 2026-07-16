import pygame

from entities import Entity
from keylogs import Keylogs
from pokemon import Pokemon
from inventory import Inventory
from quest import Quest

class Player(Entity):
    def __init__(self, spritesheet: str, rows: int, cols: int, keylogs: Keylogs):
        super().__init__(spritesheet, rows, cols)
        self.pokemon: Pokemon | None = None
        self.companion = None
        self.keylogs: Keylogs = keylogs
        self.inventory: Inventory = Inventory()
        self.can_move = True
        self.pokemon_can_move = False
        self.player_last_direction = "down"
        self.quest = Quest(self.keylogs)
        self.info = {
            "level": 0,
            "name": ""
        }

    def update(self):
        super().update()
        if self.can_move:
            self.check_input()
            moved = self.move()
            if moved and moved.split(",")[0] == "moved" and self.pokemon:
                self.companion.direction = moved.split(",")[1]
                self.pokemon_can_move = True
                self.companion.moving = True
        if self.pokemon and self.pokemon.entity:
            self._update_companion()

    def _update_companion(self):
        self.companion = self.pokemon.entity
        self.companion.dt = self.dt
        self.companion.hitbox.bottomleft = self.companion.rect.bottomleft
        if self.pokemon_can_move:
            self.companion.move()
        else:
            self.companion.image = self.companion.frames[self.direction][0]

    def check_input(self):
        if self.moving:
            return

        if self.keylogs.is_pressed(pygame.K_z):
            self._try_move("up")
        elif self.keylogs.is_pressed(pygame.K_s):
            self._try_move("down")
        elif self.keylogs.is_pressed(pygame.K_q):
            self._try_move("left")
        elif self.keylogs.is_pressed(pygame.K_d):
            self._try_move("right")
        else:
            self.image = self.frames[self.direction][0]