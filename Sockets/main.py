import sys

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser)

import pyqtgraph as pg
import numpy as np

from socketServer import socketServer

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
        self.graphGroup = QGroupBox('Graph')
        self.graphSettings = QGroupBox("Graph settings")
        self.graphGroup.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.graphSettings.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.initGraph()

        graphBoxLayout = QVBoxLayout()
        graphSettingsLayout = QVBoxLayout()

        graphBoxLayout.addWidget(self.graphWidget)
        graphBoxLayout.addWidget(self.graphSettings)

        self.graphSettings.setLayout(graphSettingsLayout)
        self.graphGroup.setLayout(graphBoxLayout)

        # Socket server window
        self.serverGroup = QGroupBox('Server')
        self.serverSettings = QGroupBox('Server settings')
        self.serverGroup.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.serverSettings.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        serverBoxLayout = QVBoxLayout()
        serverSettingsLayout = QVBoxLayout()
        self.serverDisplay = QTextBrowser()
        
        serverBoxLayout.addWidget(self.serverDisplay)
        serverBoxLayout.addWidget(self.serverSettings)

        self.serverSettings.setLayout(serverSettingsLayout)
        self.serverGroup.setLayout(serverBoxLayout)


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

        self.server = socketServer()
        self.server.statusMessage.connect(self.statusMessage)
        self.server.dataMessage.connect(self.dataMessage)
        self.server.start()


    def initGraph(self):
        # https://www.pythonguis.com/tutorials/pyqt6-plotting-pyqtgraph/
        self.graphWidget = pg.PlotWidget()
        # self.graphWidget.setFixedSize(640, 480)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle('Graph title')

        styles = {'color':'r', 'font-size':'10px'}
        self.graphWidget.setLabel('left', 'y-axis', **styles)
        self.graphWidget.setLabel('bottom', 'x-axis', **styles)
        self.graphWidget.addLegend()

        size = 100
        self.xAxis = np.arange(0, size+1, step=1)
        self.lineData = np.random.rand(size+1)

        self.dataLine = self.graphWidget.plot(self.xAxis, self.lineData, name='Line 1')
        
    def updatePlotData(self, data):
        self.xAxis = np.delete(self.xAxis, 0)  # Remove the first y element.
        self.xAxis = np.append(self.xAxis, self.xAxis[-1] + 1)  # Add a new value 1 higher than the last.

        self.lineData = np.delete(self.lineData, 0)  # Remove the first
        self.lineData = np.append(self.lineData, data)  # Add a new value.

        self.dataLine.setData(self.xAxis, self.lineData)  # Update the data.

    @Slot()
    def exit(self):
        print('Exiting...')
        self.server.running = False
        # Give time for the thread to finish
        self.server.wait()
        self.close()

    @Slot()
    def dataMessage(self, data):
        self.updatePlotData(data)

    @Slot()
    def statusMessage(self, data):
        self.serverDisplay.append(str(data))


if __name__ == "__main__":
    app = QApplication()
    w = MainWindow()
    w.show()
    sys.exit(app.exec())