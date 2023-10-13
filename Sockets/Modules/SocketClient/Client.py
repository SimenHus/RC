import socket
from PySide6.QtCore import QThread, Signal, Slot

import pickle

class Client(QThread):
    dataSignal = Signal(dict)
    statusSignal = Signal(str)

    def __init__(self, host='127.0.0.1', port=65432, *args, **kwargs):
        super().__init__()

        # Server variables
        self.HOST = host
        self.PORT = port
        self.running = True


    def run(self):
        # Main loop. Will stop running if self.running = False
        
        # Initialize client
        timeout = 5
        while self.running:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.settimeout(timeout)
                try: client.connect((self.HOST, self.PORT)) # Connect to server IP and port
                except: continue # If not server found, check again
                client.settimeout(None)
                self.connected(client) # If server found, handle communication
                self.statusSignal.emit('Not connected') # Inform that client has disconnected
                
    
    def connected(self, client):
        # Function to handle server communication
        self.statusSignal.emit('Connected') # Inform that the client is connected
        while self.running:
            try:
                data = client.recv(1024) # Get message from server
                if not data: break # If disconnected from server, data is empty
            except: break
            data = pickle.loads(data) # Load binary socket message
            self.dataSignal.emit(data)
