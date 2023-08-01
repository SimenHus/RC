import socket
from PySide6.QtCore import QThread, Signal
import pickle
import numpy as np

class socketServer(QThread):
    statusMessage = Signal(str)
    dataMessage = Signal(np.ndarray)

    def __init__(self, host='127.0.0.1', port=65432, *args, **kwargs):
        super().__init__()

        self.HOST = host
        self.PORT = port
        self.running = True

    def run(self):

        self.statusMessage.emit('Server is running')
        while self.running:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.settimeout(1)
                server.bind((self.HOST, self.PORT))
                server.listen()
                try: user, addr = server.accept()
                except: continue
                with user:
                    self.statusMessage.emit(f'Connected to {addr}')
                    while self.running:
                        data = user.recv(1024)
                        if not data: break
                        self.dataMessage.emit(pickle.loads(data))
                self.statusMessage.emit('Client closed connection')
