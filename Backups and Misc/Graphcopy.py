import numpy as np

from PySide6.QtCore import Slot

from Modules.Graph.GraphGUI import GraphGUI

class GraphHandler(GraphGUI):
    def __init__(self):
        super().__init__()

        # Connect button signals to slots
        self.toggleAutoscrollButton.clicked.connect(self.toggleAutoscroll)
        self.autoscrollRangeSpinbox.valueChanged.connect(self.setAutoscrollRange)
        self.resetGraphButton.clicked.connect(self.resetGraphs)

        # Variables to store graph data
        self.xAxis = np.array([0]) # Same xAxis for all states
        self.graphElements = {} # Dict to store graph elements as state: element

    @Slot()
    def addGraph(self):
        self._generateSubplot()

    @Slot()
    def removeGraph(self):
        self._removeSubplot()

    @Slot()
    def resetGraphs(self):
        # Variables to store graph data
        self.xAxis = np.array([0]) # Same xAxis for all states
        self.graphElements = {} # Dict to store graph elements as state: element
        self._resetGraphs()

    @Slot()
    def showHideToggleGroup(self, group: str):
        self.showHideGroup[group] = not self.showHideGroup[group]
        self._showHideToggleGroup(group)

    @Slot()
    def showHideStatePressed(self, state: str, index: int, checked: bool):
        elem = self.graphElements[state][index]
        if checked: self.graphWidget.addItem(elem)
        else: self.graphWidget.removeItem(elem)
    
    @Slot()
    def toggleAutoscroll(self):
        for graphWidget in self.graphWidgets:
            graphWidget.setMouseEnabled(x=self.autoscroll, y=self.autoscroll) # Enable/disable mouse movement
        self.autoscroll = not self.autoscroll # Toggle autoscrolling functionality
    
    @Slot()
    def setAutoscrollRange(self, range: int):
        self.autoscrollRange = range # Set the autoscroll range

    @Slot()
    def dataMessage(self, data: dict):

        if len(self.graphElements) < len(data): self.initStates(data) # If any states have not been initialized, initialize

        steps = data[list(data.keys())[0]].shape[0]
        currentX = self.xAxis[-1]
        self.xAxis = np.hstack((self.xAxis, np.arange(currentX+1, currentX+steps+1, 1)))

        for group, items in self.graphElements.items():
            for i, elem in enumerate(items):
                print(elem.params)
                newData =  np.hstack((elem.getData()[1], data[group][:, i])) # Update states with new measurements
                elem.setData(self.xAxis, newData) # Update graph elements
            
        if self.autoscroll: # If autoscrolling is active, update graph range
            for graphWidget in self.graphWidgets:
                xRange = (self.xAxis[-1]-self.autoscrollRange, self.xAxis[-1]) # Define the x-axis range
                yRange = graphWidget.getViewBox().childrenBounds()[1] # Get graph elements [min, max] y-values
                graphWidget.setRange(xRange=xRange, yRange=yRange)

    def initStates(self, states: dict):
        # Function to initialize variables from client data
        stateHierarchy = {}
        self.showHideGroup = {}
        color = 0
        for state, value in states.items():
            stateHierarchy[state] = [f'{state}_{i+1}' for i in range(value.shape[1])] # Add names to hierarchy for the state toggle buttons
            self.showHideGroup[state] = True
            # Graph the initial state of the variable and store the plot element
            newGraphElements = []
            for i in range(value.shape[1]):
                newGraphElements.append(self.graphWidgets[0].plot(self.xAxis, np.ones(len(self.xAxis))*np.inf, pen=color, connect='finite', name=f'{state}_{i+1}'))
                color += 1
            self.graphElements[state] = newGraphElements
        
        # self.showHideAll = True
        # self._setupShowHideSection(stateHierarchy)
        # self.toggleAllButton.clicked.connect(self.showHideToggleAll)