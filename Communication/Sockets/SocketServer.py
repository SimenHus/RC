import socket
import pickle
import numpy as np
from time import sleep

from threading import Thread

# python Desktop\Prog\Sockets\SocketServer.py

class Server:
    def __init__(self, host='127.0.0.1', port=65432, *args, **kwargs):

        # Server variables
        self.HOST = host
        self.PORT = port
        self.running = True

    def run(self):
        # Main loop. Will stop running if self.running = False
        activeClients = []
        # Initialize server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.settimeout(1) # Set client wait timeout
            server.bind((self.HOST, self.PORT)) # Set server IP and port
            server.listen() # Set the server to be a listening socket
            print('Server ready')
            while self.running:
                try: user, addr = server.accept() # Check for client. If waiting > timeout it will raise exception
                except: continue # If not client found, check again
                newClient = clientHandler(user, addr) # If client found, handle communication
                activeClients.append(newClient)
                newClient.start()


class clientHandler(Thread):
    def __init__(self, client, addr):
        super().__init__()
        self.client = client
        self.addr = addr
        self.running = True
        self.daemon = True


        self.t = 0
        self.steps = 10
    
    def run(self):
        print('Client connected')
        with self.client as client:
            while self.running:
                try: client.sendall(pickle.dumps(self.dataFromFile()))
                except: break
                sleep(0.1)
        print('Client disconnected')

    def dataFromFile(self):
        with open('C:\\Users\\shustad\\Desktop\\Prog\\RC\\Backups and Misc\\Robowars\\sensordata\\spinning.npy', 'rb') as f:
            data = np.load(f)
        MAX_VAL = 2**15
        ACCEL_RANGE = MAX_VAL/16
        GYRO_RANGE = MAX_VAL/2000
        MAGN_RANGE = MAX_VAL/4900

        # Extract and convert values
        time = (data[:, 0] - data[0, 0])/1000
        accel = data[:, 1:4]/ACCEL_RANGE
        gyro = data[:, 4:7]/GYRO_RANGE
        mag = data[:, 7:10]/MAGN_RANGE
        temp = 21 + (data[:, 10] - 21)/334

        data = {
            'acc': accel,
            'gyro': gyro,
            # 'mag': mag
        }



        end = len(data['acc'][:, 0])
        states = {}
        if self.t+self.steps >= end: self.t = 0
        for state, values in data.items():
            states[state] = values[self.t:self.t+self.steps, :]
        self.t += self.steps
        return states
        


if __name__ == '__main__':
    server = Server()
    server.run()