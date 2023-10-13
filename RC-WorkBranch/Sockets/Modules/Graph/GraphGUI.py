
from Modules.Graph.CustomWidgets import DataWidget, CustomGraphicsLayoutWidget, CustomPlotItem, ControlButtonWidget
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox, QWidgetItem,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser, QDoubleSpinBox, QCheckBox)

from collections import namedtuple

class GraphGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.DataGroup = namedtuple('DataGroup', ['name', 'states'])
        
        # https://www.pythonguis.com/tutorials/pyqt6-plotting-pyqtgraph/
        self.graph = CustomGraphicsLayoutWidget()
        self.graph.setBackground('w')
        self.graphWidgets = [] # List to store graphs
        self.rightPanel = QVBoxLayout() # Right panel layout
        self.graphDataControl = QVBoxLayout() # Layout for data groups
        self.controlPanel = QVBoxLayout() # Layout for control panel
        self._generateSubplot() # Create an initial graph element
        self._setupControlPanel() # Setup control panel

        # Autoscroll options
        self.autoscroll = True
        self.autoscrollRange = 10
        self.resetGraphButton = QPushButton('Reset graphs')
        self.toggleAutoscrollButton = QPushButton('Toggle autoscroll')
        self.autoscrollRangeSpinbox = QSpinBox()
        self.autoscrollRangeSpinbox.setValue(self.autoscrollRange)
        self.autoscrollRangeSpinbox.setMinimum(1)
        self.autoscrollRangeSpinbox.setMaximum(10000)

        self.resetGraphButton.setToolTip('Remove all states from all graphs and reset x-axis')
        self.toggleAutoscrollButton.setToolTip('Toggle if x-axis should autoscroll or not')
        self.autoscrollRangeSpinbox.setToolTip('Set range for x-axis if autoscrolling')

        autoscrollLayout = QHBoxLayout()

        autoscrollLayout.addWidget(self.toggleAutoscrollButton)
        autoscrollLayout.addWidget(self.autoscrollRangeSpinbox)
        autoscrollLayout.addWidget(self.resetGraphButton)

        self.graphLayout = QVBoxLayout()
        self.graphLayout.addWidget(self.graph)
        self.graphLayout.addLayout(autoscrollLayout)

        # Set main layout
        self.rightPanel.addLayout(self.graphDataControl, 60)
        self.rightPanel.addLayout(self.controlPanel, 40)
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.graphLayout, 80)
        self.layout.addLayout(self.rightPanel, 20)


    def _setupControlPanel(self) -> None:
        firstRow = QHBoxLayout()
        secondRow = QHBoxLayout()
        CCR = ControlButtonWidget()
        CR = ControlButtonWidget()
        UpArrow = ControlButtonWidget('U')
        LeftArrow = ControlButtonWidget('L')
        DownArrow = ControlButtonWidget('D')
        RightArrow = ControlButtonWidget('R')
        CCR.setToolTip('Counter-clockwise rotation speed')
        CR.setToolTip('Clockwise rotation speed')

        firstRow.addWidget(CCR)
        firstRow.addWidget(UpArrow)
        firstRow.addWidget(CR)
        secondRow.addWidget(LeftArrow)
        secondRow.addWidget(DownArrow)
        secondRow.addWidget(RightArrow)
        self.controlPanel.addLayout(firstRow)
        self.controlPanel.addLayout(secondRow)




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
        