import pytmx
import pyscroll
import pygame

from screen import Screen
from player import Player
from pokemon import Pokemon
from npc import NPC
from keylogs import Keylogs
from farmland import FarmLand
from utils import resource_path
from quest import Quest

class Map:
    def __init__(self, screen: Screen, map, keylogs: Keylogs):
        self.screen: Screen = screen
        self.keylogs: Keylogs = keylogs
        self.map: str = map
        self.tmx_data: pytmx.TiledMap | None = None
        self.map_data: pyscroll.TiledMapData | None = None
        self.map_layer: pyscroll.orthographic.BufferedRenderer | None = None
        self.group: pyscroll.PyscrollGroup | None = None
        self.player_spawn: tuple[int] | None= None
        self.collisions: list[pygame.rect.Rect] | None = None
        self.tps: list[dict[pygame.rect.Rect, str]] | None = None
        self.npcs: dict[NPC] = {}
        self.player: Player | None = None
        self.pokedex_active: bool = False
        self.selected_pokemon: Pokemon | None = None
        self.active_pokemon: bool = False
        self.active_quests: bool = False
        self.farmland: FarmLand | None = None
        self.load_map(map)

    def load_map(self, map: str):
        self.tmx_data = pytmx.load_pygame(resource_path(f"venv/assets/map/{map}.tmx"))
        self.collisions = self.get_collisions()
        self.player_spawn = self.get_spawn()
        self.map = map
        self.tps = self.get_tps()
        self.map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(self.map_data, (1280, 780))
        self.zoom_map(map)
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=3)
        self.add_npcs()
        if self.player:
            self.add_player(self.player)
            self.player.action = f"Enter [{self.map}]"
            self.player.quest.check_quest_done(self.player.action)
        if map == "farmland":
            self.farmland = FarmLand()
            self.farmland.spawn_pokemon(self.group, self.collisions)

    def handle_farmland_update(self):
        if self.map == "farmland":
            self.farmland.move_pokemons()
            self.farmland.check_pokeball_hit(self.group, self.player, self.keylogs)
            

    def handle_item_action(self):
            if self.map == "farmland":
                if self.keylogs.is_pressed(pygame.K_f):
                    self.farmland.throw_pokeball(self.player, self.player.rect.center, self.group)
                    self.keylogs.remove_key(pygame.K_f)
        
    def get_collisions(self):
        collisions: list[pygame.rect.Rect] = []
        for obj in self.tmx_data.objects:
            if obj.name == "collision":
                collisions.append(pygame.rect.Rect(obj.x, obj.y, obj.width, obj.height))
        return collisions

    def zoom_map(self, map):
        if map.startswith("house"):
            self.map_layer.zoom = 5
        elif map.startswith("hospital"):
            self.map_layer.zoom = 4
        else:
            self.map_layer.zoom = 3
        
    def get_tps(self):
        tps: list[dict[pygame.rect.Rect, str]] = []
        for obj in self.tmx_data.objects:
            if str(obj.name).split(" ")[0] == "tp":
                tps.append({
                    "rect": pygame.rect.Rect(obj.x, obj.y, obj.width, obj.height),
                    "name": str(obj.name).split(" ")[1]
                })
        return tps
    
    def update(self):
        self.group.update()
        self.group.center(self.player.rect)
        self.group.draw(self.screen.get_display())
        self.npc_hit()
        self.appear_pokemon()
        self.handle_farmland_update()
        self.handle_item_action()
        
        if self.keylogs.is_pressed(pygame.K_h):
            self.pokedex_active = not self.pokedex_active
            self.player.can_move = not self.player.can_move
            self.keylogs.remove_key(pygame.K_h)
        elif self.pokedex_active:
            self.player.inventory["pokedex"].draw_pokedex(self.keylogs)
            self.player.can_move = False
        elif self.keylogs.is_pressed(pygame.K_t):
            self.active_quests = not self.active_quests
            self.player.can_move = not self.player.can_move
            self.keylogs.remove_key(pygame.K_t)
        elif self.active_quests:
            self.player.quest.draw_quests()
            self.player.can_move = False
        
        
    def get_spawn(self):
        for obj in self.tmx_data.objects:
            if str(obj.name).endswith(self.map) and str(obj.name).startswith("spawn"):
                return [int(obj.x,) + obj.width // 2, int(obj.y) + obj.height // 2]
        for obj in self.tmx_data.objects:
            if obj.name == "player_spawn":
                return [int(obj.x) + obj.width // 2, int(obj.y) + obj.height // 2]
        
    def add_player(self, player: Player):
        self.player: Player = player
        self.player.add_collisions(self.collisions)
        self.player.rect.center = self.player_spawn
        if self.player.pokemon:
            self.selected_pokemon = self.player.pokemon
        self.group.add(player)
    
    def appear_pokemon(self):
        if not self.selected_pokemon:
            if self.player.inventory["pokedex"]["pokemons"]:
                first_pokemon_name = list(self.player.inventory["pokedex"]["pokemons"].keys())[0]
                self.player.pokemon = Pokemon(first_pokemon_name, self.player.inventory["pokedex"]["pokemons"][first_pokemon_name]["stats"]["level"])
                self.selected_pokemon = self.player.pokemon
                self.add_pokemon()
        if not self.active_pokemon:
            if self.keylogs.is_pressed(pygame.K_e):
                self.add_pokemon()
                self.keylogs.remove_key(pygame.K_e)
        else:
            if self.keylogs.is_pressed(pygame.K_e):
                self.remove_pokemon()
                self.keylogs.remove_key(pygame.K_e)
    
    def check_tp(self):
        for tp in self.tps:
            if self.player.rect.colliderect(tp["rect"]):
                self.load_map(tp["name"])

    def add_pokemon(self):
        if self.player.pokemon:
            self.group.add(self.selected_pokemon.spawn_pokemon(),layer=2)
            self.active_pokemon = True
            self.selected_pokemon.entity.rect.left = self.player.rect.right
            self.selected_pokemon.entity.rect.top = self.player.rect.top
            self.selected_pokemon.entity.add_collisions(self.collisions)
    
    def remove_pokemon(self):
        self.group.remove(self.player.pokemon.entity)
        self.active_pokemon = False
    
    def add_npcs(self):
        for obj in self.tmx_data.objects:
            if str(obj.name).startswith("pnj"):
                npc_name = str(obj.name).split(" ")[1]
                self.npcs[npc_name] = NPC(f"sprite/{npc_name}_{self.map}.png", 4, 4, npc_name)
                self.collisions.append(self.npcs[npc_name].hitbox)
                self.group.add(self.npcs[npc_name], layer=1)
                self.npcs[npc_name].rect.center = [obj.x + obj.width // 2, obj.y + obj.height // 2]
                self.npcs[npc_name].align_hitbox()
    
    def npc_hit(self):
        for npc in self.npcs:
            if self.npcs[npc].rect.colliderect(self.player.rect):
                self.npcs[npc].active_dialogue(self.keylogs, self.screen.get_display(), self.player)
                if self.npcs[npc].dialogue_active:
                    self.player.can_move = False
                    self.map_layer.zoom = 5
                else:
                    self.player.can_move = True
                    self.map_layer.zoom = 3
            elif self.npcs[npc].dialogue_active:
                self.npcs[npc].dialogue_active = False
                self.map_layer.zoom = 3
