from pyqtgraph import PlotItem, GraphicsLayoutWidget, PlotDataItem
from PySide6.QtCore import Qt, QMimeData, Signal
from PySide6.QtGui import QDrag, QDragEnterEvent, QDropEvent, QMouseEvent, QDragMoveEvent
from PySide6.QtWidgets import QLabel



class DataWidget(QLabel):

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() != Qt.LeftButton: return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.text())
        drag.setMimeData(mime)
        drag.exec_(Qt.MoveAction)


class CustomPlotItem(PlotItem):
    color = 0
    def paint(self, painter, *args) -> None:
        PlotItem.paint(self, painter, *args)


    def plot(self, *args, **kwargs) -> PlotDataItem:
        """
        Calls PlotItem.plot() with color control
        """
        self.color += 1
        return super().plot(*args, pen=self.color, **kwargs)



class CustomGraphicsLayoutWidget(GraphicsLayoutWidget):
    dropSignal = Signal(CustomPlotItem, str)
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.accept()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        event.accept()

        for child in self.findChildren(PlotItem):
            childX = child.pos()[0]
            pos = event.pos()
            if not (childX <= pos.x() <= childX + child.boundingRect().width()): continue
            self.dropSignal.emit(child, event.mimeData().text())