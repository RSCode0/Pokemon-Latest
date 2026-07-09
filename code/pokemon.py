from entities import PokemonEntity

import json
from utils import resource_path

class Pokemon(dict):
    def __init__(self, name: str, level: int = 1):
        super().__init__()
        self["name"] = name
        self["stats"] = None
        self.get_stats()
        self["stats"]["level"] = level
        self.entity = None

    def get_stats(self):
        with open(resource_path("venv/code/json/pokemon_gen1.json"), encoding="utf-8") as file:
            data_pokemons = json.load(file)
            self["stats"] = data_pokemons[self["name"]]
            
    def spawn_pokemon(self):
        self.entity = PokemonEntity(f"/pokemons/{self['name']}.png", 4, 4)
        return self.entity