#####
# It's Dangerous to Go Alone
# Gregory Kaiser (ghk48)
# Caeli MacLennan (cam476)
# December 2020
######
# classes.py contains class definitions for the objects in the game
# collision logic is contained here, as well as the draw() function for 
# each kind of displayable object.

import pygame

class character(object):
    '''character: a character object.
    The character contains a left-facing image, and a right-facing image, for movement in-game. 
    The x and y positions correspond to screen location, while the global x and y coordinates denote starting position.
    The width and height determine the size of the character's hitbox used for collision detection
    '''
    def __init__(self, image_l, image_r, x, y, glob_x, glob_y, width, height):
        self.x = x
        self.y = y
        self.glob_x = glob_x
        self.glob_y = glob_y
        self.width = width
        self.height = height
        self.speedx = 0 #set high/low during button press
        self.speedy = 0 #set high when jumping
        self.image_r = image_r
        self.image_l = image_l
        self.health = 100
        self.inventory = []
        self.attack = 0
        self.defense = 0
        self.signaling = 0
        self.physics_on = 2
        self.direction = 0
        self.env_type = "none"
        self.hitbox = (self.x, self.y, self.width, self.height)

    #the draw function chooses the left or right facing image depending on the movement direction
    def draw(self, win):
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2) #draws the hitbox as a red rectangle
        if(self.direction==1):
            win.blit(self.image_l, (self.x, self.y))
        else:
            win.blit(self.image_r, (self.x, self.y))

    #moves the character by setting x velocity high
    def moveRight(self): #upon button press
        self.direction = 0
        self.speedx = 3

    #moves the character by setting x velocity negative
    def moveLeft(self): #upon button press
        self.direction = 1
        self.speedx = -3

    #jumps the character by setting y velocity negative (low is "up")
    def jump(self): #upon button press
        self.speedy = -20

    #stops the character's movement
    def stopMoving(self): #upon button release
        self.speedx = 0

    #unused, but potentially a method of signaling to a partner that an item is required by the character
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
    '''item: a generic item object.
    Any given item can be given an arbitrary image asset for spawning into frame.
    The position on screen and global (starting) position is given, along with hitbox width and height.
    Any item is not picked up by default, and its equippability determines whether or not it disappears upon collision.
    The environment type is used mostly by the armor subclass to determine preparedness for a certain environment. This field
    can be expanded to apply to critical damage against enemies with other environment types in the future.
    Items have physics=1 by default so that they experience gravity and drag.
    '''
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
        self.env_type = "none"
        self.health = 10
        self.image = image
        self.hitbox = (self.x, self.y, self.x + self.width, self.y + self.height)
        self.physics_on = 1

    #generic items are drawn as usual using the image asset fed during instantiation.
    def draw(self, win, hero):
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2) #optional display of hitbox
        win.blit(self.image, (self.x, self.y))

class weapon(item):
    '''weapon: a weapon item.
    The weapon is a subclass of item, and contains specialty attack field, as well as a left/right image for display on the equipped character
    While the generic draw function is the same as any item, if it is picked up it will display on a character.
    '''
    def __init__(self, image_l, image_r, name, x, y, global_x, global_y, width, height, equippable, attack):
        super().__init__(image_l, name, x, y, global_x, global_y, width, height, equippable)
        self.attack = attack
        self.image_l = image_l
        self.image_r = image_r

    #draws the weapon wherever spawned by default
    def draw(self, win, hero):
        if(self.picked_up):
            self.draw_equipped(win, hero)
        else:
            self.hitbox = (self.x, self.y, self.width, self.height)
            #pygame.draw.rect(win, (255,0,0), self.hitbox, 2)
            win.blit(self.image_r, (self.x, self.y))

    #draw equipped by feeding hero to attach to hero's position
    def draw_equipped(self, win, hero):
        self.y = hero.y+4
        self.hitbox = (self.x, self.y, self.width, self.height)
        if hero.direction==0: #facing right, draw on the right side
            self.x = hero.x+int(self.width/2)
            win.blit(self.image_r, (self.x, self.y))
        else: #facing left, draw on the left side
            self.x = hero.x-int(self.width/2)-2
            win.blit(self.image_l, (self.x, self.y))
        
class armor(item):
    '''armor: an armor item.
    Armor is another subclass of item object which carries a defense value and an environment type. By equipping armor,
    one can withstand the environmental effects of a given level. When equipped, it is attached to the character at a certain
    body location determined by a string argument.
    '''
    def __init__(self, image, name, x, y, global_x, global_y, width, height, equippable, defense, env_type, body_location):
        super().__init__(image, name, x, y, global_x, global_y, width, height, equippable)
        self.defense = defense
        self.env_type = env_type
        self.body_location = body_location

    #drawing a generic piece of armor as any other item
    def draw(self, win, hero):
        if(self.picked_up):
            self.draw_equipped(win, hero)
        else:
            self.hitbox = (self.x , self.y , self.width, self.height)
            #pygame.draw.rect(win, (255,0,0), self.hitbox, 2) #optional hitbox
            win.blit(self.image, (self.x, self.y))

    #if equipped, the armor can be drawn in four candidate locations on the character. 
    def draw_equipped(self, win, hero):
        self.x = hero.x
        self.y = hero.y
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2) #optional hitbox

        if self.body_location == "head": #these values are untuned to body locale
            win.blit(self.image, (hero.x + 5, hero.y + 10))

        elif self.body_location == "feet": #these values are untuned to body locale
            win.blit(self.image, (hero.x + 5, hero.y + 10))

        elif self.body_location == "legs": #these values are untuned to body locale
            win.blit(self.image, (hero.x + 5, hero.y + 10))
            
        elif self.body_location == "torso": #these values have been tuned correctly
            win.blit(self.image, (hero.x+5, hero.y + 30))

class environment(object):
    '''environment: an environment object.
    Environments are given coordinates over which their effects are in-place. A starting coordinate and length 
    determine the extent of the environment so that eventually multiple environments can be used in level design.
    '''
    def __init__(self, global_x, effect_length, env_type, attack):
        self.global_x = global_x
        self.effect_length = effect_length
        self.type = env_type
        self.attack = attack
        self.physics_on = 0
    
    #unused member function that can increase modularity and potentially more complicated environmental effects
    #for example, this do_harm function could be used as a way to slow the character, as opposed to merely decrementing their health.
    def do_harm(self, hero):
        if not hero.env_type == self.type:
            hero.health -= self.attack

class obstacle(object):
    '''obstacle: an obstacle object.
    Obstacles are the generic building-blocks of level design, and are used in floors and platforms on which the hero can climb and jump.
    They have no physics, but have environment types.
    '''
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

    #generic draw functionality draws obstacles at their appropriate positions
    def draw(self, win):
        self.hitbox = (self.x, self.y, self.width, self.height)
        #pygame.draw.rect(win, (255,0,0), self.hitbox, 2) #optional hitbox
        win.blit(self.image, (self.x, self.y))

#helper function for collide
#takes in a list of objects and recursively finds those objects which are colliding
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
            #if the second object is an equipped item, ignore collisions
            if(not(isinstance(obj,item) and obj.equippable and obj.picked_up)):
                rect2 = pygame.Rect(obj.hitbox)
                if rect1.colliderect(rect2):
                    #collsion detected; collision flag for curr_obj = True
                    #append obj to collision list
                    collision_list.append(obj)
                    obj_list_copy.remove(obj)
                    collide_flag = True
                    
                    #check for item collide with hero to "pick it up"
                    if(isinstance(curr_obj, character) and isinstance(obj,item)):
                        obj.picked_up = True #pick it up
                        curr_obj.inventory.append(obj) #add to inventory
                        if(isinstance(obj,armor)): #armor protection
                            curr_obj.env_type = obj.env_type
                        elif(isinstance(obj,weapon)):
                            pass
                        else:
                            curr_obj.health += obj.health #fruit health increase

                    if(isinstance(curr_obj,item) and isinstance(obj,character)):
                        curr_obj.picked_up = True #pick it up
                        obj.inventory.append(curr_obj) #add to inventory
                        if(isinstance(curr_obj,armor)): #armor protection
                            obj.env_type = curr_obj.env_type
                        elif(isinstance(curr_obj,weapon)):
                            pass
                        else:
                            obj.health += curr_obj.health #fruit health increase
        if collide_flag:
            #curr_object collided with something; add it to the collide list
            collision_list.append(curr_obj)
    #search the remaining obj_list for collisions:
    return collision_list + find_collisions(obj_list_copy)

#overall collide function checks for collisions and reverses motion if collision detected
def collide(obj_list, direc):
    collided = find_collisions(obj_list) #find the collisions
    for obj in obj_list:
        if obj in collided:
            #object has collided with something; bump back by dir speed
            if isinstance(obj, item): 
                if not obj.equippable:
                    if obj.picked_up:
                        #if the object that collided was picked up by a hero, delete it from screen
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
            
#moves objects in a direction that they are heading before checking their collisions
def move_objs(obj_list, direc):
    #in x direction, just move using the speed
    if direc == 'x':
        for obj in obj_list:
            obj.x += obj.speedx
            #update hitbox
            obj.hitbox = (obj.x, obj.y, obj.width, obj.height)
    else: #in the y direction, apply physics to change speed as well
        for obj in obj_list:
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
            obj.hitbox = (obj.x, obj.y, obj.width, obj.height) #update hitbox
            
            


    
    

    

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
