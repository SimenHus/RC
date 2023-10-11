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
        self.setWindowTitle("Server side application")
        self.setGeometry(0, 0, 800, 500)
        self.path = 'C:\\Users\\shustad\\Desktop\\Prog\\RC-Workbranch\\Sockets\\Resources'

        # Graph window
        self.Graph = GraphHandler()
        self.graphGroup = QGroupBox('Graph')
        self.graphGroup.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.graphGroup.setLayout(self.Graph.layout)

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

        test = menu_graph.addAction('Add state')
        test.triggered.connect(lambda: self.Graph.addStateToGraph(self.Graph.graphWidgets[0], 'gyro_1'))

        # Status bar
        self.statusBar = self.statusBar()

        self.connectionStatusWidget = QLabel('Not connected')
        self.statusBar.addWidget(self.connectionStatusWidget)


        # Main layout
        layout = QHBoxLayout()
        layout.addWidget(self.graphGroup, 90)

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
    
    with open(f'{w.path}\\style.qss', 'r') as f: app.setStyleSheet(f.read())
    sys.exit(app.exec())