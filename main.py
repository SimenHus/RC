
import sys

# from SensorFusion import Filter
from Interface import Client


from PySide6.QtWidgets import QApplication

## System flow:
# Real system -> Interface/read sensor -> Sensor fusion -> SA -> ControlSystem -> Real system ...



if __name__ == "__main__":
    app = QApplication()
    w = Client()
    w.show()

    with open(f'{w.path}\\styleVariables.txt', 'r') as f: varList = f.readlines()
    with open(f'{w.path}\\style.qss', 'r') as f: styleSheet = f.read()
    for var in varList:
        name, value = var.split('=')
        styleSheet = styleSheet.replace(name, value)
    app.setStyleSheet(styleSheet)
    sys.exit(app.exec())