import json
import os
from utils import save_path
from crypto import encrypt_save, decrypt_save

class Save:
    def __init__(self):
        pass

    @staticmethod
    def load_inventory(player):
        save_file = save_path("save.json")
        if os.path.exists(save_file):
            with open(save_file, "r+", encoding="utf-8") as f:
                save_data = json.load(f)
        else:
            save_data = {}
        
        inventory = save_data["inventory"]
        info = save_data["player_info"]

        for i in info:
            player.info[i] = info[i]

        for item in inventory:
            if item == "pokedex":
                player.inventory["pokedex"]["pokemons"] = inventory[item]["pokemons"]
                continue
            player.inventory[item] = inventory[item]
        
    @staticmethod
    def save_inventory(player):
        save_file = save_path("save.json")
        if os.path.exists(save_file):
            with open(save_file, "r+", encoding="utf-8") as f:
                save_data = json.load(f)
        else:
            save_data = {}

        for item in player.inventory:
            save_data["inventory"][item] = player.inventory[item]
        
        for i in player.info:
            save_data["player_info"][i] = player.info[i]
        
        with open(save_file, "w+", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)