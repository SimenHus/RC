import sys

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QGroupBox,
                               QHBoxLayout, QMainWindow,
                               QSizePolicy, QWidget, QLabel)

from Modules.SocketClient.Client import Client
from Modules.Graph.Graph import GraphHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle("Client side application")
        self.setGeometry(0, 0, 800, 500)
        self.path = 'C:\\Users\\shustad\\Desktop\\Prog\\RC-Workbranch\\Sockets\\Resources'

        # Graph window
        self.Graph = GraphHandler()

        # Server window
        self.client = Client()
        self.client.dataSignal.connect(self.Graph.dataMessage)
        self.client.statusSignal.connect(self.connectionStatus)
        self.client.start()

        # Main menu bar
        self.menu = self.menuBar()
        menu_file = self.menu.addMenu("File")
        menu_about = self.menu.addMenu("&About")
        menu_graph = self.menu.addMenu('Graph')

        exit = menu_file.addAction('Exit')
        exit.triggered.connect(self.exit)

        about = menu_about.addAction("About Qt")
        about.triggered.connect(qApp.aboutQt)

        addGraph = menu_graph.addAction('Add graph')
        addGraph.triggered.connect(self.Graph.addGraph)

        removeGraph = menu_graph.addAction('Remove graph')
        removeGraph.triggered.connect(self.Graph.removeGraph)

        # Status bar
        self.statusBar = self.statusBar()

        self.connectionStatusWidget = QLabel('Not connected')
        self.statusBar.addWidget(self.connectionStatusWidget)


        # Main layout
        layout = self.Graph.layout

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    @Slot()
    def connectionStatus(self, status) -> None:
        self.connectionStatusWidget.setText(status)

    @Slot()
    def exit(self) -> None:
        print('Exiting...')
        self.client.running = False
        # Give time for the thread to finish
        self.client.wait()
        self.close()

if __name__ == "__main__":
    app = QApplication()
    w = MainWindow()
    w.show()
    
    with open(f'{w.path}\\styleVariables.txt', 'r') as f: varList = f.readlines()
    with open(f'{w.path}\\style.qss', 'r') as f: styleSheet = f.read()
    for var in varList:
        name, value = var.split('=')
        styleSheet = styleSheet.replace(name, value)
    app.setStyleSheet(styleSheet)
    sys.exit(app.exec())