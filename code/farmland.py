from pokemon import Pokemon
from pokeball import Pokeball
from fight import Fight
from save import Save
import random
import pygame

class FarmLand:
    def __init__(self):
        self.pokemons = {
            "pikachu": {
                "droprate": 60
            },
        }
        self.spawned_pokemons: dict[Pokemon, int, str | None, int, str] = {}
        self.is_poked = False
        self.fighting = False

    def spawn_pokemon(self, group, collisions):
        pokemon_names = list(self.pokemons.keys())
        for i in range(40):
            pokemon_name = pokemon_names[random.randint(0, len(pokemon_names) - 1)]
            pokemon = Pokemon(pokemon_name, 1)
            pokemon.spawn_pokemon()
            pokemon.entity.collisions = collisions
            pokemon.entity.dt = 0.01
            self.pokeball = None
            coordinates = [random.randint(0, 100 * 16), random.randint(0, 100 * 16)]
            pokemon.entity.rect.topleft = coordinates
            self.spawned_pokemons[str(i)] = {"pokemon": pokemon, "id": i, "move": None, "droprate": self.pokemons[pokemon_name]["droprate"], "name": pokemon_name}
            group.add(pokemon.entity)
        self.spawned_move()
        return self.spawned_pokemons

    def spawned_move(self):
        for pokemon in self.spawned_pokemons:
            self.spawned_pokemons[pokemon]["pokemon"].entity.rect.y += 1
            a = int(self.spawned_pokemons[pokemon]["id"] % 4)
            if a == 0:
                self.spawned_pokemons[pokemon]["move"] = "down"
            elif a == 1:
                self.spawned_pokemons[pokemon]["move"] = "up"
            elif a == 2:
                self.spawned_pokemons[pokemon]["move"] = "left"
            elif a == 3:
                self.spawned_pokemons[pokemon]["move"] = "right"

    def move_pokemons(self):
        if not self.fighting:
            for pokemon in self.spawned_pokemons:
                if self.spawned_pokemons[pokemon]["move"] == "right":
                    self.spawned_pokemons[pokemon]["pokemon"].entity.move_right()
                    if not self.spawned_pokemons[pokemon]["pokemon"].entity.check_collision():
                        self.spawned_pokemons[pokemon]["pokemon"].entity.rect.x += self.spawned_pokemons[pokemon]["pokemon"].entity.speed
                    else:
                        self.change_direction(pokemon)
                elif self.spawned_pokemons[pokemon]["move"] == "left":
                    self.spawned_pokemons[pokemon]["pokemon"].entity.move_left()
                    if not self.spawned_pokemons[pokemon]["pokemon"].entity.check_collision():
                        self.spawned_pokemons[pokemon]["pokemon"].entity.rect.x -= self.spawned_pokemons[pokemon]["pokemon"].entity.speed
                    else:
                        self.change_direction(pokemon)
                elif self.spawned_pokemons[pokemon]["move"] == "up":
                    self.spawned_pokemons[pokemon]["pokemon"].entity.move_up()
                    if not self.spawned_pokemons[pokemon]["pokemon"].entity.check_collision():
                        self.spawned_pokemons[pokemon]["pokemon"].entity.rect.y -= self.spawned_pokemons[pokemon]["pokemon"].entity.speed
                    else:
                        self.change_direction(pokemon)
                elif self.spawned_pokemons[pokemon]["move"] == "down":
                    self.spawned_pokemons[pokemon]["pokemon"].entity.move_down()
                    if not self.spawned_pokemons[pokemon]["pokemon"].entity.check_collision():
                        self.spawned_pokemons[pokemon]["pokemon"].entity.rect.y += self.spawned_pokemons[pokemon]["pokemon"].entity.speed
                    else:
                        self.change_direction(pokemon)
        else:
            self.figth.draw_fight()
            if self.figth.is_over:
                self.fighting = False
                self.figth = None
                self.is_poked = False
    
    def change_direction(self, pokemon):
        a = random.randint(1, 4)
        if self.spawned_pokemons[pokemon]["move"] == "down":
            if a == 1:
                self.spawned_pokemons[pokemon]["move"] = "right"
            elif a == 2:
                self.spawned_pokemons[pokemon]["move"] = "up"
            elif a == 3:
                self.spawned_pokemons[pokemon]["move"] = "left"
        elif self.spawned_pokemons[pokemon]["move"] == "up":
            if a == 1:
                self.spawned_pokemons[pokemon]["move"] = "down"
            elif a == 2:
                self.spawned_pokemons[pokemon]["move"] = "up"
            elif a == 3:
                self.spawned_pokemons[pokemon]["move"] = "left"
        elif self.spawned_pokemons[pokemon]["move"] == "left":
            if a == 1:
                self.spawned_pokemons[pokemon]["move"] = "down"
            elif a == 2:
                self.spawned_pokemons[pokemon]["move"] = "up"
            elif a == 3:
                self.spawned_pokemons[pokemon]["move"] = "right"
        elif self.spawned_pokemons[pokemon]["move"] == "right":
            if a == 1:
                self.spawned_pokemons[pokemon]["move"] = "down"
            elif a == 2:
                self.spawned_pokemons[pokemon]["move"] = "up"
            elif a == 3:
                self.spawned_pokemons[pokemon]["move"] = "left"

    def check_pokeball_hit(self, group, player, keylogs):
        if self.pokeball is not None and not self.fighting:
            for pokemon in self.spawned_pokemons:
                if self.spawned_pokemons[pokemon]["pokemon"].entity.rect.colliderect(self.pokeball):
                    group.remove(self.spawned_pokemons[pokemon]["pokemon"].entity)
                    self.spawned_pokemons[pokemon]["pokemon"].entity.kill()
                    self.fighting = True
                    self.figth = Fight("pokemon", player_pokedex=player.inventory["pokedex"],ennemi_pokemons=[self.spawned_pokemons[pokemon]["pokemon"]], screen=pygame.display.get_surface(), keys=keylogs)
                    self.spawned_pokemons.pop(str(pokemon))
                    break

    def throw_pokeball(self, player, player_pos, group):
        if player.inventory["pokeball"] > 0 and not self.is_poked:
            player.inventory["pokeball"] -= 1
            Save.save_inventory(player)
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            screen_center = pygame.Vector2(640, 390)
            direction = mouse_pos - screen_center
            self.pokeball = Pokeball(player_pos, direction)
            self.is_poked = True
            group.add(self.pokeball)
        else:
            if self.pokeball:
                self.is_poked = self.pokeball.is_poked