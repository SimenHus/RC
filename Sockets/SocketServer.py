import socket
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser)
import pickle
import numpy as np

class Server(QThread):
    dataMessage = Signal(np.ndarray)

    def __init__(self, host='127.0.0.1', port=65432, *args, **kwargs):
        super().__init__()

        self.HOST = host
        self.PORT = port
        self.running = True

        self.serverSettings = QGroupBox('Server settings')
        self.serverSettings.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.serverDisplay = QTextBrowser()
        
        serverSettingsLayout = QVBoxLayout()
        self.serverSettings.setLayout(serverSettingsLayout)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.serverDisplay)
        self.layout.addWidget(self.serverSettings)

    def statusMessage(self, data):
        self.serverDisplay.append(str(data))

    def run(self):

        self.statusMessage('Server is running')
        while self.running:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.settimeout(1)
                server.bind((self.HOST, self.PORT))
                server.listen()
                try: user, addr = server.accept()
                except: continue
                with user:
                    self.statusMessage(f'Connected to {addr}')
                    while self.running:
                        data = user.recv(1024)
                        if not data: break
                        self.dataMessage.emit(pickle.loads(data))
                self.statusMessage('Client closed connection')
