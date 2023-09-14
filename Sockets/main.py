import sys

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QGroupBox,
                               QHBoxLayout, QMainWindow,
                               QSizePolicy, QWidget)

from Modules.SocketClient.Client import Client
from Modules.Graph.Graph import GraphHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle("Server side application")
        self.setGeometry(0, 0, 800, 500)
        self.path = 'C:\\Users\\shustad\\Desktop\\Prog\\Sockets\\Resources'

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
        self.client = Client()
        self.clientGroup = QGroupBox('Client interface')
        self.clientGroup.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.clientGroup.setLayout(self.client.layout)
        self.client.dataSignal.connect(self.Graph.dataMessage)
        self.client.start()


        # Main layout
        layout = QHBoxLayout()
        layout.addWidget(self.graphGroup, 90)
        layout.addWidget(self.clientGroup, 10)

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    @Slot()
    def exit(self):
        print('Exiting...')
        self.client.running = False
        # Give time for the thread to finish
        self.client.wait()
        self.close()

if __name__ == "__main__":
    app = QApplication()
    w = MainWindow()
    w.show()
    sys.exit(app.exec())