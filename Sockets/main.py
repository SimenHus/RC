import sys

from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QAction, QKeySequence, QKeyEvent
from PySide6.QtWidgets import (QApplication, QGroupBox,
                               QHBoxLayout, QMainWindow,
                               QSizePolicy, QWidget, QLabel)

from Modules.SocketClient.ClientAsync import Client
from Modules.Graph.Graph import GraphHandler



class MainWindow(QMainWindow):
    outgoingSignal = Signal(set)
    def __init__(self):
        super().__init__()
        # Title and dimensions
        self.setWindowTitle("Client side application")
        self.setGeometry(0, 0, 800, 500)
        self.path = 'C:\\Users\\simen\\Desktop\\Prog\\Python\\RC-Workbranch\\Sockets\\Resources'

        self.Graph = GraphHandler()
        self.Client = Client()
        self.outgoingSignal.connect(self.Client.OutgoingAgent)
        self.Client.dataSignal.connect(self.Graph.dataMessage)
        self.Client.statusSignal.connect(self.connectionStatus)
        self.Client.start()

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

        self.keyboardSet = set({})
        # Main layout
        layout = self.Graph.layout

        # Central widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def controlButtonCB(self) -> None:
        self.outgoingSignal.emit(self.keyboardSet)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.isAutoRepeat(): return
        key = event.keyCombination().key()
        self.keyboardSet.add(key)
        self.controlButtonCB()
    
    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.isAutoRepeat(): return
        key = event.keyCombination().key()
        self.keyboardSet.remove(key)
        self.controlButtonCB()

    @Slot()
    def connectionStatus(self, status) -> None:
        self.connectionStatusWidget.setText(status)

    @Slot()
    def exit(self) -> None:
        print('Exiting...')
        self.Client.running = False
        # Give time for the thread to finish
        self.Client.wait()
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