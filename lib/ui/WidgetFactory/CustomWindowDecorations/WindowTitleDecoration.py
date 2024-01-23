from PyQt6 import QtCore, QtWidgets
from lib.ui.CustomWindow.custom_window import CloseButton, MaximizeButton, MinimizeButton

IconSize = QtCore.QSize(20, 20)

class WindowTitleDecoration(QtWidgets.QFrame):
    MainWindow = "MAINWINDOW"
    Dialog = "DIALOG"
    Window = "WINDOW"
    def __init__(self, managed_window, application, WindowMode=Window):
        super(WindowTitleDecoration, self).__init__(parent=managed_window)
        self.parent = managed_window
        self.managed_window = managed_window
        self.application = application
        self.ProgramConfiguration = application.ProgramConfiguration

        # self.managed_window.setSizeGripEnabled(True)
        self.setMinimumHeight(30)
        self.setMaximumHeight(30)
        self.max_btn = None
        self.min_btn = None

        # 0 - Normal Window, 1 - Maximized Window
        self.window_state = 0

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.windowTitle = QtWidgets.QLabel(self)
        self.windowSubTitle = QtWidgets.QLabel(self)
        self.windowTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.windowTitle.mousePressEvent = self.mousePressEvent
        self.windowTitle.mouseDoubleClickEvent = self.mouseDoubleClickEvent

        self.windowSubTitle.mousePressEvent = self.mousePressEvent
        self.windowSubTitle.mouseDoubleClickEvent = self.mouseDoubleClickEvent

        self.windowIcon = self.ProgramConfiguration.getIcon("ApplicationLogo")
        self.managed_window.setWindowIcon(self.windowIcon)

        self.windowIconLabel = QtWidgets.QLabel(self)
        self.windowIconLabel.setMinimumSize(IconSize)

        self.setWindowIcon(self.windowIcon)

        if WindowMode != self.Dialog:
            self.min_btn = MinimizeButton(application)
            self.max_btn = MaximizeButton(application)
            self.min_btn.clicked.connect(self.minimizeEvent)
            self.max_btn.clicked.connect(self.maximizeEvent)

            min_icon = self.ProgramConfiguration.getIcon("MinimizeButton")
            max_icon = self.ProgramConfiguration.getIcon("MaximizeButton")

            if min_icon:
                self.min_btn.setIcon(min_icon)
            
            if max_icon:
                self.max_btn.setIcon(max_icon)

        self.close_btn = CloseButton(self)
        self.close_btn.clicked.connect(self.closeEvent)
        close_icon = self.ProgramConfiguration.getIcon("CloseButton")
        if close_icon:
            self.close_btn.setIcon(close_icon)

        self.layout.addWidget(self.windowIconLabel, 0, 0)
        self.layout.addWidget(self.windowTitle, 0, 1, alignment=QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.windowSubTitle, 0, 3)


        # self.layout.addWidget(spacer, 0, 4)
        
        self.layout.setColumnStretch(1, 2)
        self.layout.setColumnStretch(3, 2)
        # self.layout.setColumnStretch(2, 1)

        if WindowMode != self.Dialog:
            self.layout.addWidget(self.min_btn, 0, 4)
            self.layout.addWidget(self.max_btn, 0, 5)
        self.layout.addWidget(self.close_btn, 0, 6)

        # Configure Object Properties
        self.setObjectName("WindowTitleDecoration")
        self.setProperty("CustomWindowDecoration", "WindowDecoration")

        self.managed_window.setProperty("CustomWindowDecoration", "ManagedWindow")
        self.windowIconLabel.setProperty("CustomWindowDecoration", "WindowIcon")
        self.windowTitle.setProperty("CustomWindowDecoration", "WindowTitle")
        self.windowSubTitle.setProperty("CustomWindowDecoration", "WindowSubTitle")

        if WindowMode != self.Dialog:
            self.min_btn.setProperty("CustomWindowDecoration", "MinimizeActionButton")
            self.max_btn.setProperty("CustomWindowDecoration", "MaximizeActionButton")
            
        color_scheme = ["transparent", "rgba(170,0,0,150)", "rgba(170,0,0,150)"]
        self.close_btn.colors = color_scheme
        self.close_btn.setProperty("CustomWindowDecoration", "CloseActionButton")

        self.setWindowTitle(f"{self.application.application_name}") 
        self.refresh_ui()

    def setWindowIcon(self, icon):
        self.windowIconLabel.setPixmap(icon.pixmap(IconSize))

    def setMenuBar(self, menubar):
        self.layout.addWidget(menubar, 0, 2, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

    def refresh_ui(self):
        self.managed_window.setStyleSheet(self.ProgramConfiguration.styleSheet())
        self.setStyleSheet(self.ProgramConfiguration.styleSheet())
        self.windowTitle.raise_()

        #reset the color palette for custom window decoration buttons
        if self.min_btn or self.max_btn:
            selected_button_color = self.ProgramConfiguration.getColor("SelectedObjectColor")
            color_text = f"rgba({selected_button_color.red()}, {selected_button_color.green()}, {selected_button_color.blue()}, {selected_button_color.alpha()})"
            #Normal, Selected, Pressed
            color_scheme = ["transparent", color_text, color_text]

            if self.min_btn:
                self.min_btn.colors = color_scheme
            if self.max_btn:
                self.max_btn.colors = color_scheme

    def setWindowTitle(self, title):
        self.windowTitle.setText(title)
        self.windowIconLabel.setToolTip(title)

    def setSubTitle(self, subtitle):
        self.windowSubTitle.setText(subtitle)

    def mouseDoubleClickEvent(self, event=None) -> None:
        self.maximizeEvent()

    def mousePressEvent(self, event) -> None:
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.window().windowHandle().startSystemMove()
        self.updateWindowState()
        event.accept()
    
    def mouseReleaseEvent(self, event):
        self.updateWindowState()
        event.accept()
        
    def minimizeEvent(self):
        self.window().showMinimized()
    
    def maximizeEvent(self):
        if not self.max_btn:
            return 
            
        if not self.window().isMaximized():
            self.window().showMaximized()
        else:
            self.window().showNormal()

        self.updateWindowState()
    
    def updateWindowState(self):
        if self.window().isMaximized():
            self.window_state = 1
            if self.max_btn:
                self.max_btn.setProperty("CustomWindowDecoration", "RestoreActionButton")
                restore_icon = self.ProgramConfiguration.getIcon("RestoreButton")
                if restore_icon:
                    self.max_btn.setIcon(restore_icon)
            
        else:
            self.window_state = 0
            if self.max_btn:
                self.max_btn.setProperty("CustomWindowDecoration", "MaximizeActionButton")
                max_icon = self.ProgramConfiguration.getIcon("MaximizeButton")
                if max_icon:
                    self.max_btn.setIcon(max_icon)
        self.update()


    def closeEvent(self):
        self.managed_window.close()

    def animate(self, reverse=False):
        # animate startup
        
        effect = QtWidgets.QGraphicsOpacityEffect(self.managed_window)
        self.managed_window.setGraphicsEffect(effect)

        animation = QtCore.QPropertyAnimation(self.managed_window)

        animation.setPropertyName(bytes("opacity", "utf-8"))
        animation.setTargetObject(effect)
        animation.setDuration(450)
        animation.setStartValue(0)
        animation.setEndValue(1)

        animation.finished.connect(lambda: self.managed_window.setGraphicsEffect(None))

        if reverse:
            animation.setStartValue(1)
            animation.setEndValue(0)
            animation.setDuration(350)
            animation.finished.connect(self.managed_window.close)

        animation.setEasingCurve(QtCore.QEasingCurve.Type.OutInCubic)
        animation.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)