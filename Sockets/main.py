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
        self.setWindowTitle("Graphing")
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
        self.server.dataMessage.connect(self.dataMessage)
        self.server.start()


        # Buttons layout
        buttons_layout = QHBoxLayout()
        self.button1 = QPushButton("Next")
        self.button2 = QPushButton("Prev")
        self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        buttons_layout.addWidget(self.button2)
        buttons_layout.addWidget(self.button1)

        
        serverAndGraphLayout = QHBoxLayout()
        serverAndGraphLayout.addWidget(self.graphGroup)
        serverAndGraphLayout.addWidget(self.serverGroup)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(serverAndGraphLayout)
        layout.addLayout(buttons_layout)

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

    @Slot()
    def dataMessage(self, data):
        self.Graph.updatePlotData(data)


if __name__ == "__main__":
    app = QApplication()
    w = MainWindow()
    w.show()
    sys.exit(app.exec())