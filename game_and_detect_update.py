#
import os
import random
import classes
import RPi.GPIO as GPIO
import time
import subprocess

import argparse
import cv2
import numpy as np
import sys
from threading import Thread
import importlib.util
import pygame
from pygame.locals import *

#TFT stuff
#os.putenv('SDL_VIDEODRIVER','fbcon')
#os.putenv('SDL_FBDEV','/dev/fb1')#might have to change to fb1
os.putenv('SDL_MOUSEDRV','TSLIB') #Track mouse clicks on piTFT
os.putenv('SDL_MOUSEDEV','/dev/input/touchscreen')

#pygame initialization
pygame.init()
W, H = 320, 240
BLACK = 0,0,0
win = pygame.display.set_mode((W, H))
pygame.mouse.set_visible(False)

pygame.display.set_caption('It\'s Dangerous To Go Alone...')
#========================object detection setup=======================
# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(320,240),framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

	# Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
	# Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
	# Return the most recent frame
        return self.frame

    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True

# Define and parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', help='Folder the .tflite file is located in',
                    required=True)
parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                    default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                    default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                    default=0.5)
parser.add_argument('--resolution', help='Desired webcam resolution in WxH. If the webcam does not support the resolution entered, errors may occur.',
                    default='1280x720')
parser.add_argument('--edgetpu', help='Use Coral Edge TPU Accelerator to speed up detection',
                    action='store_true')

args = parser.parse_args()

MODEL_NAME = args.modeldir
GRAPH_NAME = args.graph
LABELMAP_NAME = args.labels
min_conf_threshold = float(args.threshold)
resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)
use_TPU = args.edgetpu

# Import TensorFlow libraries
# If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
# If using Coral Edge TPU, import the load_delegate library
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
    if use_TPU:
        from tflite_runtime.interpreter import load_delegate
else:
    from tensorflow.lite.python.interpreter import Interpreter
    if use_TPU:
        from tensorflow.lite.python.interpreter import load_delegate

# If using Edge TPU, assign filename for Edge TPU model
if use_TPU:
    # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
    if (GRAPH_NAME == 'detect.tflite'):
        GRAPH_NAME = 'edgetpu.tflite'       

# Get path to current working directory
CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del(labels[0])

# Load the Tensorflow Lite model.
# If using Edge TPU, use special load_delegate argument
if use_TPU:
    interpreter = Interpreter(model_path=PATH_TO_CKPT,
                              experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    print(PATH_TO_CKPT)
else:
    interpreter = Interpreter(model_path=PATH_TO_CKPT)

interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()

# Initialize video stream
videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
time.sleep(1)
#=============end object detection setup===============================
#==============gameplay main==================================
GPIO.setmode(GPIO.BCM)

#Button setup
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #init but 17, close to power supply
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP) #init but 22 signal
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

#finite state machine
GAME_STATE = 4
GAME_PLAY = 1
OBJ_DETECT = 2
END_SCREEN = 3
MENU_SCREEN = 4

#recognizable objects taken from "lablemap.txt" in Sample_TFLite_model
#recog_obj = ["knife","scissors","apple","banana","person","bed","tv","laptop","mouse","keyboard","cell phone","book"]
recog_knife = ["knife", "scissors"]
recog_fruit = ["apple","banana","bed","person"]
recog_armor = ["umbrella","backpack","tie"]

def switch_state(channel):
    global GAME_STATE
    global GAME_PLAY
    global OBJ_DETECT
    global obj_capture
    #global run
    #print("switch",GAME_STATE)
    if GAME_STATE==GAME_PLAY:
        GAME_STATE = OBJ_DETECT
    elif GAME_STATE==OBJ_DETECT:
        GAME_STATE = GAME_PLAY
        if (not obj_capture=="none"):# and obj_capture in recog_obj):
            #spawn an object
            drop_item_noncb()
    #print("switch",GAME_STATE)
    #run=False

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


#image assets-------------------------------
hero_im = pygame.image.load("staticBoy.png")
hero_im = pygame.transform.scale(hero_im,(50,50))
ground_im = pygame.image.load("Ground.png")
ground_im = pygame.transform.scale(ground_im, (320, 40))
circle_im = pygame.image.load("circle.png")
circle_im2 = pygame.transform.scale(circle_im, (30,30))
circle_im = pygame.transform.scale(circle_im, (100,100))
brick = pygame.image.load("brick.png")
brick = pygame.transform.scale(brick, (40,40))
knife_im = pygame.image.load("knife.png")
knife_im = pygame.transform.scale(knife_im,(30,30))
apple_im = pygame.image.load("apple.png")
apple_im = pygame.transform.scale(apple_im,(30,30))
armor_im = pygame.image.load("armor.png")
armor_im = pygame.transform.scale(armor_im,(15,15))
#image assets above-------------------------------

clock = pygame.time.Clock()

#====Create game objects====
global hero
hero = classes.character(hero_im, 50, 50, 50, 50, 25, 50)
hero.speedx = 0
hero.speedy = 2

env1 = classes.environment(100, 300, "cold", 1)
block = classes.obstacle(brick, 150, 160, 150, 160, 40, 40, "hot")
block2 = classes.obstacle(brick, 30, 100, 30, 100, 40, 40, "hot")
floor = classes.obstacle(ground_im, 0, 200, 0, 200, 320, 15, "normal")

all_objects = [hero, env1, floor, block]
disp_objects = [hero, floor, block, block2]
#====pygame timers and variables===
run = True
score = 0
# pygame.time.set_timer(USEREVENT+1, 500)
pygame.time.set_timer(USEREVENT+2, 3000)
global obj_capture #stores the last recognized object in the camera frame
obj_capture = "none"

def redrawWindow():
    global obj_capture
    global hero #for drawing relative to hero position
    #global disp_objects
    largeFont = pygame.font.SysFont('comicsans', 20)
    #win.blit(bg, (bgX, 0))
    #win.blit(bg, (bgX2,0))
    health_text = largeFont.render('Health: ' + str(hero.health), 1, (255,0,0))
    hero_text = largeFont.render('Hero:'+str(hero.env_type), 1, (255,255,255))
    env_text = largeFont.render('Current Env:'+str(env1.type), 1, (255,255,255))
    for obstacle in disp_objects:
        if isinstance(obstacle,classes.item):
            obstacle.draw(win,hero)
        else:
            obstacle.draw(win)
    win.blit(health_text, (10, 10))
    win.blit(env_text, (10,22))
    win.blit(hero_text, (10,34))
    
    #icon indicators for player
    
    
    pygame.display.update()

def drop_item(channel):
    global all_objects
    global disp_objects
    shirt = classes.armor(circle_im2, "shirt", 310, 50, 310, 50, 30, 30, True, 10, "hot", "torso")
    shirt.speedx = -5
    disp_objects.append(shirt)

def drop_item_noncb():
    global all_objects
    global disp_objects
    global obj_capture
    if(obj_capture in recog_knife):
        knife = classes.weapon(knife_im, "knife", 310, 50, 310, 50, 30, 30, True, 10)
        knife.speedx = -10
        disp_objects.append(knife)
    elif(obj_capture in recog_fruit):
        apple = classes.item(apple_im, "apple", 310, 50, 310, 50, 30, 30, False)
        apple.speedx = -10
        disp_objects.append(apple)
    elif(obj_capture in recog_armor):
        shirt = classes.armor(armor_im, "armor", 310, 50, 310, 50, 15, 15, True, 10, "cold", "torso")
        shirt.speedx = -10
        disp_objects.append(shirt)

#connect buttons to callbacks
GPIO.add_event_detect(17, GPIO.FALLING, callback=quit_game, bouncetime=100)
GPIO.add_event_detect(23, GPIO.BOTH, callback=move_hero_left, bouncetime=100)
GPIO.add_event_detect(27, GPIO.BOTH, callback=move_hero_right, bouncetime=100)
GPIO.add_event_detect(22, GPIO.FALLING, callback = switch_state, bouncetime=100)
#======================end gameplay setup====================================

while run : #main game loop
    clock.tick(40)
    if GAME_STATE==MENU_SCREEN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
        title_font = pygame.font.SysFont('comicsans', 50)
        color = (200,200,200)
        title_text = title_font.render('It\'s Dangerous', 1, color)
        title_text2 = title_font.render('to Go Alone...', 1, color)
        win.blit(title_text, (10, 120))
        win.blit(title_text2, (10, 150))
        pygame.display.update()
        time.sleep(3)
        GAME_STATE = GAME_PLAY
    elif GAME_STATE==END_SCREEN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
        win.fill((BLACK))
        end_font = pygame.font.SysFont('comicsans', 50)
        end_text = end_font.render('You Died', 1, (255,0,0))
        win.blit(end_text, (60, 120))
        pygame.display.update()
        time.sleep(3)
        win.fill((BLACK))
        pygame.display.update()
        time.sleep(3)
        #reset hero
        hero = classes.character(hero_im, 50, 50, 50, 50, 25, 50)
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
        #check for end state
        if(hero.health<=0 or hero.y>=340):
            disp_objects.remove(hero)
            all_objects.remove(hero)
            GAME_STATE = END_SCREEN
        #move everything x
        classes.move_objs(disp_objects, 'x')
        #check for x collisions
        classes.collide(disp_objects, 'x')
        #move everything y
        classes.move_objs(disp_objects, 'y')
        #check for y collisions
        classes.collide(disp_objects, 'y')  
        #clock.tick(40)
        win.fill(BLACK)
        redrawWindow()
    elif GAME_STATE==OBJ_DETECT:
        #below is mostly from the tutorial script-----
        #for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
        
        # Start timer (for calculating frame rate)
        t1 = cv2.getTickCount()

        # Grab frame from video stream
        frame1 = videostream.read()

        # Acquire frame and resize to expected shape [1xHxWx3]
        frame = frame1.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes_obj = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
        #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

        # Loop over all detections and draw detection box if confidence is above minimum threshold
        for i in range(len(scores)):
            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):
                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))
                
                cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                # Draw label
                object_name = labels[int(classes_obj[i])] # Look up object name from "labels" array using class index
                label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
        if (len(scores)>0 and (scores[0]>min_conf_threshold)):
            obj_capture = labels[int(classes_obj[0])]
        else:
            obj_capture = "none"
            
        #rotate to align with our setup
        frame = cv2.rotate(frame, cv2.cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        # Draw framerate in corner of frame
        cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)

        ## All the results have been drawn on the frame, so it's time to display it.
        #cv2.imshow('Object detector', frame)
        
        #ghk48: write to temp file so pygame can read and display
        cv2.imwrite('./tmp.bmp', frame) #write frame
        img = pygame.image.load('./tmp.bmp') #read frame
        win.fill((0,0,0)) #clear screen
        win.blit(img, (0,0)) #add frame
        pygame.display.update()
        
        # Calculate framerate
        t2 = cv2.getTickCount()
        time1 = (t2-t1)/freq
        frame_rate_calc= 1/time1
    
            
GPIO.cleanup()
pygame.quit()
cv2.destroyAllWindows()
videostream.stop()
