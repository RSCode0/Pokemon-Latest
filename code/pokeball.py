import pygame

from utils import resource_path

class Pokeball(pygame.sprite.Sprite):
    def __init__(self, start_pos, direction):
        super().__init__()
        self.image = pygame.image.load(resource_path("venv/assets/sprite/items/pokeball.png")).convert_alpha()
        self.image = pygame.transform.scale_by(self.image, 0.1)
        self.rect: pygame.rect.Rect = self.image.get_rect(center=start_pos)
        self.start_pos = pygame.Vector2(start_pos)
        self.pos = pygame.Vector2(start_pos)
        self.is_poked = True
        if direction.length() > 0:
            self.velocity = direction.normalize() * 2
        else:
            self.velocity = pygame.Vector2(0, 0)
    
    def update(self):
        self.pos += self.velocity
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.kill_pokeball()

    def kill_pokeball(self):
        if self.rect.left < self.start_pos[0] - (1280 / 2) or self.rect.right > self.start_pos[0] + (1280 / 2) or self.rect.top < self.start_pos[1] - (780 / 2) or self.rect.bottom > self.start_pos[1] + (780 / 2):
            self.kill()
            self.is_poked = False