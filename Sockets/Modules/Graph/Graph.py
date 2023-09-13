import numpy as np

from PySide6.QtCore import Slot

from Modules.Graph.GraphGUI import GraphGUI

class GraphHandler(GraphGUI):
    def __init__(self):
        super().__init__()

        # Connect button signals to slots
        self.toggleAutoscrollButton.clicked.connect(self.toggleAutoscroll)
        self.autoscrollRangeSpinbox.valueChanged.connect(self.setAutoscrollRange)
        self.setManRangeButton.clicked.connect(self.setManualRange)
        self.resetGraphButton.clicked.connect(self.resetGraph)

        # Variables to store graph data
        self.xAxis = np.array([0]) # Same xAxis for all states
        self.yAxis = {} # Dict with variable name : yAxis
        self.graphElements = {} # Dict to store graph elements as state: element


    @Slot()
    def resetGraph(self):
        # Variables to store graph data
        self.xAxis = np.array([0]) # Same xAxis for all states
        self.yAxis = {} # Dict with variable name : yAxis
        self.graphElements = {} # Dict to store graph elements as state: element
        self._resetGraph()

    @Slot()
    def showHideToggleAll(self):
        self.showHideAll = not self.showHideAll
        self._showHideToggleAll()

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
        self.setManRangeButton.setEnabled(self.autoscroll) # Enable/Disable manual range button
        self.autoscroll = not self.autoscroll # Toggle autoscrolling functionality
    
    @Slot()
    def setAutoscrollRange(self, range):
        self.autoscrollRange = range # Set the autoscroll range

    @Slot()
    def dataMessage(self, msg):
        data = msg['Data']
        # Sort message category
        if msg['MessageType'] == 'Init': self.initStates(data) # Initialize
        elif msg['MessageType'] == 'Data': self.updateGraph(data) # Update graph

        
    def updateGraph(self, data):
        if len(self.yAxis) < 1: return # If states have not been initialized, do nothing
        self.xAxis = np.append(self.xAxis, self.xAxis[-1] + 1)  # Add a new value 1 higher than the last.

        for state in data: # Update states with new measurements
            self.yAxis[state['Name']] = np.append(self.yAxis[state['Name']], state['Measurement'])

        for name, elem in self.graphElements.items():
            elem.setData(self.xAxis, self.yAxis[name]) # Update graph elements
            
        if self.autoscroll: # If autoscrolling is active, update graph range
            xRange = (self.xAxis[-1]-self.autoscrollRange, self.xAxis[-1]) # Define the x-axis range
            yRange = self.graphWidget.getViewBox().childrenBounds()[1] # Get graph elements [min, max] y-values
            self.graphWidget.setRange(xRange=xRange, yRange=yRange)

    def initStates(self, states):
        if len(self.yAxis) > 0: return # If already initialized, return
        # Function to initialize variables from client data
        names = []
        for state in states:
            name = state['Name'] # Variable name
            names.append(name)
            self.yAxis[name] = state['x0'] # Define initial state for variable
            # Graph the initiale state of the variable and store the plot element
            self.graphElements[name] = self.graphWidget.plot(self.xAxis, self.yAxis[name], connect='finite', name=name)
        
        self.showHideAll = True
        self._setupShowHideSection(names)
        self.toggleAllButton.clicked.connect(self.showHideToggleAll)