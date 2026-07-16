import pygame
from pokemon import Pokemon

from utils import resource_path

class Pokedex(dict):
    def __init__(self):
        super().__init__()
        self["pokemons"] = {}
        
        self.state = "choose_pokemon"

        self.max_team = 0
        self.selected_team = []

        self.display_surface = pygame.display.get_surface()

        self.font = pygame.font.Font(resource_path("venv/assets/fonts/Abel-Regular.ttf"), 30)
        self.font_small = pygame.font.Font(resource_path("venv/assets/fonts/Agdasima-Regular.ttf"), 26)
                
        self.tint_surface = pygame.Surface(self.display_surface.get_size())
        self.tint_surface.set_alpha(200)
        
        self.main_rect = pygame.rect.Rect((0, 0, self.display_surface.get_size()[0] * 0.8, self.display_surface.get_size()[1] * 0.8)).move_to(center=(self.display_surface.get_size()[0] // 2, self.display_surface.get_size()[1] // 2))
        self.main_rect_border = pygame.rect.Rect((0, 0, self.display_surface.get_size()[0] * 0.8 + 8, self.display_surface.get_size()[1] * 0.8 + 8)).move_to(center=(self.display_surface.get_size()[0] // 2, self.display_surface.get_size()[1] // 2))
        
        self.max_items = 6
        self.index = 0
        self.list_width = self.main_rect.width * 0.27
        self.item_height = (self.main_rect.height // self.max_items) - 10
        
    def add_pokemon(self, pokemon: Pokemon):
        self["pokemons"][pokemon["name"]] = pokemon
    
    def inputs(self, keys):
        if keys.is_pressed(pygame.K_UP):
            self.index -= 1
            keys.remove_key(pygame.K_UP)
        if keys.is_pressed(pygame.K_DOWN):
            self.index += 1
            keys.remove_key(pygame.K_DOWN)
        
        if self["pokemons"]:
            self.index = self.index % len(self["pokemons"])

    def draw_pokedex(self, keys):
        self.inputs(keys)
        
        self.display_surface.blit(self.tint_surface, (0, 0))
        pygame.draw.rect(self.display_surface, (255, 255, 255), self.main_rect_border, border_bottom_left_radius=10, border_top_left_radius=10)
        pygame.draw.rect(self.display_surface, (157, 200, 232), self.main_rect, border_bottom_left_radius=10, border_top_left_radius=10)

        pygame.draw.line(self.display_surface, "white", [self.display_surface.get_size()[0] * 0.1 + self.list_width + 1, self.display_surface.get_size()[1] * 0.1], [self.display_surface.get_size()[0] * 0.1 + self.list_width + 1, self.display_surface.get_size()[1] * 0.9 - 1], 4)


        for index, pokemon in enumerate(self["pokemons"].items()):
            bg_color = (150, 150, 150) if self.index != index else (37, 120, 170)

            if self.state == "choose_fight":
                if pokemon[0] in self.selected_team:
                    bg_color = (100, 200, 100)

            v_offset = 0 if self.index < self.max_items else -(self.index - self.max_items + 1) * self.item_height - 10
            top = self.main_rect.top + index * self.item_height + v_offset

            if index != self.index:
                item_rect = pygame.rect.Rect(self.main_rect.left + 30, 5+ top + index * 10, self.list_width - 30, self.item_height)
            else:
                item_rect = pygame.rect.Rect(self.main_rect.left + 20, 5+ top + index * 10, self.list_width - 20, self.item_height)
                surface = pygame.Surface(item_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(surface, (40, 40, 40, 150), (4, 4, item_rect.width - 8, (item_rect.height // 2) - 4), border_top_left_radius=6)
                
            icon = pygame.image.load(resource_path(f"venv/assets/pokemons/pokemons_gen1_fronts/{pokemon[0]}_front.png")).convert_alpha()
            icon = pygame.transform.scale(icon, (100, 100))
            icon_rect = icon.get_rect(midleft=item_rect.midleft)

            name_surface = self.font.render(pokemon[0], True, (255, 255, 255))
            name_rect = name_surface.get_rect(midleft=icon_rect.midright)

            if self.main_rect.collidepoint(item_rect.topleft):
                pygame.draw.rect(self.display_surface, bg_color, item_rect, border_bottom_left_radius=10, border_top_left_radius=10)
                if index == self.index:
                    pygame.draw.rect(self.display_surface, (60, 60, 60), item_rect, 4, border_bottom_left_radius=10, border_top_left_radius=10)
                    self.display_surface.blit(surface, item_rect.topleft)
                self.display_surface.blit(name_surface, name_rect)
                self.display_surface.blit(icon, icon_rect)
            
            #selected
            select_button_rect = pygame.rect.Rect(0, 0, 150, 60).move_to(bottomright=self.main_rect.bottomright + pygame.Vector2(-10, -10))
            select_button_text = self.font.render("Choisir" if pokemon[0] not in self.selected_team else "Ranger", True, (255, 255, 255))
            select_button_text_rect = select_button_text.get_rect().move_to(center=select_button_rect.center)

            #heal
            heal_button_rect = pygame.rect.Rect(0, 0, 150, 60).move_to(bottomleft=[self.main_rect.left + self.list_width, self.main_rect.bottom] + pygame.Vector2(10, -10))
            heal_button_text = self.font.render("Soigner", True, (255, 255, 255))
            heal_button_text_rect = heal_button_text.get_rect(center=heal_button_rect.center)

            if self.index == index:
                hp_text = self.font_small.render(f"HP: {str(pokemon[1]["stats"]["stats"]["hp"])}", True, (255, 255, 255))
                hp_text_size = self.font_small.size(f"HP: {str(pokemon[1]["stats"]["stats"]["hp"])}")[1]
                level_text = self.font_small.render(f"Level: {str(pokemon[1]["stats"]["level"])}", True, (255, 255, 255))
                
                icon = pygame.transform.scale(icon, (200, 200))
                icon_rect = icon.get_rect(topleft=self.main_rect.topleft + pygame.Vector2(self.list_width + 10, 10))
                
                pygame.draw.rect(self.display_surface, (220, 100, 100) if pokemon[0] not in self.selected_team else (100, 220, 100), select_button_rect, 0, 10)
                self.display_surface.blit(select_button_text, select_button_text_rect)

                pygame.draw.rect(self.display_surface, (100, 220, 100), heal_button_rect, 0, 10)
                self.display_surface.blit(heal_button_text, heal_button_text_rect)
                
                pygame.draw.rect(self.display_surface, (255, 255, 255), icon_rect, 3)
                self.display_surface.blit(icon, icon_rect)
                
                self.display_surface.blit(level_text, icon_rect.topright + pygame.Vector2(20, 0))
                self.display_surface.blit(hp_text, icon_rect.topright + pygame.Vector2(20, hp_text_size))

                if self.state == "choose_fight":
                    mouse_pos     = pygame.mouse.get_pos()
                    mouse_clicked = pygame.mouse.get_just_pressed()

                    if mouse_clicked[0] and select_button_rect.collidepoint(mouse_pos):
                        if pokemon[0] in self.selected_team:
                            self.selected_team.remove(pokemon[0])
                        elif len(self.selected_team) < self.max_team:
                            self.selected_team.append(pokemon[0])
                            
                    if len(self.selected_team) == self.max_team:
                        return self.selected_team
                
                if self.state == "choose_pokemon":
                    mouse_pos     = pygame.mouse.get_pos()
                    mouse_clicked = pygame.mouse.get_just_pressed()