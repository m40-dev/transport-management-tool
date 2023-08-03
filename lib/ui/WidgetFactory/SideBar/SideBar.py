
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtWidgets import QToolButton, QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon


class SideBar(QWidget):
    buttonClicked = pyqtSignal(int)

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        self.setObjectName("SideBar")
        self.application.currentViewChanged.connect(self.currentViewChanged)

        PackageManagerButton = QToolButton()
        

        # PackageManagerButton.setText("PM")
        PackageManagerButton.clicked.connect(lambda: self.buttonClicked.emit(0))
        PM_icon = QIcon("./lib/ui/img/icons/PackageManager.png")
        PackageManagerButton.setIcon(PM_icon)
        PackageManagerButton.setIconSize(QSize(round(PackageManagerButton.width()*0.7), round(PackageManagerButton.height()*0.7)))

        TemplateEditorButton = QToolButton()
        # TemplateEditorButton.setText("TE")
        TE_icon = QIcon("./lib/ui/img/icons/XMLTemplateEditor.png")
        TemplateEditorButton.setIcon(TE_icon)
        TemplateEditorButton.setIconSize(QSize(round(TemplateEditorButton.width()*0.7), round(TemplateEditorButton.height()*0.7)))
        TemplateEditorButton.clicked.connect(lambda: self.buttonClicked.emit(1))

        SettingsButton = QToolButton()
        # SettingsButton.setText("S")
        Settings_icon = QIcon("./lib/ui/img/icons/Settings.png")
        SettingsButton.setIcon(Settings_icon)
        SettingsButton.setIconSize(QSize(round(SettingsButton.width()*0.7), round(SettingsButton.height()*0.7)))
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
