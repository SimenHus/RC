import socket
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser)
import pickle
import numpy as np

class Server(QThread):
    dataMessage = Signal(np.ndarray)
    clientConnected = Signal(list)

    def __init__(self, host='127.0.0.1', port=65432, *args, **kwargs):
        super().__init__()

        # Server variables
        self.HOST = host
        self.PORT = port
        self.running = True

        # Interface box for server settings
        self.serverSettings = QGroupBox('Server settings')
        self.serverSettings.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.serverDisplay = QTextBrowser()
        
        serverSettingsLayout = QVBoxLayout()
        self.serverSettings.setLayout(serverSettingsLayout)

        # Set server interface layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.serverDisplay, 80)
        self.layout.addWidget(self.serverSettings, 20)

    @Slot()
    def statusMessage(self, data):
        # Function to display status messages for the server
        self.serverDisplay.append(str(data))

    def run(self):
        # Main loop. Will stop running if self.running = False
        
        # Initialize server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.settimeout(1) # Set client wait timeout
            server.bind((self.HOST, self.PORT)) # Set server IP and port
            server.listen() # Set the server to be a listening socket
            self.statusMessage('Server is running') # Inform that the server is ready
            while self.running:
                try: user, addr = server.accept() # Check for client. If waiting > timeout it will raise exception
                except: continue # If not client found, check again
                with user: self.handleClient(user, addr) # If client found, handle communication
                self.statusMessage('Client closed connection') # Inform that client has disconnected
    
    def handleClient(self, user, addr):
        # Function to handle client communication
        self.statusMessage(f'Connected to {addr}')
        while self.running:
            data = user.recv(1024) # Get message from client
            if not data: break # If client has disconnected, data is 0
            data = pickle.loads(data) # Load binary socket message
            if data['MessageType'] == 'Init': self.clientConnected.emit(data['Data'])
            if data['MessageType'] == 'Data': self.dataMessage.emit(data['Data'])
