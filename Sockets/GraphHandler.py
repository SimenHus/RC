import numpy as np

import pyqtgraph as pg
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser)

class GraphHandler:

    def __init__(self):
        self.initGraph()
        self.graphSettings = QGroupBox("Graph settings")
        self.graphSettings.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.graphSettingsXAxisFormat = QComboBox()
        self.graphSettingsXAxisFormat.addItems(['Elapsed time', 'Real time'])
        self.graphSettingsXAxisFormat.currentIndexChanged.connect(self.XAxisIndexChanged)

        graphSettingsLayout = QHBoxLayout()
        graphSettingsLayout.addWidget(QLabel('x-Axis format:'), 60)
        graphSettingsLayout.addWidget(self.graphSettingsXAxisFormat, 40)
        self.graphSettings.setLayout(graphSettingsLayout)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.graphWidget)
        self.layout.addWidget(self.graphSettings)

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

    def XAxisIndexChanged(self, idx):
        pass

    def updatePlotData(self, data):
        self.xAxis = np.delete(self.xAxis, 0)  # Remove the first y element.
        self.xAxis = np.append(self.xAxis, self.xAxis[-1] + 1)  # Add a new value 1 higher than the last.

        self.lineData = np.delete(self.lineData, 0)  # Remove the first
        self.lineData = np.append(self.lineData, data)  # Add a new value.

        self.dataLine.setData(self.xAxis, self.lineData)  # Update the data.

