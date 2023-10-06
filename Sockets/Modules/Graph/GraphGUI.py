
from Modules.Graph.CustomWidgets import DataWidget, GraphLayoutWidget
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QWidgetItem,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser, QDoubleSpinBox, QCheckBox)

from collections import namedtuple

class GraphGUI:
    def __init__(self):

        self.DataGroup = namedtuple('DataGroup', ['name', 'states'])
        
        # https://www.pythonguis.com/tutorials/pyqt6-plotting-pyqtgraph/
        self.graph = GraphLayoutWidget()
        self.graph.setBackground('w')
        self.graphWidgets = [] # List to store graphs
        self._generateSubplot() # Create an initial graph element
        self.graphDataControl = QVBoxLayout() # Layout for data groups

        # Autoscroll options
        self.autoscroll = True
        self.autoscrollRange = 10
        self.resetGraphButton = QPushButton('Reset graph')
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

    def _removeSubplot(self):
        if len(self.graphWidgets) == 1: return
        self.graphWidgets.pop().deleteLater()

    def _generateSubplot(self):
        graphWidget = self.graph.addPlot()
        # graphWidget.setFixedSize(640, 480)
        graphWidget.showGrid(x=True, y=True)
        graphWidget.setTitle('Graph title')

        styles = {'color':'r', 'font-size':'10px'}
        graphWidget.setLabel('left', 'y-axis', **styles)
        graphWidget.setLabel('bottom', 'x-axis', **styles)
        graphWidget.addLegend()
        graphWidget.hideButtons()
        graphWidget.disableAutoRange()
        graphWidget.setMouseEnabled(x=False, y=False)
        self.graphWidgets.append(graphWidget)

    def _resetGraphs(self):
        for graphWidget in self.graphWidgets: graphWidget.clear()

    def _setupControlDataWidgets(self, data: dict):
        for group, values in data.items():
            groupData = self.DataGroup(group, values.shape[1])
            groupWidget = self._addDataControlWidget(groupData)
            self.graphDataControl.addWidget(groupWidget)

    def _addDataControlWidget(self, group: namedtuple):
        widget = QWidget()
        groupLayout = QVBoxLayout()

        firstRow = QHBoxLayout()
        firstRow.addWidget(QLabel(group.name))

        secondRow = QHBoxLayout()
        for i in range(group.states):
            l = QVBoxLayout()
            dw = DataWidget(f'{group.name}_{i+1}')
            dw.setStyleSheet('border: 1px solid black')
            l.addWidget(dw)
            secondRow.addLayout(l)
        groupLayout.addLayout(firstRow)
        groupLayout.addLayout(secondRow)
        widget.setLayout(groupLayout)
        return widget
        