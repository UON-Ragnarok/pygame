import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos, speed, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface([5,10])
        self.image.fill([255,255,255]) #black bullet, place holder, need to find image or something
        self.rect = self.image.get_rect()
        self.rect.x  = x_pos
        self.rect.y  = y_pos
        self.speed = speed

    def update(self):
        self.rect.y -= self.speed