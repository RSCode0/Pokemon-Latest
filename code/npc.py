from entities import Entity
import pygame
import json
import os

from fight import Fight
from pokemon import Pokemon
from keylogs import Keylogs
from assets.choice import Choice
from save import Save
from utils import resource_path, save_path

class NPC(Entity):
    def __init__(self, spritesheet, rows, cols, name):
        super().__init__(spritesheet, rows, cols)
        self.name: str = name
        self.player = None
        self.player_inventory = None
        self.screen = None
        self.keylogs: Keylogs | None = None
        self.font = pygame.font.Font(resource_path("venv/assets/fonts/Agdasima-Regular.ttf"), 25)
        self.last_dialogue_id = ""
        self.missing_flags = False
        self.dialogues = []
        self.speakers = []
        self.speakers_image = {}
        self.dialogue_index = 0
        self.npc_turn = True
        self.is_condition = False
        self.dialogue_active = False
        self.can_start = False
        self.current_text = ""
        self.current_speaker = ""
        self.condition = ""
        self.choice = False
        self.choiced = False
        self.figth = None
        self.figthed = False
        self.action = ""
        self.typewriter_index = 0
        self.typewriter_speed = 20
        self.last_typewriter_time = 0
        
    def active_dialogue(self, keylogs: Keylogs, screen, player):
        self.player = player
        self.player_inventory = self.player.inventory
        self.keylogs = keylogs
        self.screen = screen
        if self.dialogue_active:
            current_time = pygame.time.get_ticks()
            if self.typewriter_index < len(self.current_text):
                if current_time - self.last_typewriter_time > self.typewriter_speed:
                    self.typewriter_index += 1
                    self.last_typewriter_time = current_time
            if self.missing_flags: 
                if keylogs.is_pressed(pygame.K_SPACE):
                    self.dialogue_active = False
            if self.figth:
                self.figth.draw_fight()
                if self.figth.is_over:
                    self.figth = None
                    self.figthed = True
                    self.advance_dialogue()
                return
            self.draw_current_dialogue(screen)
            if self.choice and not self.choiced:
                self.choice.draw_choices()
                self.choiced = self.choice.choiced
                return
            if keylogs.is_pressed(pygame.K_SPACE):
                if self.typewriter_index < len(self.current_text):
                    self.typewriter_index = len(self.current_text)
                    keylogs.remove_key(pygame.K_SPACE)
                    return
                if self.action:
                    self.npc_action()
                    return
                self.advance_dialogue()
                keylogs.remove_key(pygame.K_SPACE)
        else:
            if keylogs.is_pressed(pygame.K_SPACE):
                self.screen_fade()
                if self.can_start:
                    self.start_dialogue()
                    self.get_speakers()
                    self.dialogue_active = True
                keylogs.remove_key(pygame.K_SPACE)

    def load_dialogues(self):
        with open(resource_path("venv/code/json/dialogues.json"), encoding="utf-8") as file:
            data_dialogues = json.load(file)
            with open(resource_path("venv/code/json/save.json"), encoding="utf-8") as file:
                data_save = json.load(file)
                self.last_dialogue_id = data_save["dialogues"][self.name]
                if self.last_dialogue_id.startswith("condition"):
                    self.dialogues = data_dialogues[self.name][self.last_dialogue_id]["response"]
                    self.condition = data_dialogues[self.name][self.last_dialogue_id]["condition"]
                    self.is_condition = True
                else:
                    if not len(data_dialogues[self.name][self.last_dialogue_id][0]["required_flags"]) == 0:
                        for flag in data_dialogues[self.name][self.last_dialogue_id][0]["required_flags"]:
                            if flag not in self.player.quest.flags:
                                self.dialogues = data_dialogues[self.name][self.last_dialogue_id][0]["response"]
                                self.missing_flags = True
                                return
                            
                    self.speakers = data_dialogues[self.name][self.last_dialogue_id][0]
                    self.dialogues = data_dialogues[self.name][self.last_dialogue_id][2:]
    
    def get_speakers(self):        
        self.speakers_image[self.name] = self.get_all_images()["down"][0].subsurface(0, 0, self.frame_width, self.frame_height // 1.25)
        self.speakers_image[self.name] = pygame.transform.scale_by(self.speakers_image[self.name], 4)
        
        self.speakers_image["Player"] = pygame.image.load(resource_path("venv/assets/sprite/ash_atchoum_walk.png")).convert_alpha()
        frame_width = self.speakers_image["Player"].get_size()[0] // 4
        frame_height = self.speakers_image["Player"].get_size()[1] // 4
        self.speakers_image["Player"] = self.speakers_image["Player"].subsurface(0, 0, frame_width, frame_height // 1.25)
        self.speakers_image["Player"] = pygame.transform.scale_by(self.speakers_image["Player"],  2 if frame_width > 37 else 4)
            
    def load_speakers(self, speakers):
        if not speakers:
            return
        
        speaker = {}
        
        for speaker in speakers:
            speaker[speaker] = Entity(f"venv/assets/sprite/{speaker}.png", 4, 4)
            speaker[speaker].rect.left = self.player.rect.right
            
    def screen_fade(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        max_alpha = 160
        step = 10
        delay = 40

        for alpha in range(0, max_alpha + 1, step):
            overlay.fill((0, 0, 0, alpha))
            self.screen.blit(overlay, (0, 0))
            pygame.display.update()
            pygame.event.pump()
            pygame.time.delay(delay)

        self.can_start = True

    def start_dialogue(self):
        self.load_dialogues()
        self.dialogue_index = 0
        self.npc_turn = True
        self.advance_dialogue()

    def advance_dialogue(self):
        if self.dialogue_index >= len(self.dialogues):
            self.next_section()
            self.dialogue_active = False
            self.screen_fade()
            return

        if self.is_condition:
            dialogue = self.dialogues[0]
            self.current_text = dialogue["text"]
            self.current_speaker = dialogue["speaker"]
            self.npc_turn = self.current_speaker != "Player"
            self.check_condition()
            self.typewriter_index = 0
            return
        
        if self.missing_flags:
            dialogue = self.dialogues
            self.current_text = dialogue
            self.dialogue_index += 1
            self.typewriter_index = 0
            return
        
        dialogue = self.dialogues[self.dialogue_index]
        self.current_text = dialogue["text"]
        self.current_speaker = dialogue["speaker"]
        self.npc_turn = self.current_speaker != "Player"
        self.dialogue_index += 1

        self.current_text = self.handle_action_tag(self.current_text)
        self.typewriter_index = 0

    def handle_action_tag(self, text: str) -> str:
        if not text:
            return text

        start = text.find("[")
        end = text.find("]", start + 1)
        if start != -1 and end != -1:
            self.action = text[start + 1:end].strip()
            text = (text[:start] + text[end + 1:]).strip()

        return text

    def draw_current_dialogue(self, screen):
        if self.current_text:
            self.draw_speaker_name(screen)
            self.draw_text(self.current_text[:self.typewriter_index], screen)

    def draw_speaker_name(self, screen):
        if self.current_speaker:
            name_font = pygame.font.Font(None, 25)
            name_surface = name_font.render(self.current_speaker, True, (255, 255, 255))
            name_width, name_height = name_surface.get_size()
            box_width = name_width + 40
            box_height = name_height + 20
            box_x = 200
            box_y = 780 - 150 - box_height
            pygame.draw.rect(screen, (80,80, 80), (box_x, box_y, box_width, box_height), 0, 10)
            pygame.draw.rect(screen, (245, 206, 78), (box_x, box_y, box_width, box_height), 2, 10)
            screen.blit(name_surface, (box_x + 20, box_y + 10))
            screen.blit(self.speakers_image[self.current_speaker], (box_x + box_width + 20, 780 - 150 - self.speakers_image[self.current_speaker].get_size()[1]))
            

    def draw_text(self, text, screen):
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            if word.startswith("["):
                break

            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < 1280 - 510:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "   

        lines.append(current_line)

        line_height = self.font.get_linesize()
        red_letter_start = None

        pygame.draw.rect(screen, (80, 80, 80), (200, 780 - 150, 1280 - 400, 140), 0, 10)
        pygame.draw.rect(screen, (245, 206, 78), (200, 780 - 150, 1280 - 400, 140), 2, 10)
        pygame.draw.rect(screen, (255, 255, 255), (220, 780 - 140, 1280 - 500, 120), 0, 10)

        for i, line in enumerate(lines):
            x_pos = 230
            for j, letter in enumerate(line):
                if letter.strip():
                    if letter == "#" and not red_letter_start:
                        red_letter_start = j + 1
                        continue
                    
                    if letter == "#" and red_letter_start:
                        red_letter_start = None
                        continue

                    if red_letter_start:
                        if j >= red_letter_start:
                            screen.blit(self.font.render(letter, True, (255, 40, 40)), (x_pos, 780 - 130 + i * line_height))
                    else:
                        screen.blit(self.font.render(letter, True, (20, 20, 20)), (x_pos, 780 - 130 + i * line_height))
                x_pos += self.font.size(letter)[0]
                
    def next_section(self):
        next_section_index = None
        next_section_name = self.last_dialogue_id
        with open(resource_path("venv/code/json/dialogues.json")) as file:
            data_dialogues = json.load(file)
            for i, key in enumerate(data_dialogues[self.name].keys()):
                if next_section_index == i:
                    next_section_name = key
                    break
                if key == self.last_dialogue_id:
                    if i < len(data_dialogues[self.name].keys()):
                        next_section_index = i + 1
        self.save_progression(next_section_name)

    def save_progression(self, next_section_name):
        save_file = save_path("save.json")

        if os.path.exists(save_file):
            with open(save_file, "r+", encoding="utf-8") as f:
                save_data = json.load(f)
        else:
            save_data = {}

        save_data["dialogues"][self.name] = next_section_name
        
        with open(save_file, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
        
        Save.save_inventory(self.player)

        self.player.action = f"Talk [{self.name}]"
        self.player.quest.check_quest_done(self.player.action)

    def npc_action(self):
        if self.action:
            action_parts = self.action.split(" ")
            if action_parts[0] == "Give":
                item = action_parts[2]
                quantity = int(action_parts[1])
                self.player_inventory.add_item(item, quantity)
                self.action = ""
            elif action_parts[0] == "Choice":
                choices = action_parts[2].split(",")
                type = action_parts[1]
                self.choice = Choice(self.screen, type, choices, self.player_inventory)
                self.choiced = False
                self.action = ""
            elif action_parts[0] == "Figth":
                pokemon_parts = action_parts[1].split(",")
                pokemon_levels = {i.split(":")[0]: int(i.split(":")[1]) for i in pokemon_parts}
                ennemi_pokemons = [Pokemon(name, level) for name, level in pokemon_levels.items()]
                self.figth = Fight(
                    type="npc",
                    player_pokedex=self.player_inventory["pokedex"],
                    ennemi_pokemons=ennemi_pokemons,
                    screen=self.screen,
                    keys=self.keylogs
                )
                self.action = ""
        return None

    def check_condition(self):
        if self.condition.startswith("HAVE"):
            quantity = int(self.condition.split(" ")[1])
            item = self.condition.split(" ")[2]
            if self.player_inventory[item] >= quantity:
                self.is_condition = False
                self.next_section()