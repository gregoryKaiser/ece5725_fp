#File to sore the item class
import pygame
"""
x --> x position on screen
y --> y position on screen


"""

class item():

    def __init__(self, x, y, global_x, global_y, width, height, equippable):
        self.x = x
        self.y = y
        self.global_x = global_x
        self.global_y = global_y
        self.speedx = 0 #move with background
        self.speedy = 0 #always zero
        self.width = width
        self.height = height
        self.equippable = equippable
        self.picked_up = False

    def draw(self, win):
        self.hitbox = (self.x + 10, self.y + 5, self.width - 20, self.height - 5)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(image, (self.x, self.y))

    def collide(self, rect): #copied from spike
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] < self.hitbox[3]:
                self.picked_up = True
                return True
        return False

class weapon(item):
    def __init__(self, x, y, global_x, global_y, width, height, equippable, attack):
        super().__init__(x, y, global_x, global_y, width, height, equippable)
        self.attack = attack
