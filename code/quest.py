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

        font_path = "venv/assets/fonts/Agdasima-Regular.ttf"
        self.font = pygame.font.Font(font_path, 25)
        self.font.bold = True
        self.font_list = pygame.font.Font(font_path, 20)
        self.font_text = pygame.font.Font(font_path, 20)
        self.font_small = pygame.font.Font(font_path, 16)

        self.true_icon = pygame.image.load(
            "venv/assets/icons/true_icon.png").convert_alpha()
        self.true_icon = pygame.transform.scale(self.true_icon, (28, 28))

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

    def wrap_text(self, text, font, max_width):
        """Découpe un texte en plusieurs lignes pour qu'il tienne dans max_width."""
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def clean_quest_name(self, raw_name):
        """Transforme 'Talk [pnj1]' en 'Talk pnj1' pour l'affichage."""
        return raw_name.replace("[", "").replace("]", "")

    def draw_quests(self):
        tint_surface = pygame.Surface(self.display_surface.size, pygame.SRCALPHA)
        tint_surface.fill((0, 0, 0, 175))
        self.display_surface.blit(tint_surface, (0, 0))

        pygame.draw.rect(self.display_surface, (157, 200, 232), self.main_rect, 0)
        pygame.draw.rect(self.display_surface, (37, 150, 190), self.main_rect, 4)

        surface_alpha = pygame.Surface((self.main_rect.width - 6, self.main_rect.height - 6), pygame.SRCALPHA)
        for i in range((self.main_rect.height - 6) // 2):
            pygame.draw.line(surface_alpha, [100, 160, 120, 150], (0, i * 2), (self.main_rect.width - 6, i * 2))
        self.display_surface.blit(surface_alpha, self.main_rect.topleft + pygame.Vector2(3, 3))

        header_rect = pygame.Rect(self.main_rect.x + 40, self.main_rect.y + 40, self.main_rect.width - 80, 80)
        pygame.draw.rect(self.display_surface, (255, 255, 255), header_rect)
        pygame.draw.rect(self.display_surface, (245, 206, 78), header_rect, 4)

        title = self.font.render("Journal de quête", True, (0, 0, 0))
        self.display_surface.blit(title, title.get_rect(center=header_rect.center))

        body_rect = pygame.Rect(
            self.main_rect.x + 40,
            header_rect.bottom + 20,
            self.main_rect.width - 80,
            self.main_rect.bottom - 40 - (header_rect.bottom + 20)
        )

        list_rect = pygame.Rect(body_rect.x, body_rect.y, int(body_rect.width * 0.35), body_rect.height)
        detail_rect = pygame.Rect(list_rect.right + 16, body_rect.y, body_rect.width - list_rect.width - 16, body_rect.height)

        self.draw_quest_list(list_rect)
        self.draw_quest_detail(detail_rect)

    def draw_quest_list(self, rect):
        pygame.draw.rect(self.display_surface, (255, 255, 255), rect)
        pygame.draw.rect(self.display_surface, (37, 150, 190), rect, 3)

        padding = 8
        item_height = 44
        y = rect.y + padding

        for i, quest in enumerate(self.quests):
            item_rect = pygame.Rect(rect.x + padding, y, rect.width - padding * 2, item_height)
            if item_rect.bottom > rect.bottom - padding:
                break

            if i == self.index:
                bg_color = (168, 216, 184)
                border_color = (60, 140, 90)
            else:
                bg_color = (240, 240, 235)
                border_color = (200, 200, 195)

            pygame.draw.rect(self.display_surface, bg_color, item_rect, border_radius=6)
            pygame.draw.rect(self.display_surface, border_color, item_rect, 2, border_radius=6)

            text_color = (120, 120, 115) if quest["completed"] == "True" else (30, 30, 30)
            label = self.clean_quest_name(quest["quest"])

            if quest["completed"] == "True":
                icon_pos = (item_rect.right - 34, item_rect.centery - 14)
                self.display_surface.blit(self.true_icon, icon_pos)
                max_text_width = item_rect.width - 50
            else:
                max_text_width = item_rect.width - 16

            label_surface = self.font_list.render(label, True, text_color)
            if label_surface.get_width() > max_text_width:
                while label and self.font_list.size(label + "...")[0] > max_text_width:
                    label = label[:-1]
                label += "..."
                label_surface = self.font_list.render(label, True, text_color)

            text_x = item_rect.x + 8
            self.display_surface.blit(label_surface, (text_x, item_rect.centery - label_surface.get_height() // 2))

            y += item_height + 6

    def draw_quest_detail(self, rect):
        pygame.draw.rect(self.display_surface, (255, 255, 255), rect)
        pygame.draw.rect(self.display_surface, (37, 150, 190), rect, 3)

        quest = self.quests[self.index]
        padding = 16
        inner_width = rect.width - padding * 2

        title_surface = self.font.render(self.clean_quest_name(quest["quest"]), True, (30, 30, 30))
        self.display_surface.blit(title_surface, (rect.x + padding, rect.y + padding))

        if quest["completed"] == "True":
            self.display_surface.blit(self.true_icon, (rect.right - padding - 28, rect.y + padding))

        text_y = rect.y + padding + title_surface.get_height() + 14
        for line in self.wrap_text(quest["text"], self.font_text, inner_width):
            line_surface = self.font_text.render(line, True, (70, 70, 70))
            self.display_surface.blit(line_surface, (rect.x + padding, text_y))
            text_y += line_surface.get_height() + 4

        text_y += 10
        progress_text = self.handle_flags(quest["flags"])
        progress_rect = pygame.Rect(rect.x + padding, text_y, inner_width, 32)
        pygame.draw.rect(self.display_surface, (245, 224, 168), progress_rect, border_radius=6)
        pygame.draw.rect(self.display_surface, (44, 44, 44), progress_rect, 2, border_radius=6)
        progress_surface = self.font_small.render(progress_text, True, (90, 70, 20))
        self.display_surface.blit(
            progress_surface,
            (progress_rect.x + 10, progress_rect.centery - progress_surface.get_height() // 2)
        )

        text_y = progress_rect.bottom + 10
        reward_text = self.handle_reward(quest["reward"])
        reward_rect = pygame.Rect(rect.x + padding, text_y, inner_width, 32)
        pygame.draw.rect(self.display_surface, (232, 200, 216), reward_rect, border_radius=6)
        pygame.draw.rect(self.display_surface, (44, 44, 44), reward_rect, 2, border_radius=6)
        reward_surface = self.font_small.render(f"Récompense : {reward_text}", True, (90, 30, 55))
        self.display_surface.blit(
            reward_surface,
            (reward_rect.x + 10, reward_rect.centery - reward_surface.get_height() // 2)
        )

    def handle_flags(self, flags):
        if not flags:
            return "Aucune condition requise"
        done = sum(1 for f in flags if f in self.flags)
        return f"Progression : {done}/{len(flags)}"

    def handle_reward(self, reward):
        if not reward:
            return "Aucune"
        if isinstance(reward, list):
            return ", ".join(str(r) for r in reward)
        return str(reward)

    def load_quest(self):
        with open("venv/code/json/save.json", "r+") as file:
            save_data = json.load(file)
            self.last_quest_id = save_data["quest"]["id"]

            self.flags = save_data["flags"]

            with open("venv/code/json/quest.json", "r+") as f:
                quest_data = json.load(f)

                self.quests = [
                    {
                        "index": index,
                        "quest": quest_data[self.last_quest_id][index]["quest"],
                        "flags": quest_data[self.last_quest_id][index]["required_flags"],
                        "completed_flag": quest_data[self.last_quest_id][index]["completed_flag"],
                        "completed": quest_data[self.last_quest_id][index]["completed"],
                        "reward": quest_data[self.last_quest_id][index]["reward"],
                        "text": quest_data[self.last_quest_id][index]["quest_text"],
                    }
                    for index, quest in enumerate(quest_data[self.last_quest_id])
                ]