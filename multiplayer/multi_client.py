import socket, pickle
import classes_multi

class tst_obj:
    def __init__(self, img, x_pos, y_pos, x_speed, y_speed):
        self.image = img
        self.x = x_pos
        self.y = y_pos
        self. speedx = x_speed
        self.speedy = y_speed

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
testing = tst_obj(1, 50, 50, 2, 2)
client = Client(hostname, port)
client.connect()

while(True):
    print("sending")
    data_send = pickle.dumps(testing)
    try:
        client.s.send(data_send)
    except socket.error as e:
        print(str(e))