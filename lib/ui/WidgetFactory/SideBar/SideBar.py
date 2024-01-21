
from PyQt6.QtCore import pyqtSignal, QSize, QEasingCurve, QPropertyAnimation, QAbstractAnimation
from PyQt6.QtWidgets import QToolButton, QWidget, QVBoxLayout, QGraphicsOpacityEffect, QFrame


class SideBar(QFrame):
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
        # PM_icon = self.application.ProgramConfiguration.getIcon("PackageManager")
        # PackageManagerButton.setIcon(PM_icon)
        # PackageManagerButton.setIconSize(QSize(round(PackageManagerButton.width()*0.7), round(PackageManagerButton.height()*0.7)))

        TemplateEditorButton = QToolButton()
        # TemplateEditorButton.setText("TE")
        # TE_icon = self.application.ProgramConfiguration.getIcon("XMLTemplateEditor")

        # TemplateEditorButton.setIcon(TE_icon)
        # TemplateEditorButton.setIconSize(QSize(round(TemplateEditorButton.width()*0.7), round(TemplateEditorButton.height()*0.7)))
        TemplateEditorButton.clicked.connect(lambda: self.buttonClicked.emit(1))

        SettingsButton = QToolButton()
        # SettingsButton.setText("S")
        # Settings_icon = self.application.ProgramConfiguration.getIcon("Settings")

        # SettingsButton.setIcon(Settings_icon)
        # SettingsButton.setIconSize(QSize(round(SettingsButton.width()*0.7), round(SettingsButton.height()*0.7)))
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

        self.animate()
        
    def animate(self, reverse=False):
        # animate startup
        target = self.application.ui.MainTabWidget.currentWidget()

        effect = QGraphicsOpacityEffect(target)
        target.setGraphicsEffect(effect)

        animation = QPropertyAnimation(target)

        animation.setPropertyName(bytes("opacity", "utf-8"))
        animation.setTargetObject(effect)
        animation.setDuration(250)
        animation.setStartValue(0)
        animation.setEndValue(1)

        if reverse:
            animation.setStartValue(1)
            animation.setEndValue(0)
            animation.setDuration(150)
        
        animation.setEasingCurve(QEasingCurve.Type.OutInCubic)
        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        animation.finished.connect(lambda: target.setGraphicsEffect(None))