
from PyQt6.QtCore import pyqtSignal, QSize, QEasingCurve, QPropertyAnimation, QAbstractAnimation
from PyQt6.QtWidgets import QToolButton, QWidget, QVBoxLayout, QGraphicsOpacityEffect, QFrame
from PyQt6 import QtGui


class SideBar(QFrame):
    buttonClicked = pyqtSignal(int)

    def __init__(self, application, target_widget):
        super().__init__()
        self.target_widget = target_widget
        self.application = application

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        self.setObjectName("SideBar")
        self.navigation_buttons = []
        self.buttonClicked.connect(lambda index: self.target_widget.setCurrentIndex(index))
        self.target_widget.currentChanged.connect(self.currentViewChanged)
        self.target_widget.tabBar().setVisible(False)

    def addActionButton(self, index, action, widget, icon=None, show_action_text=True):
        button = QToolButton(self)
        if isinstance(icon, QtGui.QIcon):
            button.setIcon(icon)
        if show_action_text:
            button.setText(action)
        button.setCheckable(True)
        button.setProperty("ToolButton", "SideBar")
        button.setObjectName(action)

        self.layout.insertWidget(index, button)

        self.navigation_buttons.insert(index, button)
        self.target_widget.insertTab(index, widget, action)
        button.clicked.connect(lambda: self.buttonClicked.emit(index))

    def currentViewChanged(self, index):
        # print("mark sidebar button", index)
        for button in self.navigation_buttons:
            if button.isChecked():
                button.setChecked(False)
                
        if index <= len(self.navigation_buttons):
            current_button = self.navigation_buttons[index]
            current_button.setChecked(True)
        self.animate()
    
    def addStretch(self, index, stretch_factor=5): 
        self.layout.insertStretch(index, 5)

    def animate(self, reverse=False):
        # animate startup
        target = self.target_widget.currentWidget()

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