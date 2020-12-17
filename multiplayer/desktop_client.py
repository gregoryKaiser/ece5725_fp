import socket, pickle
import classes_multi

class Client:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = None

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))


hostname = 'localhost'#'192.168.56.1'
port = 50007

#stuff for actually playing the game/showing what is on the screen
import os
import random
#import RPi.GPIO as GPIO
import time
import subprocess

import argparse
#import cv2
import numpy as np
import sys
from threading import Thread
import importlib.util
import pygame
from pygame.locals import *

#pygame initialization
pygame.init()
W, H = 320, 240
BLACK = 0,0,0
win = pygame.display.set_mode((W, H))
pygame.mouse.set_visible(False)

pygame.display.set_caption('It\'s Dangerous To Go Alone...')
#==============gameplay main==================================



# #image assets-------------------------------
# hero_im = pygame.image.load("../staticBoy.png")
# hero_im = pygame.transform.scale(hero_im,(50,50))
# ground_im = pygame.image.load("../Ground.png")
# ground_im = pygame.transform.scale(ground_im, (320, 40))
# circle_im = pygame.image.load("../circle.png")
# circle_im2 = pygame.transform.scale(circle_im, (30,30))
# circle_im = pygame.transform.scale(circle_im, (100,100))
# brick = pygame.image.load("../brick.png")
# brick = pygame.transform.scale(brick, (40,40))
# knife_im = pygame.image.load("../knife.png")
# knife_im = pygame.transform.scale(knife_im,(30,30))
# apple_im = pygame.image.load("../apple.png")
# apple_im = pygame.transform.scale(apple_im,(30,30))
# armor_im = pygame.image.load("../armor.png")
# armor_im = pygame.transform.scale(armor_im,(15,15))
#images for the side buttons
stop_im = pygame.image.load("../stop.png")
stop_im = pygame.transform.scale(stop_im,(30,30))
left_im = pygame.image.load("../left_arrow.png")
left_im = pygame.transform.scale(left_im,(30,30))
right_im = pygame.image.load("../right_arrow.png")
right_im = pygame.transform.scale(right_im,(30,30))
prayer_im = pygame.image.load("../prayer.png")
prayer_im = pygame.transform.scale(prayer_im,(30,30))
#background
bg_im = pygame.image.load("../background.png")
#image assets above-------------------------------

clock = pygame.time.Clock()

#====Create game objects====
global hero
hero = classes_multi.character("../rightBoy.png", 90, 50, 90, 50, 25, 50)
hero.speedx = 0
hero.speedy = 2

env1 = classes_multi.environment(100, 300, "cold", 1) #wintertime environment
block = classes_multi.obstacle("../brick.png", 150, 160, 150, 160, 40, 40, "hot")
block2 = classes_multi.obstacle("../brick.png", 30, 100, 30, 100, 40, 40, "hot")
floor = classes_multi.obstacle("../Ground.png", 60, 200, 60, 200, 320, 30, "normal")
#floor2 = classes_multi.obstacle(ground_im, -300, 200, -300, 200, 320, 15, "normal")

all_objects = [hero, env1, floor, block]
disp_objects = [hero, floor, block, block2]
#====pygame timers and variables===
run = True
score = 0
# pygame.time.set_timer(USEREVENT+1, 500)
pygame.time.set_timer(USEREVENT+2, 3000)
# global obj_capture #stores the last recognized object in the camera frame
# obj_capture = "none"

def redrawWindow():
    global obj_capture
    global hero #for drawing relative to hero position
    win.blit(bg_im, (-80,-140)) #background draw
    #global disp_objects
    largeFont = pygame.font.SysFont('comicsans', 25)
    #outerFont = pygame.font.SysFont('comicsans', 27)
    #win.blit(bg, (bgX, 0))
    #win.blit(bg, (bgX2,0))
    health_text = largeFont.render('Health: '+str(hero.health), 1, (255,255,255))
    #health_border = outerFont.render('Health: '+str(hero.health), 1, (255,255,255))
    hero_text = largeFont.render('Equipped: '+str(hero.env_type), 1, (255,255,255))
    env_text = largeFont.render('Current Env: '+str(env1.type), 1, (255,255,255))
    for obstacle in disp_objects:
        if isinstance(obstacle,classes_multi.item):
            obstacle.draw(win,hero)
        else:
            obstacle.draw(win)
            
    #win.blit(health_border, (10, 10))
    win.blit(health_text, (10, 10))
    win.blit(env_text, (10,24))
    win.blit(hero_text, (10,36))
    
    #icon indicators for player
    win.blit(stop_im, (290,10))
    win.blit(prayer_im, (290,80))
    win.blit(left_im, (290,150))
    win.blit(right_im, (290,210))
    
    pygame.display.update()

def drop_item_noncb():
    global all_objects
    global disp_objects
    global obj_capture
    if(obj_capture in recog_knife):
        knife = classes_multi.weapon("../rightknife.png", "knife", 310, 50, 310, 50, 30, 30, True, 10)
        knife.speedx = -10
        disp_objects.append(knife)
    elif(obj_capture in recog_fruit):
        apple = classes_multi.item("../apple.png", "apple", 310, 50, 310, 50, 30, 30, False)
        apple.speedx = -10
        disp_objects.append(apple)
    elif(obj_capture in recog_armor):
        shirt = classes_multi.armor("../armor.png", "armor", 310, 50, 310, 50, 15, 15, True, 10, "cold", "torso")
        shirt.speedx = -10
        disp_objects.append(shirt)

#connect buttons to callbacks
# GPIO.add_event_detect(17, GPIO.FALLING, callback=quit_game, bouncetime=100)
# GPIO.add_event_detect(23, GPIO.BOTH, callback=move_hero_left, bouncetime=100)
# GPIO.add_event_detect(27, GPIO.BOTH, callback=move_hero_right, bouncetime=100)
# GPIO.add_event_detect(22, GPIO.FALLING, callback = switch_state, bouncetime=100)
#======================end gameplay setup====================================

#client send the game data over the network
client = Client(hostname, port)
client.connect()

#finite state machine
GAME_STATE = 4
GAME_PLAY = 1
OBJ_DETECT = 2
END_SCREEN = 3
MENU_SCREEN = 4

while run : #main game loop
    clock.tick(40)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_RIGHT]:
        hero.moveRight()
    elif keys[pygame.K_LEFT]:
        hero.moveLeft()
    else:
        hero.speedx = 0

    if keys[pygame.K_UP]:
        hero.jump()

    if GAME_STATE==MENU_SCREEN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.K_ESCAPE:
                run = False
                pygame.quit()
        title_font = pygame.font.SysFont('comicsans', 50)
        color = 200,200,200
        title_text = title_font.render('It\'s Dangerous', 1, (color))
        title_text2 = title_font.render('to Go Alone...', 1, (color))
        win.blit(title_text, (10, 80))
        win.blit(title_text2, (10, 110))
        pygame.display.update()
        time.sleep(3)
        GAME_STATE = GAME_PLAY
    elif GAME_STATE==END_SCREEN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if event.type == pygame.K_ESCAPE:
                run = False
                pygame.quit()
        win.fill((BLACK))
        end_font = pygame.font.SysFont('comicsans', 50)
        end_text = end_font.render('You Died', 1, (255,0,0))
        win.blit(end_text, (80, 80))
        pygame.display.update()
        time.sleep(3)
        win.fill((BLACK))
        pygame.display.update()
        time.sleep(3)
        #reset hero
        hero = classes_multi.character("../staticBoy.png", 50, 50, 50, 50, 50, 50)
        hero.speedx = 0
        hero.speedy = 2
        disp_objects.append(hero)
        all_objects.append(hero)
        GAME_STATE = MENU_SCREEN
    elif GAME_STATE==GAME_PLAY:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type is MOUSEBUTTONDOWN:
                hero.jump()
            if event.type == USEREVENT+2: #3 second timer
                #check for environment matched
                if((not env1.type=="none") and (not env1.type==hero.env_type)):
                    hero.health -= 1
            if event.type == pygame.K_ESCAPE:
                run = False
                pygame.quit()
        #check for end state
        if(hero.health<=0 or hero.y>=280):
            #remove all of the hero's assets
            for item in hero.inventory:
                if item.equippable:
                    disp_objects.remove(item)
            #remove the hero itself
            disp_objects.remove(hero)
            all_objects.remove(hero)
            GAME_STATE = END_SCREEN
        #move everything x
        classes_multi.move_objs(disp_objects, 'x')
        #check for x collisions
        classes_multi.collide(disp_objects, 'x')
        #move everything y
        classes_multi.move_objs(disp_objects, 'y')
        #check for y collisions
        classes_multi.collide(disp_objects, 'y')  
        #clock.tick(40)
        win.fill(BLACK)
        redrawWindow()
    
    # #update the displayable objects
    # #by sending the changes to the server
    print("sending")
    data_send = pickle.dumps(disp_objects)
    try:
        client.s.send(data_send)
    except socket.error as e:
        print(str(e))
    
            
#GPIO.cleanup()
pygame.quit()
#cv2.destroyAllWindows()
#videostream.stop()
