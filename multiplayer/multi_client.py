import socket, pickle

class tst_obj:
    def __init__(self, img, x_pos, y_pos, x_speed, y_speed):
        self.image = img
        self.x = x_pos
        self.y = y_pos
        self. speedx = x_speed
        self.speedy = y_speed

class Client:
    def __init__(self, HOST, PORT):