import pygame
from pygame.locals import *
import os
import random
import classes
import RPi.GPIO as GPIO
import time
import subprocess

#TFT stuff
os.putenv('SDL_VIDEODRIVER','fbcon')
os.putenv('SDL_FBDEV','/dev/fb1')#might have to change to fb1
os.putenv('SDL_MOUSEDRV','TSLIB') #Track mouse clicks on piTFT
os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

GPIO.setmode(GPIO.BCM)

#Button setup
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #init but 17, close to power supply
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) #init but 22
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP) #init but 23
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) #init but 27
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) #init but 26
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP) #init but 16

move_l_toggle = 0
move_r_toggle = 0
#Button callback
def quit_game(channel):
    global run
    run = False

def move_hero_left(channel):
    global hero
    global move_l_toggle
    if move_l_toggle == 0:
        move_l_toggle = 1
        hero.moveLeft()
        
    else:
        move_l_toggle = 0
        hero.speedx = 0


def move_hero_right(channel):
    global hero
    global move_r_toggle
    if move_r_toggle == 0:
        move_r_toggle = 1
        hero.moveRight()
    else:
        move_r_toggle = 0
        hero.speedx = 0



pygame.init()
pygame.mouse.set_visible(False)
W, H = 320, 240
BLACK = 0,0,0
#win = pygame.screen?
win = pygame.display.set_mode((W, H))
pygame.display.set_caption('And My Axe')

hero_im = pygame.image.load("staticBoy.png")
hero_im = pygame.transform.scale(hero_im,(50,50))
ground_im = pygame.image.load("Ground.png")
ground_im = pygame.transform.scale(ground_im, (320, 40))
circle_im = pygame.image.load("circle.png")
circle_im = pygame.transform.scale(circle_im, (100,100))

# background image load
# bg = pygame.image.load(os.path.join('images', 'bg.png')).convert()
# bgX = 0
# bgX2 = bg.get_width()

clock = pygame.time.Clock()

#====Create game objects====
hero = classes.character(hero_im, 50, 50, 50, 50, 25, 50)
hero.speedx = 0
hero.speedy = 2

env1 = classes.environment(100, 300, "hot", 1)
block = classes.obstacle(circle_im, 150, 15, 150, 15, 100, 100, "hot")
floor = classes.obstacle(ground_im, 0, 200, 0, 200, 320, 15, "normal")

all_objects = [hero, env1, floor, block]
#TODO: fill all_objects with map
disp_objects = [hero, floor, block]
#====pygame timers and variables
run = True
score = 0
# pygame.time.set_timer(USEREVENT+1, 500)
# pygame.time.set_timer(USEREVENT+2, 3000)

def redrawWindow():
    largeFont = pygame.font.SysFont('comicsans', 30)
    #win.blit(bg, (bgX, 0))
    #win.blit(bg, (bgX2,0))
    text = largeFont.render('Score: ' + str(score), 1, (255,255,255))
    for obstacle in disp_objects:
        obstacle.draw(win)

    win.blit(text, (700, 10))
    pygame.display.update()

#connect buttons to callbacks
GPIO.add_event_detect(17, GPIO.FALLING, callback=quit_game)
GPIO.add_event_detect(23, GPIO.BOTH, callback=move_hero_left, bouncetime=100)
GPIO.add_event_detect(27, GPIO.BOTH, callback=move_hero_right, bouncetime=100)


#TODO: add more buttons

while run: #main game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
        if event.type is MOUSEBUTTONDOWN:
            hero.jump()
    #loop through obstacles 
    for obj in disp_objects:
        #move every object based on speed
        obj.x += obj.speedx
        obj.y += obj.speedy
        #gravity
        if obj.physics_on==1:
            obj.speedy += 2
            #drag
            # if obj.speedy>0:
            #     obj.speedy -= 1
            # elif obj.speedy<0:
            #     obj.speedy += 1
        elif obj.physics_on==2:
            obj.speedy += 2

        #check for collision
        collision = classes.collide(hero,obj)
        # print(collision)
    clock.tick(40)
    win.fill(BLACK)
    redrawWindow()
            
GPIO.cleanup()




#main while:

#if key_right
#    set right speed
#if key_left
#    set left speed
#if key_up
#    set positive y speed

#for all objects
#   collide with character?
#       if obstacle
#           stop the character
#               -sets speeds to zero
#           do environment check
#       else if enemy
#           decrement health
#       else if item
#           pick up item
#           if equippable:
#               update hero params
#           else:
#               update hero inventory

#if character at rightward limit
#   character speed zero
#   update background position (moves left)
#   update global position
#if chracter at leftward limit
#   character speed zero
#   update background 
#   update global posiiotn
#else
#   update character position with speed (pixels/frame)
#   update global position
#y speed = y speed - gravity
