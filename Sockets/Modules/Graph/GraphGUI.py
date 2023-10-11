
from Modules.Graph.CustomWidgets import DataWidget, CustomGraphicsLayoutWidget, CustomPlotItem
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QWidgetItem,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser, QDoubleSpinBox, QCheckBox)

from collections import namedtuple

class GraphGUI:
    def __init__(self):

        self.DataGroup = namedtuple('DataGroup', ['name', 'states'])
        
        # https://www.pythonguis.com/tutorials/pyqt6-plotting-pyqtgraph/
        self.graph = CustomGraphicsLayoutWidget()
        self.graph.setBackground('w')
        self.graphWidgets = [] # List to store graphs
        self._generateSubplot() # Create an initial graph element
        self.graphDataControl = QVBoxLayout() # Layout for data groups

        # Autoscroll options
        self.autoscroll = True
        self.autoscrollRange = 10
        self.resetGraphButton = QPushButton('Reset graphs')
        self.toggleAutoscrollButton = QPushButton('Toggle autoscroll')
        self.autoscrollRangeSpinbox = QSpinBox()
        self.autoscrollRangeSpinbox.setValue(self.autoscrollRange)
        self.autoscrollRangeSpinbox.setMinimum(1)
        self.autoscrollRangeSpinbox.setMaximum(10000)

        autoscrollLayout = QHBoxLayout()

        autoscrollLayout.addWidget(self.toggleAutoscrollButton)
        autoscrollLayout.addWidget(self.autoscrollRangeSpinbox)
        autoscrollLayout.addWidget(self.resetGraphButton)

        self.graphLayout = QVBoxLayout()
        self.graphLayout.addWidget(self.graph)
        self.graphLayout.addLayout(autoscrollLayout)

        # Set main layout
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.graphLayout, 80)
        self.layout.addLayout(self.graphDataControl, 20)

    def _removeSubplot(self) -> None:
        """
        Function to remove last subplot
        """
        if len(self.graphWidgets) == 1: return
        self.graphWidgets.pop().deleteLater()

    def _generateSubplot(self) -> None:
        """
        Function to generate a subplot
        """
        graphWidget = CustomPlotItem()
        graphWidget.setParent(self.graph)
        graphWidget.showGrid(x=True, y=True)
        graphWidget.setTitle('Graph title')

        styles = {'color':'r', 'font-size':'10px'}
        graphWidget.setLabel('left', 'y-axis', **styles)
        graphWidget.setLabel('bottom', 'x-axis', **styles)
        graphWidget.addLegend()
        graphWidget.hideButtons()
        graphWidget.disableAutoRange()
        graphWidget.setMouseEnabled(x=False, y=False)
        self.graph.addItem(graphWidget)
        self.graphWidgets.append(graphWidget)

    def _resetGraphs(self) -> None:
        """
        Clears all graphs of their content
        """
        for graphWidget in self.graphWidgets: graphWidget.clear()

    def _setupDataWidgetGroup(self, data: dict) -> None:
        """
        Takes in a dataset dict with state: values,
        and creates a widget with dragable statenames
        """
        for group, values in data.items():
            groupData: namedtuple = self.DataGroup(group, values.shape[1])
            groupWidget: QWidget = self._createDataWidget(groupData)
            self.graphDataControl.addWidget(groupWidget)

    def _createDataWidget(self, group: namedtuple) -> QWidget:
        """
        Takes in a namedtuple with statename and number of states.
        Returns a widget with dragable states
        """
        widget = QWidget()
        layout = QHBoxLayout()
        for i in range(group.states):
            dw = DataWidget(f'{group.name}_{i+1}')
            dw.setObjectName('DataWidget')
            layout.addWidget(dw)
        widget.setLayout(layout)
        return widget
        