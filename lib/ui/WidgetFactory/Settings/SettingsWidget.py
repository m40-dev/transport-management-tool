
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel


class SettingsWidget(QWidget):

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        self.setObjectName("SettingsWidget")

        wip_label = QLabel("Coming Soon...")

        self.layout.addWidget(wip_label, 0, 0, -1, -1)

