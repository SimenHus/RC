
import sys

# from SensorFusion import Filter
from Interface import Client

from Communication import SocketClient


from PySide6.QtWidgets import QApplication

## System flow:
# Real system -> Interface/read sensor -> Sensor fusion -> SA -> ControlSystem -> Real system ...


if __name__ == "__main__":
    app = QApplication()
    w = Client(SocketClient)
    w.show()

    with open('C:\\Users\\shustad\\Desktop\\Prog\\RC\\Interface\\Client\\styleVariables.txt', 'r') as f: varList = f.readlines()
    with open('C:\\Users\\shustad\\Desktop\\Prog\\RC\\Interface\\Client\\style.qss', 'r') as f: styleSheet = f.read()
    for var in varList:
        name, value = var.split('=')
        styleSheet = styleSheet.replace(name, value)
    app.setStyleSheet(styleSheet)
    sys.exit(app.exec())