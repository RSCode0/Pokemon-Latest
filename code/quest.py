import json
import pygame


class Quest:
    def __init__(self, keylogs):
        self.keylogs = keylogs
        self.last_quest_id = ""
        self.quests = []
        self.location = []
        
        self.load_quest()

        self.display_surface = pygame.display.get_surface()
        self.SW = self.display_surface.get_size()[0]
        self.SH = self.display_surface.get_size()[1]

        self.index = 0

        self.font = pygame.font.Font(
            "venv/assets/fonts/Agdasima-Regular.ttf", 25)
        self.font.bold = True
        self.true_icon = pygame.image.load("venv/assets/icons/true_icon.png").convert_alpha()
        self.true_icon = pygame.transform.scale(self.true_icon, (32, 32))

        self.main_rect = pygame.rect.Rect(
            (0, 0, self.SW * 0.8, self.SH * 0.8)).move_to(center=[self.SW // 2, self.SH // 2])
    
    def input(self):
        if self.keylogs.is_pressed(pygame.K_UP):
            self.index -= 1
            self.keylogs.remove_key(pygame.K_UP)
        elif self.keylogs.is_pressed(pygame.K_DOWN):
            self.index += 1
            self.keylogs.remove_key(pygame.K_DOWN)

        self.index = self.index % len(self.quests)
    
    def update(self):
        self.input()
        self.draw_quests()

    def check_quest_done(self, action):
        for quest in self.quests:
            if action == quest["quest"] and quest["completed"] != "True":
                success_flags = 0
                for flag in quest["flags"]:
                    if flag in self.flags:
                        success_flags += 1
                if success_flags == (len(quest["flags"])):
                    if quest["completed_flag"]:
                        with open("venv/code/json/save.json", "r+", encoding="utf-8") as file:
                            data_save = json.load(file)

                        data_save["flags"].append(quest["completed_flag"])

                        with open("venv/code/json/save.json", "w+", encoding="utf-8") as f:
                            json.dump(data_save, f, ensure_ascii=False, indent=4)

                    with open("venv/code/json/quest.json", "r+", encoding="utf-8") as q_file:
                        data_quest = json.load(q_file)

                    data_quest[self.last_quest_id][quest["index"]]["completed"] = "True"

                    with open("venv/code/json/quest.json", "w+", encoding="utf-8") as q:
                        json.dump(data_quest, q, ensure_ascii=False, indent=4)

    def draw_quests(self):
        tint_surface = pygame.Surface(self.display_surface.size, pygame.SRCALPHA)
        tint_surface.fill((0, 0, 0, 175))
        self.display_surface.blit(tint_surface, (0, 0))

        quest_title_backround = pygame.rect.Rect((0, 0, 100, 60)).move_to(
            bottomleft=self.main_rect.topleft + pygame.Vector2(0, 4))
        quest_title = self.font.render("Quêtes", True, (255, 255, 255))
        quest_title_rect = quest_title.get_rect(
            center=quest_title_backround.center)

        pygame.draw.rect(self.display_surface,
                         (157, 200, 232), self.main_rect, 0, 10)
        pygame.draw.rect(self.display_surface, (37, 150, 190),
                         self.main_rect, 4, 10, border_top_left_radius=0)

        surface_alpha = pygame.Surface(
            (self.main_rect.width - 3, self.main_rect.height - 3), pygame.SRCALPHA)
        for i in range((self.main_rect.height - 3) // 2):
            pygame.draw.line(surface_alpha, [
                             100, 160, 120, 150], (0, i * 2), (self.main_rect.width - 3, i * 2))
        self.display_surface.blit(
            surface_alpha, self.main_rect.topleft + pygame.Vector2(3, 3))

        
        
        pygame.draw.rect(self.display_surface, (157, 200, 232),
                         quest_title_backround, 0, 10, border_bottom_left_radius=0, border_bottom_right_radius=0)
        pygame.draw.rect(self.display_surface, (37, 150, 190),
                         quest_title_backround, 4, 10, border_bottom_left_radius=0, border_bottom_right_radius=0)
        
        surface_title_alpha = pygame.Surface(
            quest_title_backround.size, pygame.SRCALPHA)
        pygame.draw.rect(surface_title_alpha, (100, 150, 150, 90), (0, 0, surface_title_alpha.width,
                         surface_title_alpha.height // 2), border_top_left_radius=10, border_top_right_radius=10)
        self.display_surface.blit(
            surface_title_alpha, quest_title_backround.topleft)
        
        self.display_surface.blit(quest_title, quest_title_rect)

        
        y_offset = self.main_rect.top + 40 - (0 if self.index < 5 else 10 - (self.index - 6) * (self.main_rect.height - 80 - 4 * 10) / 5)

        for index, quest in enumerate(self.quests):
            quest_completed = quest["completed"]
            quest = self.handle_tag(quest["quest"])
            quest_backround = pygame.rect.Rect(0, 0, self.main_rect.width * 0.8, (self.main_rect.height - 80 - 4 * 10) / 5).move_to(left=self.main_rect.left + 40, top=y_offset + index * (self.main_rect.height - 80 + 10) / 5 )
            quest_txt = self.font.render(quest, True, (255, 255, 255) if quest_completed == "True" else (0, 0, 0))
            quest_txt_rect = quest_txt.get_rect(midleft=quest_backround.midleft + pygame.Vector2(20, 0))

            if self.main_rect.collidepoint(quest_backround.bottomleft)  and self.main_rect.collidepoint(quest_backround.topleft):
                pygame.draw.rect(self.display_surface, (255, 255, 255) if quest_completed != "True" else (100, 150, 120), quest_backround, border_radius=5)
                pygame.draw.rect(self.display_surface, (196, 202, 204), quest_backround, 4, 5)

                if self.index == index:
                    pygame.draw.rect(self.display_surface, (0, 0, 0), quest_backround, 4, 5)

                if quest_completed == "True":
                    icon_rect = self.true_icon.get_rect(midleft=quest_backround.midright + pygame.Vector2(20, 0))
                    self.display_surface.blit(self.true_icon, icon_rect)
                self.display_surface.blit(quest_txt, quest_txt_rect)

    def handle_tag(self, txt):
        action, value = txt.split(" ")
        value = value[1:-1]

        if action == "Talk":
            return f"Parlez à {value}"
        elif action == "Figth":
            return f"Combattez {value}"
        elif action == "Enter":
            return f"Entrez dans {value}"

    def load_quest(self):
        with open("venv/code/json/save.json", "r+") as file:
            save_data = json.load(file)
            self.last_quest_id = save_data["quest"]["id"]

            self.flags = save_data["flags"]

            with open("venv/code/json/quest.json", "r+") as f:
                quest_data = json.load(f)

                self.quests = [{"index": index,"quest": quest_data[self.last_quest_id][index]["quest"], "flags": quest_data[self.last_quest_id][index]["required_flags"], "completed_flag": quest_data[self.last_quest_id][index]["completed_flag"], "completed": quest_data[self.last_quest_id]
                                [index]["completed"]} for index, quest in enumerate(quest_data[self.last_quest_id])]    