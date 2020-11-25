class character(object):
    #image assets
    #TODO: get image and define image path
    #image = pygame.image.load(os.path(??))
    image = 0
    def __init__(self, x, y, glob_x, glob_y, width, height):
        self.x = x
        self.y = y
        self.glob_x = glob_x
        self.glob_y = glob_y
        self.width = width
        self.height = height
        self.speedx = 0 #set high during button press
        self.speedy = 0 #set high when jumping

        self.health = 100
        self.inventory = {}
        self.attack = 0
        self.defense = 0
        self.speed = (2,2) #y-speed?
        self.signaling = 0

    def draw(self, win):
        win.blit(image, (self.x, self.y))
        if self.signaling:
            win.blit(sig_image, (self.x, self.y+20))
    def moveRight(self): #upon button press
        self.speedx = 5

    def moveLeft(self): #upon button press
        self.speedx = -5

    def jump(self): #upon button press
        self.speedy = 5

    def stopMoving(self): #upon button release
        self.speedx = 0

    def stop_signal(self): #upon signal button release
        self.signaling = 0

    def signal(self): #upon button press
        self.signaling = 1
