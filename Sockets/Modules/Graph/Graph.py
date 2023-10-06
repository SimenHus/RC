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
        self._resetGraphs()

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

        if len(data) > self.graphDataControl.count(): self._setupControlDataWidgets(data)

        def updateXAxis(): # Function to update x axis
            steps = data[list(data.keys())[0]].shape[0] # Find how much data has been sent
            currentX = self.xAxis[-1]
            self.xAxis = np.hstack((self.xAxis, np.arange(currentX+1, currentX+steps+1, 1))) # Expand xAxis with new amount of data
            xAxisUpdated = True

        xAxisUpdated = False # Wait to update x axis until at least one graph is using data
        for graphWidget in self.graphWidgets: # Loop through all graphs
            for graphElement in graphWidget.listDataItems(): # Loop through all items in graph
                if not xAxisUpdated: updateXAxis()
                    
                name, id = graphElement.name()[:-2], int(graphElement.name()[-1:])
                newY = np.hstack((graphElement.getData()[1], data[name][:, id])) # Update states with new measurements
                graphElement.setData(self.xAxis, newY) # Update graph elements

                if not self.autoscroll: continue # If autoscrolling is active, update graph range
                xRange = (self.xAxis[-1]-self.autoscrollRange, self.xAxis[-1]) # Define the x-axis range
                yRange = graphWidget.getViewBox().childrenBounds()[1] # Get graph elements [min, max] y-values
                graphWidget.setRange(xRange=xRange, yRange=yRange)

    @Slot()
    def addStateToGraph(self, graph, state):
        color = 0 # To be improved
        graph.plot(self.xAxis, np.ones(len(self.xAxis))*np.inf, pen=color, connect='finite', name=state)