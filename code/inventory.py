import pygame
from pokedex import Pokedex

class Inventory(dict):
    def __init__(self):
        super().__init__()
        self["pokeball"] = 0
        self["medicine"] = 0
        self["pokedex"] = Pokedex()

    def add_item(self, item: str, quantity: int):
        if item == "Pokéball":
            self["pokeball"] += quantity
        elif item == "Medicine":
            self["medicine"] += quantity

# class InventoryBar:
#     def __init__(self, screen, inventory):
#         self.screen = screen
#         self.inventory = inventory
#         self.items_images = {}
#         self.font = pygame.font.Font(None, 20)
#         self.selected_item_rect = pygame.rect.Rect(325, 780 - 70 - 20, 70, 70)
#         self.selected_item = ""

#     def draw_inventory(self):
#         screen_width, screen_height = self.screen.get_size()
#         bar_height = 70
#         bar_rect = pygame.Rect(320, screen_height - bar_height - 25, screen_width - 640, 80)
#         pygame.draw.rect(self.screen, (255, 255, 255), bar_rect)
#         bar_rect = pygame.Rect(325, screen_height - bar_height - 20, screen_width - 650, bar_height)
#         pygame.draw.rect(self.screen, (58, 158, 181), bar_rect)
#         slot_width = 70
#         slot_height = 70

#         for i in range(9):
#             pygame.draw.rect(self.screen, (255, 255, 255), (325 + i * slot_width, screen_height - bar_height - 20, slot_width, slot_height), 4)
#             for i, item in enumerate(self.inventory.keys()):
#                 self.items_images[item] = {
#                     "image": pygame.image.load("venv/assets/sprite/items/pokeball.png").convert_alpha(),
#                     "rect": pygame.rect.Rect(0, 0, 0, 0)
#                 }
#                 self.items_images[item]["image"] = pygame.transform.scale_by(self.items_images[item]["image"], 0.3)
#                 self.items_images[item]["rect"] = self.items_images[item]["image"].get_rect()
#                 self.items_images[item]["rect"].center = [325 + 70 * i + 35.5, screen_height - bar_height - 20 + 35.5]
#                 quantity = self.inventory[item]
#                 if isinstance(quantity, int):
#                     quantity_text = self.font.render(str(quantity), True, (255, 255, 255))
#                     text_rect = quantity_text.get_rect()
#                     text_rect.center = self.items_images[item]["rect"].bottomleft
#                     self.screen.blit(quantity_text, text_rect)
#                 self.screen.blit(self.items_images[item]["image"], self.items_images[item]["rect"])
#         self.update()
    
#     def update(self):
#         if self.selected_item_rect:
#             pygame.draw.rect(self.screen, (240, 100, 100), self.selected_item_rect, 5)
#             for item in self.items_images:
#                 if self.items_images[item]["rect"].colliderect(self.selected_item_rect):
#                     self.selected_item = item

#     def select_item(self, key):
#         if key == pygame.K_1:
#             self.selected_item_rect = pygame.rect.Rect(325, 780 - 70 - 20, 70, 70)
#         elif key == pygame.K_2:
#             self.selected_item_rect = pygame.rect.Rect(325 + 70, 780 - 70 - 20, 70, 70)
#         elif key == pygame.K_3:
#             self.selected_item_rect = pygame.rect.Rect(325 + 70 * 2, 780 - 70 - 20, 70, 70)