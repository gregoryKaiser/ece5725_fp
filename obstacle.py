class obstacle():

    def __init__(self, x, y, glob_x, glob_y, width, height, env_type):
        self.x = x
        self.y = y
        self.glob_x = glob_x
        self.glob_y = glob_y
        self.width = width
        self.height = height
        self.speedx = 0 #move with background
        self.speedy = 0 #always zero
        self.type = env_type

    def draw(self, win):
        self.hitbox = (self.x + 10, self.y + 5, self.width - 20, self.height - 5)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(image, (self.x, self.y))

    def collide(self, rect): #copied from spike
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] < self.hitbox[3]:
                return True
        return False