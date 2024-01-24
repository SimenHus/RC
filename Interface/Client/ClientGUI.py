from PySide6.QtWidgets import QGroupBox, QSizePolicy, QVBoxLayout, QTextBrowser

class ClientGUI:
    def __init__(self):
        # Interface box for client settings
        self.clientSettings = QGroupBox('Client settings')
        self.clientSettings.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.clientDisplay = QTextBrowser()
        
        clientSettingsLayout = QVBoxLayout()
        self.clientSettings.setLayout(clientSettingsLayout)

        # Set client interface layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.clientDisplay, 80)
        self.layout.addWidget(self.clientSettings, 20)
