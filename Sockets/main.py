import sys

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser)

from SocketServer import Server
from GraphHandler import GraphHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle("Server side application")
        self.setGeometry(0, 0, 800, 500)

        # Main menu bar
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("File")
        exit = QAction("Exit", self, triggered=self.exit)
        self.menu_file.addAction(exit)

        self.menu_about = self.menu.addMenu("&About")
        about = QAction("About Qt", self, shortcut=QKeySequence(QKeySequence.HelpContents),
                        triggered=qApp.aboutQt)
        self.menu_about.addAction(about)


        # Graph window
        self.Graph = GraphHandler()
        self.graphGroup = QGroupBox('Graph')
        self.graphGroup.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.graphGroup.setLayout(self.Graph.layout)

        # Server window
        self.server = Server()
        self.serverGroup = QGroupBox('Server')
        self.serverGroup.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.serverGroup.setLayout(self.server.layout)
        self.server.dataMessage.connect(self.Graph.dataMessage)
        self.server.clientConnected.connect(self.Graph.clientConnected)
        self.server.start()

        
        serverAndGraphLayout = QHBoxLayout()
        serverAndGraphLayout.addWidget(self.graphGroup, 70)
        serverAndGraphLayout.addWidget(self.serverGroup, 30)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(serverAndGraphLayout)

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    @Slot()
    def exit(self):
        print('Exiting...')
        self.server.running = False
        # Give time for the thread to finish
        self.server.wait()
        self.close()

if __name__ == "__main__":
    app = QApplication()
    w = MainWindow()
    w.show()
    sys.exit(app.exec())