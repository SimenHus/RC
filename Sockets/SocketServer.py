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
    
    def run(self):
        print('Client connected')
        with self.client as client:
            nStates = 2
            t = np.array([0])
            funcs = [np.sin, np.cos]
            states = []
            for i in range(nStates):
                # newState = {'Name': f'x{i+1}', 'x0': np.random.default_rng().standard_normal(1)*10}
                newState = {'Name': f'x{i+1}', 'x0': funcs[i%len(funcs)](t)}
                states.append(newState)

            connectMsg = {'MessageType': 'Init', 'Data': states}
            client.sendall(pickle.dumps(connectMsg))
            sleep(1)
            while self.running:
                # data = [{'Name': f'x{i+1}', 'Measurement': np.random.default_rng().standard_normal(1)*10} for i in range(nStates)]
                data = [{'Name': f'x{i+1}', 'Measurement': funcs[i%len(funcs)](t*0.1)} for i in range(nStates)]
                dataMsg = {'MessageType': 'Data', 'Data': data}
                try: client.sendall(pickle.dumps(dataMsg))
                except: break
                t[0] += 1
                sleep(0.1)
        print('Client disconnected')

if __name__ == '__main__':
    server = Server()
    server.run()