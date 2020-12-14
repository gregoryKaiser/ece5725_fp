import socket, pickle

class tst_obj:
    def __init__(self, img, x_pos, y_pos, x_speed, y_speed):
        self.image = img
        self.x = x_pos
        self.y = y_pos
        self. speedx = x_speed
        self.speedy = y_speed

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
server = Server(hostname, port)
server.connect()

while(True):
    try:
        data_unpack = server.get_data()
        print('Data recieved:',data_unpack)
    except:
        print("Closing connection")
        server.close_connection()
        break


