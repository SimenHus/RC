from pyqtgraph import GraphicsLayoutWidget
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag, QDragEnterEvent, QDropEvent, QMouseEvent, QDragMoveEvent
from PySide6.QtWidgets import QLabel



class DataWidget(QLabel):

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() != Qt.LeftButton: return
        drag = QDrag(self)
        mime = QMimeData()
        drag.setMimeData(mime)
        drag.exec_(Qt.MoveAction)


class GraphLayoutWidget(GraphicsLayoutWidget):
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.accept()
        print('Graph accepted')

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        event.accept()

    def dropEvent(self, event: QDropEvent) -> None:
        event.accept()
        widgetAt = qApp.widgetAt(event.pos)
        print('Graph dropped')