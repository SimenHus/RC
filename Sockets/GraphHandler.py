import numpy as np

import pyqtgraph as pg
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser, QDoubleSpinBox, QCheckBox)

class GraphHandler:
    def __init__(self):
        self.initGraph()
        self.graphSettings = QGroupBox("Graph settings")
        self.graphSettings.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Settings layout
        graphSettingsLayout = QVBoxLayout()

        # Define sub-settings and layouts

        # Autoscroll options
        toggleAutoscroll = QPushButton('Toggle autoscroll')
        toggleAutoscroll.clicked.connect(self.toggleAutoscroll)
        autoscrollRange = QSpinBox()
        autoscrollRange.setValue(self.autoscrollRange)
        autoscrollRange.setMinimum(1)
        autoscrollRange.valueChanged.connect(self.setAutoscrollRange)

        # Manual control options
        lims = (-1000, 1000)
        self.manualXRangeMin = QDoubleSpinBox()
        self.manualXRangeMin.setMinimum(lims[0])
        self.manualXRangeMin.setMaximum(lims[1])
        self.manualXRangeMax = QDoubleSpinBox()
        self.manualXRangeMax.setMinimum(lims[0])
        self.manualXRangeMax.setMaximum(lims[1])

        self.manualYRangeMin = QDoubleSpinBox()
        self.manualYRangeMin.setMinimum(lims[0])
        self.manualYRangeMin.setMaximum(lims[1])
        self.manualYRangeMax = QDoubleSpinBox()
        self.manualYRangeMax.setMinimum(lims[0])
        self.manualYRangeMax.setMaximum(lims[1])

        autoscrollRange.setMaximum(lims[1])

        # Button to set manual range to graph
        self.setManRange = QPushButton('Set manual range')
        self.setManRange.clicked.connect(self.setManualRange)
        self.setManRange.setEnabled(False)

        manualAutoscrollLayout = QHBoxLayout()
        rangesMin = QVBoxLayout()
        rangesMin.addWidget(QLabel('Manual range y min:'), 20)
        rangesMin.addWidget(self.manualYRangeMin, 20)
        rangesMin.addWidget(QLabel('Manual range x min:'), 20)
        rangesMin.addWidget(self.manualXRangeMin, 20)

        rangesMax = QVBoxLayout()
        rangesMax.addWidget(QLabel('Manual range y max:'), 20)
        rangesMax.addWidget(self.manualYRangeMax, 20)
        rangesMax.addWidget(QLabel('Manual range x max:'), 20)
        rangesMax.addWidget(self.manualXRangeMax, 20)

        toggles = QVBoxLayout()
        toggles.addWidget(QLabel(), 20)
        toggles.addWidget(self.setManRange, 20)
        toggles.addWidget(QLabel(), 20)
        toggles.addWidget(toggleAutoscroll, 20)

        autoscrollRangeLayout = QVBoxLayout()
        autoscrollRangeLayout.addWidget(QLabel(), 20)
        autoscrollRangeLayout.addWidget(QLabel(), 20)
        autoscrollRangeLayout.addWidget(QLabel('Autoscroll x-axis range:'), 20)
        autoscrollRangeLayout.addWidget(autoscrollRange, 20)

        manualAutoscrollLayout.addLayout(rangesMin)
        manualAutoscrollLayout.addLayout(rangesMax)
        manualAutoscrollLayout.addLayout(toggles)
        manualAutoscrollLayout.addLayout(autoscrollRangeLayout)

        # Layout for show/hide graph elements
        self.showHideBox = QGroupBox('Show/Hide states')
        self.showHideBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Set sub-layouts
        graphSettingsLayout.addLayout(manualAutoscrollLayout)
        graphSettingsLayout.addWidget(self.showHideBox)
        self.graphSettings.setLayout(graphSettingsLayout)

        # Set main layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.graphWidget, 80)
        self.layout.addWidget(self.graphSettings, 20)

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
        self.graphWidget.hideButtons()
        self.graphWidget.disableAutoRange()
        self.graphWidget.setMouseEnabled(x=False, y=False)
        self.autoscroll = True
        self.autoscrollRange = 10

        # Variables to store graph data
        self.xAxis = np.array([0]) # Same xAxis for all states
        self.yAxis = {} # Dict with variable name : yAxis
        self.graphElements = {} # Dict to store graph elements as state: element


    @Slot()
    def clientConnected(self, states):
        # Function to initialize variables from client data
        if len(self.yAxis) > 0: return # If client is already initialized, return
        names = []
        for state in states:
            name = state['Name'] # Variable name
            names.append(name)
            self.yAxis[name] = state['x0'] # Define initial state for variable
            # Graph the initiale state of the variable and store the plot element
            self.graphElements[name] = self.graphWidget.plot(self.xAxis, self.yAxis[name], connect='finite', name=name)
        self.setupShowHideSection(names)

    def setupShowHideSection(self, states):
        vLayout = QVBoxLayout()

        self.showHideAll = True
        toggleAllButton = QPushButton('Toggle all')
        toggleAllButton.clicked.connect(self.showHideToggleAll)


        statesPerRow = 8 # States per row before linechange
        for i in range((len(states)-1)//statesPerRow+1): # If more than statesPerRow states, repeat for-loop
            row = QHBoxLayout()
            for state in states[statesPerRow*i:statesPerRow*(1+i)]:
                stateBox = QCheckBox()
                stateBox.setChecked(True)
                stateBox.stateChanged.connect(lambda val, name=state: self.showHideStatePressed(name, val))
                
                itemLayout = QVBoxLayout()
                itemLayout.addWidget(QLabel(f'{state}:'), 40)
                itemLayout.addWidget(stateBox, 40)

                row.addLayout(itemLayout)
            vLayout.addLayout(row)
        vLayout.addWidget(toggleAllButton)
        self.showHideBox.setLayout(vLayout)

    @Slot()
    def showHideToggleAll(self):
        self.showHideAll = not self.showHideAll
        for box in self.showHideBox.findChildren(QCheckBox): box.setChecked(self.showHideAll)

    @Slot()
    def showHideStatePressed(self, state, checked):
        elem = self.graphElements[state]
        if checked: self.graphWidget.addItem(elem)
        else: self.graphWidget.removeItem(elem)


    @Slot()
    def setManualRange(self):
        # Collect and set manual ranges
        xmin = self.manualXRangeMin.value()
        xmax = self.manualXRangeMax.value()
        ymin = self.manualYRangeMin.value()
        ymax = self.manualYRangeMax.value()
        self.graphWidget.setRange(xRange=(xmin,xmax), yRange=(ymin,ymax))
    
    @Slot()
    def toggleAutoscroll(self):
        self.graphWidget.setMouseEnabled(x=self.autoscroll, y=self.autoscroll) # Enable/disable mouse movement
        self.setManRange.setEnabled(self.autoscroll) # Enable/Disable manual range button
        self.autoscroll = not self.autoscroll # Toggle autoscrolling functionality
    
    @Slot()
    def setAutoscrollRange(self, range):
        self.autoscrollRange = range # Set the autoscroll range

    @Slot()
    def dataMessage(self, data):
        if len(self.yAxis) < 1: return # If states have not been initialized, do nothing
        self.xAxis = np.append(self.xAxis, self.xAxis[-1] + 1)  # Add a new value 1 higher than the last.
        for state in data: # Update states with new measurements
            self.yAxis[state['Name']] = np.append(self.yAxis[state['Name']], state['Measurement'])
        self.updateGraph() # Update graph

        
    def updateGraph(self):
        for name, elem in self.graphElements.items():
            elem.setData(self.xAxis, self.yAxis[name]) # Update graph elements
        if self.autoscroll:
            xRange = (self.xAxis[-1]-self.autoscrollRange, self.xAxis[-1]) # Define the x-axis range
            yRange = self.graphWidget.getViewBox().childrenBounds()[1] # Get graph elements [min, max] y-values
            self.graphWidget.setRange(xRange=xRange, yRange=yRange)

