#File to store the item class
"""
png image --> image to represent item
string name --> string name of the object, used for items stored in inventory
int x --> x position on screen
int y --> y position on screen
int global_x --> the global x position for that level (so it can come back on screen)
int global_y --> the global y position for that level (so it can come back on screen)
int width --> the width in pixels that the item takes up when not picked up
int height --> the height in pixels that the item takes up when not picked up
bool equippable --> boolean True or False that determines if the item can alter the player's stats

weapon: any item that does damage
- int attack --> int damage to modify player's attack stat to

armor: any item that provides defense
- int defense --> int defense to modify player's defence stat to
- string env_type --> string environment type to match (i.e. "cold", "hot", "none")
- string body_location --> string that indicates where to draw on character when picked_up == True


"""

class item(object):

    def __init__(self, name, image, x, y, global_x, global_y, width, height, equippable):
        self.name = name
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
        self.image = image

    def draw(self, win):
        self.hitbox = (self.x + 10, self.y + 5, self.width - 20, self.height - 5)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(self.image, (self.x, self.y))

    def collide(self, rect): #copied from spike
        if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
            if rect[1] < self.hitbox[3]:
                self.picked_up = True
                return True
        return False

class weapon(item):
    def __init__(self, image, name, x, y, global_x, global_y, width, height, equippable, attack):
        super().__init__(image, name, x, y, global_x, global_y, width, height, equippable)
        self.attack = attack

    def draw_equipped(self, win, hero):
        self.hitbox = (self.x + 10, self.y + 5, self.width - 20, self.height - 5)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        #TODO: figure out correct location on hero to draw
        win.blit(self.image, (hero.x + 5, hero.y + 10))

class armor(item):
    def __init__(self, image, name, x, y, global_x, global_y, width, height, equippable, defense, env_type, body_location):
        super().__init__(image, name, x, y, global_x, global_y, width, height, equippable)
        self.defense = defense
        self.env_type = env_type
        self.body_location = body_location

    def draw_equipped(self, win, hero):
        self.hitbox = (self.x + 10, self.y + 5, self.width - 20, self.height - 5)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)

        #TODO: figure out correct location on hero to draw
        if self.body_location == "head":
            win.blit(self.image, (hero.x + 5, hero.y + 10))

        elif self.body_location == "feet":
            win.blit(self.image, (hero.x + 5, hero.y + 10))

        elif self.body_location == "legs":
            win.blit(self.image, (hero.x + 5, hero.y + 10))
            
        elif self.body_location == "torso":
            win.blit(self.image, (hero.x + 5, hero.y + 10))

