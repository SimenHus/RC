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
        self.graph.dropSignal.connect(self.addStateToGraph)

        # Variables to store graph data
        self.xAxis = np.array([0]) # Same xAxis for all states

    @Slot()
    def addGraph(self) -> None:
        self._generateSubplot()

    @Slot()
    def removeGraph(self) -> None:
        self._removeSubplot()

    @Slot()
    def resetGraphs(self) -> None:
        # Variables to store graph data
        self.xAxis = np.array([0]) # Same xAxis for all states
        self._resetGraphs()

    @Slot()
    def toggleAutoscroll(self) -> None:
        """
        Toggles autoscrolling on all graphs
        """
        for graphWidget in self.graphWidgets:
            graphWidget.setMouseEnabled(x=self.autoscroll, y=self.autoscroll) # Enable/disable mouse movement
        self.autoscroll = not self.autoscroll # Toggle autoscrolling functionality
    
    @Slot()
    def setAutoscrollRange(self, range: int) -> None:
        """
        range: int - x-axis range when autoscrolling
        """
        self.autoscrollRange = range # Set the autoscroll range

    @Slot()
    def dataMessage(self, data: dict) -> None:

        if len(data) > self.graphDataControl.count(): self._setupDataWidgetGroup(data)

        steps = data[list(data.keys())[0]].shape[0] # Find how much data has been sent
        currentX = self.xAxis[-1]
        self.xAxis = np.hstack((self.xAxis, np.arange(currentX+1, currentX+steps+1, 1))) # Expand xAxis with new amount of data

        itemsPresent = False # Revert x axis if no items are present
        for graphWidget in self.graphWidgets: # Loop through all graphs
            for graphElement in graphWidget.listDataItems(): # Loop through all items in graph
                itemsPresent = True
                    
                name, id = graphElement.name()[:-2], int(graphElement.name()[-1:])-1
                newY = np.hstack((graphElement.getData()[1], data[name][:, id])) # Update states with new measurements
                graphElement.setData(self.xAxis, newY) # Update graph elements

                if not self.autoscroll: continue # If autoscrolling is active, update graph range
                xRange = (self.xAxis[-1]-self.autoscrollRange, self.xAxis[-1]) # Define the x-axis range
                yRange = graphWidget.getViewBox().childrenBounds()[1] # Get graph elements [min, max] y-values
                graphWidget.setRange(xRange=xRange, yRange=yRange)
        
        if not itemsPresent:
            self.xAxis = np.array([0])

    @Slot()
    def addStateToGraph(self, graphWidget, state: str) -> None:
        for line in graphWidget.listDataItems():
            if line.name() == state: return # If state already drawn on graph, return
        graphWidget.plot(self.xAxis, np.ones(len(self.xAxis))*np.inf, connect='finite', name=state)