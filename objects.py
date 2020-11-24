#FOR ALL INDIVIDUAL WORK: make a seperate file

#hero
#globals - Caeli
#   environment type
#   global positoin

#character - Greg
#   move left
#   move right
#   jump
#   attack
#   use item
#   signal to other player
#       ask
#       +
#       -

#items - Caeli
#   fall from sky (and collide and stop on floor)
#   get picked up (collide)
#   modify character attribute
#   can be equipped (show next to character)
#   type

#enemies (hold off for now)
#   move left
#   move right
#   attack

#obstacles - Greg
#   collide for platforming
#   type

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

class hero(object):
    #image assets
    #TODO: get image and define image path
    #image = pygame.image.load(os.path(??))
    image = 0
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.jumping = False
        self.sliding = False
        self.falling = False
        self.slideCount = 0
        self.jumpCount = 0
        self.runCount = 0
        self.slideUp = False

        self.health = 100
        self.inventory = {}
        self.attack = 0
        self.defense = 0
        self.speed = (2,2) #y-speed?

    def draw(self, win):
        #could cycle through images for animation
        win.blit(image, (self.x, self.y))