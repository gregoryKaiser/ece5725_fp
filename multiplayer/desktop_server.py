import socket, pickle
import classes_multi

class Server:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = None
        self.conn = None
        self.addr = None
    
    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.bind((self.HOST, self.PORT))
        except socket.error as e:
            print(str(e))
        self.s.listen(1)
        print("Waiting for a connection")
        self.conn, self.addr = self.s.accept()
        print( "Connected by: ", self.addr)
        return self.conn, self.addr

    def get_data(self):
        data = self.conn.recv(4096)
        data_var = pickle.loads(data)
        return data_var

    def close_connection(self):
        self.conn.close()

hostname = 'localhost'
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
# global hero
hero = classes_multi.character("../staticBoy.png", 90, 50, 90, 50, 50, 50)
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
    global hero #for drawing relative to hero position and health
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
        knife = classes_multi.weapon("../knife.png", "knife", 310, 50, 310, 50, 30, 30, True, 10)
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

#server send the game data over the network
server = Server(hostname, port)
server.connect()

#finite state machine
GAME_STATE = 4
GAME_PLAY = 1
OBJ_DETECT = 2
END_SCREEN = 3
MENU_SCREEN = 4

while run : #main game loop
    clock.tick(40)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
    #update the displayable objects
    #by getting changes from the client
    try:
        data_unpack = server.get_data() 
        print('Data recieved:',data_unpack)
        disp_objects = data_unpack
    except:
        print("Closing connection")
        server.close_connection()
        break
    
    win.fill(BLACK)
    redrawWindow()

#GPIO.cleanup()
pygame.quit()
#cv2.destroyAllWindows()
#videostream.stop()


