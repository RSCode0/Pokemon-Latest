import json
import pygame


class Quest:
    def __init__(self):
        self.quest = ""
        self.quests = []
        self.location = []
        
        self.load_quest()

        self.display_surface = pygame.display.get_surface()
        self.SW = self.display_surface.get_size()[0]
        self.SH = self.display_surface.get_size()[1]

        self.font = pygame.font.Font("venv/assets/fonts/Agdasima-Regular.ttf", 25)
        self.font.bold = True

        self.main_rect = pygame.rect.Rect((0, 0, self.SW * 0.8, self.SH * 0.8)).move_to(center=[self.SW // 2, self.SH // 2])

    def check_quest_done(self, action):
        for quest in self.quests:
            if action == quest["quest"] and (quest["flags"] in self.flags or not quest["flags"]) and quest["completed"] != "True":
                with open("venv/code/json/save.json", "r+", encoding="utf-8") as file:
                    data_save = json.load(file)

                data_save["flags"].append(quest["completed_flag"])

                with open("venv/code/json/save.json", "w+", encoding="utf-8") as f:
                    json.dump(data_save, f, ensure_ascii=False, indent=4)

                with open("venv/code/json/quest.json", "r+", encoding="utf-8") as q_file:
                    data_quest = json.load(q_file)
                
                data_quest[quest["quest_index"]]["completed"] = "True"

                with open("venv/code/json/quest.json", "w+", encoding="utf-8") as q:
                    json.dump(data_quest, q, ensure_ascii=False, indent=4)

    def draw_quests(self):
        quest_title_backround = pygame.rect.Rect((0, 0, 100, 60)).move_to(topleft=self.main_rect.topleft + pygame.Vector2(10, 10))
        quest_title = self.font.render("Quêtes", True, (0,0,0))
        quest_title_rect = quest_title.get_rect(center=quest_title_backround.center)

        pygame.draw.rect(self.display_surface, (157, 200, 232), self.main_rect, 0, 10)
        pygame.draw.rect(self.display_surface, (37, 150, 190), self.main_rect, 4, 10)
        
        pygame.draw.rect(self.display_surface, (255, 255, 255), quest_title_backround, 0, 10)
        pygame.draw.rect(self.display_surface, (37, 150, 190), quest_title_backround, 5, 10)
        self.display_surface.blit(quest_title, quest_title_rect)
        
        y_offset = quest_title_backround.bottom + 10
        
        for index, quest in enumerate(self.quests):
            quest_completed = quest["completed"]
            quest = self.handle_tag(quest["quest"])
            quest_backround = pygame.rect.Rect(0, 0, self.main_rect.width * 0.8, (self.main_rect.height - quest_title_backround.height - 20 - 5 * 10) / 5).move_to(left=self.main_rect.left + 10, top=y_offset + index * (self.main_rect.height - quest_title_backround.height - 20) / 5)
            quest_txt = self.font.render(quest, True, (0, 0, 0))
            quest_txt_rect = quest_txt.get_rect(midleft=quest_backround.midleft + pygame.Vector2(20, 0))
            
            pygame.draw.rect(self.display_surface, (255, 255, 255) if quest_completed != "True" else (100, 150, 120), quest_backround, border_radius=5)
            pygame.draw.rect(self.display_surface, (196, 202, 204), quest_backround, 4, 5)
            self.display_surface.blit(quest_txt, quest_txt_rect)
            
    def handle_tag(self, txt):
        action, value = txt.split(" ")
        value = value[1:-1]

        if action == "Talk":
            return f"Talk to {value}"
        elif action == "Figth":
            return f"Figth {value}"
        elif action == "Enter":
            return f"Enter the {value}"

    def load_quest(self):
        with open("venv/code/json/save.json", "r+") as file:
            save_data = json.load(file)
            last_quest_id = save_data["quest"]["id"]

            self.flags = save_data["flags"]

            with open("venv/code/json/quest.json", "r+") as f:
                quest_data = json.load(f)

                for index, quest_id in enumerate(quest_data.keys()):
                    if last_quest_id == quest_id:
                        self.quest = quest_data[quest_id]["quest"]
                        quest_index = index
                
                self.quests = [{"quest_index": quest,"quest":quest_data[quest]["quest"], "flags":quest_data[quest]["required_flags"], "completed_flag":quest_data[quest]["completed_flag"], "completed": quest_data[quest]["completed"]} for index, quest in enumerate(quest_data.keys()) if index >= quest_index - 5 and index <= quest_index + 5 or index == index and quest["completed_flag"] not in self.flags]