import pygame
from pokemon import Pokemon

class Choice:
    def __init__(self, screen, type, choices, player_inventory):
        self.screen = screen
        self.player_inventory = player_inventory
        self.type = type
        self.choices = choices
        self.choices_images = {}
        self.choices_quantity = {}
        self.choiced = False
        self.selected_choice = None
        self.path = ""
        self.get_path()
        self.get_images()
        self.get_quantity()
    
    def get_path(self):
        if self.type == "pokemon":
            self.path = "venv/assets/pokemons/pokemons_gen1_fronts/"
        elif self.type == "item":
            self.path = "venv/assets/sprite/items/"

    def get_images(self):
        if self.type == "pokemon":
            for choice in self.choices:
                self.choices_images[choice] = pygame.image.load(f"{self.path}{choice}_front.png").convert_alpha()
                self.choices_images[choice] = pygame.transform.scale(self.choices_images[choice], (128, 128))
        elif self.type == "item":
            for choice in self.choices:
                self.choices_images[choice] = pygame.image.load(f"{self.path}{choice}.png").convert_alpha()
                self.choices_images[choice] = pygame.transform.scale(self.choices_images[choice], (128, 128))
    
    def get_quantity(self):
        if self.type == "item":
            for choice in self.choices:
                self.choices_quantity[choice] = choice.split("/")[0]
    
    def draw_choices(self):
        screen_width, screen_height = self.screen.get_size()
        x = 40
        card_width = (screen_width // len(self.choices)) - (x * 2)  if (screen_width // len(self.choices)) > 140 else 140
        card_height = screen_height // 2
        card_x_start = (x * (len(self.choices) - 1))

        font_name = pygame.font.Font(None, 24)
        font_quantity = pygame.font.Font(None, 20)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for i, choice in enumerate(self.choices):
            card_x = card_x_start + i * (card_width + x)
            card_y = screen_height // 2 - card_height // 2
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            is_hovered = card_rect.collidepoint(mouse_pos)
            
            bg_color = (41, 41, 38) if is_hovered else (41, 41, 50)
            border_color = (255, 255, 255)
            border_width = 3 if is_hovered else 2

            pygame.draw.rect(self.screen, bg_color, card_rect, border_radius=15)
            pygame.draw.rect(self.screen, border_color, card_rect, border_width, border_radius=15)

            if choice in self.choices_images:
                img = self.choices_images[choice]
                img_rect = img.get_rect()
                img_rect.center = (card_x + card_width // 2, card_y + card_height // 3)
                self.screen.blit(img, img_rect)

            choice_name = choice.split("/")[-1] if self.type == "item" else choice
            text_surface = font_name.render(choice_name.capitalize(), True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.center = (card_x + card_width // 2, card_y + card_height - 40)
            self.screen.blit(text_surface, text_rect)

            if self.type == "item" and choice in self.choices_quantity:
                quantity = self.choices_quantity[choice]
                quantity_surface = font_quantity.render(f"x{quantity}", True, (200, 200, 200))
                quantity_rect = quantity_surface.get_rect()
                quantity_rect.center = (card_x + card_width // 2, card_y + card_height - 15)
                self.screen.blit(quantity_surface, quantity_rect)
            
            if is_hovered and mouse_clicked:
                self.choiced = True
                self.selected_choice = choice
                self.handle_choice()
                break
    
    def handle_choice(self):
        if self.selected_choice:
            if self.type == "pokemon":
                self.player_inventory["pokedex"].add_pokemon(Pokemon(self.selected_choice, 1))
            elif self.type == "item":
                self.player_inventory.add_item(self.selected_choice)