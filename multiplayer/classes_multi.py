#####
# It's Dangerous to Go Alone
# Gregory Kaiser (ghk48)
# Caeli MacLennan (cam476)
# December 2020
######
# classes_multi.py is an adapted old version of classes.py
# which is modified to take image path strings, instead of pygame surface
# to its displayable objects. THis is done so that pickle can package
# and send the data without error.

import pygame

class character(object):
    #image assets
    
    def __init__(self, imagepath, x, y, glob_x, glob_y, width, height):
        self.x = x
        self.y = y
        self.glob_x = glob_x
        self.glob_y = glob_y
        self.width = width
        self.height = height
        self.speedx = 0 #set high/low during button press
        self.speedy = 0 #set high when jumping
        self.imagepath = imagepath
        self.health = 100
        self.inventory = []
        self.attack = 0
        self.defense = 0
        self.signaling = 0
        self.physics_on = 2
        self.env_type = "none"
        self.hitbox = (self.x, self.y, self.width, self.height)

    def draw(self, win):
        image_disp = pygame.image.load(self.imagepath)
        image_disp = pygame.transform.scale(image_disp,(self.width,self.height))
        self.hitbox = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(image_disp, (self.x, self.y))
        if self.signaling:
            win.blit(image_disp, (self.x, self.y))

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

class item(object):

    def __init__(self, imagepath, name, x, y, global_x, global_y, width, height, equippable):
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
        self.env_type = "none"
        self.health = 10
        self.imagepath = imagepath
        self.hitbox = (self.x, self.y, self.x + self.width, self.y + self.height)
        self.physics_on = 1

    def draw(self, win, hero):
        image_disp = pygame.image.load(self.imagepath)
        image_disp = pygame.transform.scale(image_disp,(self.width,self.height))
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(image_disp, (self.x, self.y))

class weapon(item):
    def __init__(self, image, name, x, y, global_x, global_y, width, height, equippable, attack):
        super().__init__(image, name, x, y, global_x, global_y, width, height, equippable)
        self.attack = attack

    def draw(self, win, hero):
        if(self.picked_up):
            self.draw_equipped(win, hero)
        else:
            image_disp = pygame.image.load(self.imagepath)
            image_disp = pygame.transform.scale(image_disp,(self.width,self.height))
            self.hitbox = (self.x, self.y, self.width, self.height)
            #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
            win.blit(image_disp, (self.x, self.y))

    def draw_equipped(self, win, hero):
        self.x = hero.x+int(self.width/2)
        self.y = hero.y+4
        self.hitbox = (self.x, self.y, self.width, self.height)
        image_disp = pygame.image.load(self.imagepath)
        image_disp = pygame.transform.scale(hero_im,(self.width,self.height))
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        #TODO: figure out correct location on hero to draw
        win.blit(image_disp, (self.x, self.y))

class armor(item):
    def __init__(self, image, name, x, y, global_x, global_y, width, height, equippable, defense, env_type, body_location):
        super().__init__(image, name, x, y, global_x, global_y, width, height, equippable)
        self.defense = defense
        self.env_type = env_type
        self.body_location = body_location

    def draw(self, win, hero):
        if(self.picked_up):
            self.draw_equipped(win, hero)
        else:#draw on ground at initial position
            image_disp = pygame.image.load(self.imagepath)
            image_disp = pygame.transform.scale(image_disp,(self.width,self.height))
            self.hitbox = (self.x , self.y , self.width, self.height)
            #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
            win.blit(image_disp, (self.x, self.y))

    def draw_equipped(self, win, hero):
        self.x = hero.x
        self.y = hero.y+self.height
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        image_disp = pygame.image.load(self.imagepath)
        image_disp = pygame.transform.scale(image_disp,(self.width,self.height))
        #TODO: figure out correct location on hero to draw
        if self.body_location == "head":
            win.blit(image_disp, (hero.x + 5, hero.y + 10))

        elif self.body_location == "feet":
            win.blit(image_disp, (hero.x + 5, hero.y + 10))

        elif self.body_location == "legs":
            win.blit(image_disp, (hero.x + 5, hero.y + 10))
            
        elif self.body_location == "torso":
            win.blit(image_disp, (hero.x+5, hero.y + 28))

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

    def __init__(self, imagepath, x, y, glob_x, glob_y, width, height, env_type):
        self.x = x
        self.y = y
        self.glob_x = glob_x
        self.glob_y = glob_y
        self.width = width
        self.height = height
        self.speedx = 0 #move with background
        self.speedy = 0 #always zero
        self.type = env_type
        self.imagepath = imagepath
        self.hitbox = (self.x, self.y, self.width, self.height)
        self.physics_on = 0

    def draw(self, win):
        image_disp = pygame.image.load(self.imagepath)
        image_disp = pygame.transform.scale(image_disp,(self.width,self.height))
        #self.hitbox = (self.x, self.y + 25, self.width, self.height)
        self.hitbox = (self.x, self.y, self.width, self.height)
        pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
        win.blit(image_disp, (self.x, self.y))


#helper function for collide
def find_collisions(obj_list):
    collision_list = []
    
    obj_list_copy = obj_list[:]
    #base case:
    if len(obj_list) < 1:
        return collision_list

    #select the next object to compare and remove it from the list
    curr_obj = obj_list_copy[0]
    obj_list_copy.remove(curr_obj)
    
    #if the object is an equipped item, ignore collisions
    if(not(isinstance(curr_obj,item) and curr_obj.equippable and curr_obj.picked_up)):
        #identify rect for obj hitbox
        rect1 = pygame.Rect(curr_obj.hitbox)
        collide_flag = False
        for obj in obj_list_copy:
            #if the object is an equipped item, ignore collisions
            if(not(isinstance(obj,item) and obj.equippable and obj.picked_up)):
                rect2 = pygame.Rect(obj.hitbox)
                if rect1.colliderect(rect2):
                    #collsion detected; collision flag for curr_obj = True
                    #append obj to collision list
                    collision_list.append(obj)
                    obj_list_copy.remove(obj)
                    collide_flag = True
                    
                    #check for item collide with hero
                    if(isinstance(curr_obj, character) and isinstance(obj,item)):
                        obj.picked_up = True
                        curr_obj.inventory.append(obj)
                        if(isinstance(obj,armor)):
                            curr_obj.env_type = obj.env_type
                        elif(isinstance(obj,weapon)):
                            pass
                        else:
                            curr_obj.health += obj.health
                    if(isinstance(curr_obj,item) and isinstance(obj,character)):
                        curr_obj.picked_up = True
                        obj.inventory.append(curr_obj)
                        if(isinstance(curr_obj,armor)):
                            obj.env_type = curr_obj.env_type
                        elif(isinstance(curr_obj,weapon)):
                            pass
                        else:
                            obj.health += curr_obj.health
        if collide_flag:
            #curr_object collided with something; add it to the collide list
            collision_list.append(curr_obj)
    #search the remaining obj_list for collisions:
    return collision_list + find_collisions(obj_list_copy)

def collide(obj_list, direc):
    collided = find_collisions(obj_list)
    for obj in obj_list:
        if obj in collided:
            #object has collided with something; bump back by dir speed
            if isinstance(obj, item):
                if not obj.equippable:
                    if obj.picked_up:
                        obj_list.remove(obj)

            if direc == 'x':
                if obj.speedx < 0:
                    #bump forward by width
                    obj.x += obj.width
                elif obj.speedx > 0:
                    #bump backward by width
                    obj.x -= obj.width
            else:
                obj.y -= obj.speedy
                obj.speedy = 0
                if obj.speedy > 0:
                    #falling onto platform, set vertical speed to zero
                    obj.speedy = 0
            #update hitbox
            obj.hitbox = (obj.x, obj.y, obj.width, obj.height)
            

def move_objs(obj_list, direc):
    if direc == 'x':
        for obj in obj_list:
            #if(isinstance(obj,item) and not obj.picked_up):
            obj.x += obj.speedx
            #update hitbox
            obj.hitbox = (obj.x, obj.y, obj.width, obj.height)
    else:
        for obj in obj_list:
            #if(isinstance(obj,item) and not obj.picked_up):
            obj.y += obj.speedy
            #gravity
            if obj.physics_on==1 or obj.physics_on==2:
                if(obj.speedy<20):
                    obj.speedy += 2
            #drag
            if obj.speedy > 0:
                obj.speedy -= 1
            elif obj.speedy < 0:
                obj.speedy += 1
            if obj.speedx > 0 and obj.physics_on == 1:
                obj.speedx -= 1
            elif obj.speedx < 0 and obj.physics_on == 1:
                obj.speedx += 1
            obj.hitbox = (obj.x, obj.y, obj.width, obj.height)
            #update hitbox
