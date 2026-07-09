import pygame
from utils import resource_path

class Entity(pygame.sprite.Sprite):
    def __init__(self, spritesheet: str, rows: int, cols: int):
        super().__init__()
        self.dt: float | None = None
        self.spritesheet = pygame.image.load(resource_path(f"venv/assets/{spritesheet}")).convert_alpha()
        if self.spritesheet.get_size()[0] > 150:
         self.spritesheet: pygame.Surface = pygame.transform.scale_by(self.spritesheet, 0.5)
        self.width: int = self.spritesheet.get_size()[0]
        self.height: int = self.spritesheet.get_size()[1]
        self.cols: int = cols
        self.rows: int = rows
        self.frame_width: int | float = self.width // self.cols
        self.frame_height: int | float = self.height // self.rows
        self.image: pygame.Surface = self.spritesheet.subsurface((0, 0, self.frame_width, self.frame_height))
        self.frames: dict[list[pygame.Surface]] = self.get_all_images()
        self.frame_index: int = 0
        self.speed: int = 1
        self.steps: int = 0
        self.moving: bool = False
        self.direction: str = "down"
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.hitbox: pygame.rect.Rect = pygame.rect.Rect(0, 0, 16, 16)
        self.align_hitbox()
        self.collisions: list[pygame.rect.Rect] | None = None

    def update(self):
        self.hitbox.midbottom = self.rect.midbottom
    
    def align_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom
        while self.hitbox.x % 16 != 0:
            self.rect.x -= 1
            self.hitbox.midbottom = self.rect.midbottom
        while self.hitbox.y % 16 != 0:
            self.rect.y -= 1
            self.hitbox.midbottom = self.rect.midbottom

    def move_right(self):
        self.direction = "right"
        self.moving = True
        self.hitbox.x += self.speed
        self.animation("right")

    def move_left(self):
        self.direction = "left"
        self.moving = True
        self.hitbox.x -= self.speed
        self.animation("left")

    def move_up(self):
        self.direction = "up"
        self.moving = True
        self.hitbox.y -= self.speed
        self.animation("up")

    def move_down(self):
        self.direction = "down"
        self.moving = True
        self.hitbox.y += self.speed
        self.animation("down")

    def animation(self, direction: str):
        self.frame_index += 7 * self.dt
        self.image = self.frames[direction][(
            int(self.frame_index) + 1) % len(self.frames[direction])]
    
    def move(self):
        if self.moving:
            if self.steps < 16:
                self.steps += 1
                if self.direction == "down":
                    self.rect.y += 1
                elif self.direction == "left":
                    self.rect.x -= 1
                elif self.direction == "right":
                    self.rect.x += 1
                elif self.direction == "up":
                    self.rect.y -= 1
                self.animation(self.direction)
                self.hitbox.bottomleft = self.rect.bottomleft
            else:
                self.steps = 0
                self.moving = False
                return f"moved,{self.direction}"
    
    def _try_move(self, direction: str):
        self.direction = direction
        dx, dy = 0, 0
        if direction == "up":    dy = -16
        elif direction == "down": dy = 16
        elif direction == "left": dx = -16
        elif direction == "right": dx = 16

        future = self.hitbox.move(dx, dy)
        blocked = False
        if self.collisions:
            for col in self.collisions:
                if future.colliderect(col):
                    blocked = True
                    break

        if not blocked:
            self.moving = True
            self.steps = 0
            self.animation(direction)

    def check_collision(self):
        if not self.collisions:
            return False
        for collision in self.collisions:
            if self.hitbox.colliderect(collision):
                return True
        return False

    def add_collisions(self, collisions: list[pygame.rect.Rect]):
        self.collisions = collisions

    def get_all_images(self):
        frames = {
            "down": [],
            "left": [],
            "right": [],
            "up": []
        }

        for row, direction in enumerate(frames.keys()):
            for col in range(self.cols):
                frames[direction].append(self.spritesheet.subsurface(
                    ((self.width // self.cols) * col, (self.height // self.rows) * row, self.width // self.cols, self.height // self.rows)))
        return frames


class PokemonEntity(Entity):
    def __init__(self, spritesheet: str, rows: int, cols: int):
        super().__init__(spritesheet, rows, cols)
        self.get_rect()

    def get_rect(self):
        bounding: pygame.rect.Rect = self.image.get_bounding_rect()
        self.rect: pygame.rect.Rect = pygame.rect.Rect(0, 0, bounding.width + 14, bounding.height + 14)

    def move_up(self):
        self.hitbox.y -= self.speed
        self.animation("up")

    def move_down(self):
        self.hitbox.y += self.speed
        self.animation("down")

    def move_left(self):
        self.hitbox.x -= self.speed
        self.animation("left")

    def move_right(self):
        self.hitbox.x += self.speed
        self.animation("right")

    def change_position(self, player_side, player_rect):
        if player_side == "top":
            self.rect.bottom = player_rect.top
            self.rect.left = player_rect.left
        elif player_side == "down":
            self.rect.top = player_rect.bottom
            self.rect.left = player_rect.left
        elif player_side == "left":
            self.rect.right = player_rect.left
            self.rect.top = player_rect.top
        elif player_side == "right":
            self.rect.left = player_rect.right
            self.rect.top = player_rect.top

    def add_collisions(self, collisions: list[pygame.rect.Rect]):
        new_collisions = []
        for collision in collisions:
            new_collisions.append(pygame.rect.Rect(collision.x, collision.y, collision.width, collision.height))
        self.collisions = new_collisions