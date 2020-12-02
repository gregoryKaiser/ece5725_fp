import pygame
from pygame.locals import *
import os
import random

import classes

pygame.init()

W, H = 320, 240
BLACK = 0,0,0
#win = pygame.screen?
win = pygame.display.set_mode((W, H))
pygame.display.set_caption('And My Axe')

circle = pygame.image.load("circle.png")

# background image load
# bg = pygame.image.load(os.path.join('images', 'bg.png')).convert()
# bgX = 0
# bgX2 = bg.get_width()

clock = pygame.time.Clock()

#====Create game objects====
hero = classes.character(circle, 50, 50, 50, 50, 60, 60)
hero.speedx = 3
hero.speedy = 10
env1 = classes.environment(100, 300, "hot", 1)
block = classes.obstacle(circle, 100, 50, 100, 50, 80, 80, "hot")
all_objects = [hero, env1, block]
#TODO: fill all_objects with map
disp_objects = [hero, block]
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

while run: #main game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            run = False
    #loop through obstacles 
    for obj in disp_objects:
        #check for collision
        #collision = classes.collide(hero,obj)
        #move every object based on speed
        obj.x += obj.speedx
        obj.y += obj.speedy
        #gravity
        obj.speedy -= 1
    clock.tick(40)
    win.fill(BLACK)
    redrawWindow()
            




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