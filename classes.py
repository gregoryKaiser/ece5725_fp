import pygame

class character(object):
    #image assets
    #TODO: get image and define image path
    image = pygame.image.load("circle.png")
    
    def __init__(self, image, x, y, glob_x, glob_y, width, height):
        self.x = x
        self.y = y
        self.glob_x = glob_x
        self.glob_y = glob_y
        self.width = width
        self.height = height
        self.speedx = 0 #set high during button press
        self.speedy = 0 #set high when jumping
        self.image = image
        self.health = 100
        self.inventory = {}
        self.attack = 0
        self.defense = 0
        self.signaling = 0
        self.physics_on = 2
        self.hitbox = (self.x, self.y, self.x+self.width, self.height)

    def draw(self, win):
        self.hitbox = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(self.image, (self.x, self.y))
        if self.signaling:
            win.blit(self.image, (self.x, self.y))

    def moveRight(self): #upon button press
        self.speedx = 3

    def moveLeft(self): #upon button press
        self.speedx = -3

    def jump(self): #upon button press
        self.speedy = -20

    def stopMoving(self): #upon button release
        self.speedx = 0

    def stop_signal(self): #upon signal button release
        self.signaling = 0

    def signal(self): #upon button press
        self.signaling = 1


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

    def __init__(self, image, name, x, y, global_x, global_y, width, height, equippable):
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
        self.hitbox = (self.x, self.y, self.x + self.width, self.y + self.height)
        self.physics_on = 1

    def draw(self, win):
        self.hitbox = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(self.image, (self.x, self.y))

class weapon(item):
    def __init__(self, image, name, x, y, global_x, global_y, width, height, equippable, attack):
        super().__init__(image, name, x, y, global_x, global_y, width, height, equippable)
        self.attack = attack

    def draw(self, win, hero):
        if(self.picked_up):
            draw_equipped(win, hero)
        else:
            self.hitbox = (self.x + 10, self.y + 5, self.width - 20, self.height - 5)
            pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
            win.blit(self.image, (self.x, self.y))

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

    def draw(self, win):
        if(self.picked_up):
            pass
        #    draw_equipped(win, hero)
        else:#draw on ground at initial position
            self.hitbox = (self.x , self.y , self.width, self.height)
            pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
            win.blit(self.image, (self.x, self.y))

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

#class for global objects/effects

class environment(object):
    def __init__(self, global_x, effect_length, env_type, attack):
        self.global_x = global_x
        self.effect_length = effect_length
        self.type = env_type
        self.attack = attack
        self.physics_on = 0
    
    def do_harm(self, hero):
        #not sure whether to do location check here or in main??
        if hero.env_type != self.env_type:
            hero.health -= self.attack

class obstacle(object):

    def __init__(self, image, x, y, glob_x, glob_y, width, height, env_type):
        self.x = x
        self.y = y
        self.glob_x = glob_x
        self.glob_y = glob_y
        self.width = width
        self.height = height
        self.speedx = 0 #move with background
        self.speedy = 0 #always zero
        self.type = env_type
        self.image = image
        self.hitbox = (self.x, self.y, self.x + self.width, self.y + self.height)
        self.physics_on = 0

    def draw(self, win):
        #self.hitbox = (self.x, self.y + 25, self.width, self.height)
        self.hitbox = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(self.image, (self.x, self.y))


#helper function for collide
def find_collisions(obj_list):
    collision_list = []
    obj_list_copy = obj_list[:]
    #base case:
    if len(obj_list) < 1:
        return collision_list, no_collision_list

    #select the next object to compare and remove it from the list
    curr_obj = obj_list_copy[0]
    obj_list_copy.remove(curr_obj)

    #identify rect for obj hitbox
    rect1 = pygame.Rect(curr_obj.hitbox)
    collide_flag = False
    for obj in obj_list_copy:
        rect2 = pygame.Rect(obj.hitbox)
        if rect1.colliderect(rect2):
            #collsion detected; collision flag for curr_obj = True
            #append obj to collision list
            collision_list.append(obj)
            obj_list_copy.remove(obj)
            collide_flag = True

    if collide_flag:
        #curr_object collided with something; add it to the collide list
        collision_list.append(curr_obj)
    
    #search the remaining obj_list for collisions:
    return collision_list + find_collisions(obj_list_copy)

        


def collide(obj_list, dir):
    #TODO: finish implementation using reference: http://programarcadegames.com/python_examples/show_file.php?file=platform_jumper.py
    global disp_objects
    collided = find_collisions(obj_list)
    for obj in obj_list:
        if obj in collided:
            #object has collided with something
            #check to see if moving left or right
            if obj.speedx > 0:
                #moving right; undo by bumping back left by the object's speed
                obj.x = obj.x - obj.width


    
    

    

"""
def collide(obj1, obj2):
    #NOTE: obj1 must have a speed
    #NOTE: some edits needed to remove slippery effect
    # collision_tuple = (0,0)
    obj1_left = obj1.hitbox[0]
    obj1_right = obj1.hitbox[0] + obj1.hitbox[2]
    obj1_bottom = obj1.hitbox[1] + obj1.hitbox[3]
    obj1_top = obj1.hitbox[1]

    obj2_left = obj2.hitbox[0]
    obj2_right = obj2.hitbox[0] + obj2.hitbox[2]
    obj2_bottom = obj2.hitbox[1] + obj2.hitbox[3]
    obj2_top = obj2.hitbox[1]

    collided = 0

    #collision code 

    #approach from left
    if (obj1_right > obj2_left and obj1_left < obj2_left):
        #fully enveloped case 
        if obj1_top > obj2_top and obj1_bottom < obj2_bottom:
            #obj1 is within y range of obj2
            # print("x direction collide")
            obj1.speedx = 0
            obj1.x = obj2_left - obj1.width - 1
            collided = 1
        elif obj1_bottom > obj2_top and obj1_top < obj2_top:
            obj1.speedx = 0
            obj1.x = obj2_left - obj1.width - 1
            collided = 1
        elif obj1_top < obj2_bottom and obj1_bottom > obj2_bottom:
            obj1.speedx = 0
            obj1.x = obj2_left - obj1.width - 1
            collided = 1
    #approach from right
    if (obj1_left < obj2_right and obj1_right > obj2_right):
        #fully enveloped case 
        if obj1_top > obj2_top and obj1_bottom < obj2_bottom:
            #obj1 is within y range of obj2
            # print("x direction collide")
            obj1.speedx = 0
            obj1.x = obj2_right + 1
            collided = 1
        elif obj1_bottom > obj2_top and obj1_top < obj2_top:
            obj1.speedx = 0
            obj1.x = obj2_right + 1
            collided = 1
        elif obj1_top < obj2_bottom and obj1_bottom > obj2_bottom:
            obj1.speedx = 0
            obj1.x = obj2_right + 1
            collided = 1

    if obj1_left > obj2_left and obj1_right < obj2_right:
        #obj1 is above or below obj2, bounded in x dir
        if obj1_bottom > obj2_top and obj1_top < obj2_top:
            # print("y1 direction collide")
            collided = 1
            #obj1 is hitting obj2 from above
            if obj1.speedy > 0:
                #prevent obj1 from falling through obj2 but let them jump
                obj1.speedy = 0
                obj1.y = -obj1.height+obj2_top-1
            
        if obj1_top < obj2_bottom and obj1_bottom > obj2_bottom:
            # print("y direction collide")
            #obj1 is below obj2 and hitting it from below
            collided = 1
            if obj1.speedy < 0:
                #prevent obj1 from rising through obj2 but let them fall
                obj1.speedy = 0
                

    return collided

    """
    # #x collision
    # if(obj1.hitbox[0] < obj2.hitbox[0] + obj2.hitbox[2] or obj1.hitbox[0] + obj1.hitbox[2] > obj2.hitbox[0]):
    #     #in the correct x range
    #     if
    
    
    # #y collision
    #     if rect[0] + rect[2] > self.hitbox[0] and rect[0] < self.hitbox[0] + self.hitbox[2]:
    #         if rect[1] < self.hitbox[3]:
    #             return True
    #     return False
    # return collision_tuple
