import pyqtgraph as pg
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QSpinBox,
                               QTextBrowser, QDoubleSpinBox, QCheckBox)

class GraphGUI:
    def __init__(self):

        # -------------Graph related------------------
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
        self.graphSettings = QGroupBox("Graph settings")
        self.graphSettings.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # -------------Settings related--------------
        # Settings layout
        self.graphSettingsLayout = QVBoxLayout()

        # Define sub-settings and layouts

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

        # Autoscroll options
        self.autoscroll = True
        self.autoscrollRange = 10
        self.toggleAutoscrollButton = QPushButton('Toggle autoscroll')
        self.autoscrollRangeSpinbox = QSpinBox()
        self.autoscrollRangeSpinbox.setValue(self.autoscrollRange)
        self.autoscrollRangeSpinbox.setMinimum(1)
        self.autoscrollRangeSpinbox.setMaximum(lims[1])

        # Button to set manual range to graph
        self.setManRangeButton = QPushButton('Set manual range')
        self.setManRangeButton.setEnabled(False)

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
        toggles.addWidget(self.setManRangeButton, 20)
        toggles.addWidget(QLabel(), 20)
        toggles.addWidget(self.toggleAutoscrollButton, 20)

        self.resetGraphButton = QPushButton('Reset graph')

        autoscrollRangeLayout = QVBoxLayout()
        autoscrollRangeLayout.addWidget(QLabel(), 20)
        autoscrollRangeLayout.addWidget(self.resetGraphButton, 20)
        autoscrollRangeLayout.addWidget(QLabel('Autoscroll x-axis range:'), 20)
        autoscrollRangeLayout.addWidget(self.autoscrollRangeSpinbox, 20)

        manualAutoscrollLayout.addLayout(rangesMin)
        manualAutoscrollLayout.addLayout(rangesMax)
        manualAutoscrollLayout.addLayout(toggles)
        manualAutoscrollLayout.addLayout(autoscrollRangeLayout)

        # Layout for show/hide graph elements
        self.showHideBox = QGroupBox('Show/Hide states')
        self.showHideBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Set sub-layouts
        self.graphSettingsLayout.addLayout(manualAutoscrollLayout)
        self.graphSettingsLayout.addWidget(self.showHideBox)
        self.graphSettings.setLayout(self.graphSettingsLayout)

        # Set main layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.graphWidget, 80)
        self.layout.addWidget(self.graphSettings, 20)


    def _setupShowHideSection(self, states):
        vLayout = QVBoxLayout()

        self.toggleAllButton = QPushButton('Toggle all')

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
        vLayout.addWidget(self.toggleAllButton)
        self.showHideBox.setLayout(vLayout)

    def _resetGraph(self):
        self.graphSettingsLayout.removeWidget(self.showHideBox)
        self.graphWidget.clear()
        self.showHideBox.deleteLater()
        self.showHideBox = QGroupBox('Show/Hide states')
        self.showHideBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.graphSettingsLayout.addWidget(self.showHideBox)

    def _showHideToggleAll(self):
        for box in self.showHideBox.findChildren(QCheckBox): box.setChecked(self.showHideAll)