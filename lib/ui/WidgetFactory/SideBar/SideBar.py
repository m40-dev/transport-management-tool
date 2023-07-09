
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QToolButton


class SideBar(QObject):
    buttonClicked = pyqtSignal(int)

    def __init__(self, application, target_layout):
        super().__init__()
        self.application = application
        self.layout = target_layout
        self.application.currentViewChanged.connect(self.currentViewChanged)

        PackageManagerButton = QToolButton()
        PackageManagerButton.setText("PM")
        PackageManagerButton.clicked.connect(lambda: self.buttonClicked.emit(0))

        TemplateEditorButton = QToolButton()
        TemplateEditorButton.setText("TE")
        TemplateEditorButton.clicked.connect(lambda: self.buttonClicked.emit(1))

        SettingsButton = QToolButton()
        SettingsButton.setText("S")
        SettingsButton.clicked.connect(lambda: self.buttonClicked.emit(2))

        PackageManagerButton.setProperty("ToolButton", "SideBar")
        TemplateEditorButton.setProperty("ToolButton", "SideBar")
        SettingsButton.setProperty("ToolButton", "SideBar")

        PackageManagerButton.setObjectName("PackageManagerButton")
        TemplateEditorButton.setObjectName("TemplateEditorButton")
        SettingsButton.setObjectName("SettingsButton")

        PackageManagerButton.setCheckable(True)
        TemplateEditorButton.setCheckable(True)
        SettingsButton.setCheckable(True)

        self.navigation_buttons = [PackageManagerButton, TemplateEditorButton, SettingsButton]
        self.layout.insertWidget(0, PackageManagerButton)
        self.layout.insertWidget(1, TemplateEditorButton)
        self.layout.insertStretch(2, 5)
        self.layout.insertWidget(3, SettingsButton)


    def currentViewChanged(self, index):
        # print("mark sidebar button", index)
        for button in self.navigation_buttons:
            if button.isChecked():
                button.setChecked(False)
        if index <= len(self.navigation_buttons):
            current_button = self.navigation_buttons[index]
            current_button.setChecked(True)
