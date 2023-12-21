from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QMouseEvent

IconSize = QtCore.QSize(18, 18)

class WindowTitleBarDecoration(QtWidgets.QWidget):

    def __init__(self, managed_window, application):
        super(WindowTitleBarDecoration, self).__init__(parent=managed_window)
        
        self.managed_window = managed_window
        self.application = application
        self.ProgramConfiguration = application.ProgramConfiguration

        # self.managed_window.setSizeGripEnabled(True)
        
        self.startPosition = None

        # 0 - Normal Window, 1 - Maximized Window
        self.window_state = 0
        self.managed_window.setProperty("CustomWindowDecoration", "ManagedWindow")
        self.setProperty("CustomWindowDecoration", "TitleBar")

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(1)

        self.windowTitle = QtWidgets.QLabel(self)

        self.windowTitle.mousePressEvent = self.mousePressEvent
        self.windowTitle.mouseDoubleClickEvent = self.mouseDoubleClickEvent

        self.windowIcon = self.ProgramConfiguration.getIcon("ApplicationLogo")
        self.managed_window.setWindowIcon(self.windowIcon)

        self.windowIconLabel = QtWidgets.QLabel(self)
        self.windowIconLabel.setMinimumSize(IconSize)
        self.windowIconLabel.setPixmap(self.windowIcon.pixmap(IconSize))

        self.btn_minimize = QtWidgets.QToolButton()
        self.btn_maximize = QtWidgets.QToolButton()
        self.btn_close = QtWidgets.QToolButton()

        self.btn_minimize.clicked.connect(self.minimizeEvent)
        self.btn_maximize.clicked.connect(self.maximizeEvent)
        self.btn_close.clicked.connect(self.closeEvent)

        self.btn_minimize.setText("__")
        self.btn_maximize.setText("[ ]")
        self.btn_close.setText("X")

        size_grip_nw = QtWidgets.QSizeGrip(self)
        size_grip_nw.setProperty("Location", "NorthWest")
        size_grip_nw.setEnabled(True)
        
        # spacer = QtWidgets.QLabel(self)

        self.layout.addWidget(size_grip_nw, 0, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.windowIconLabel, 0, 0)
        self.layout.addWidget(self.windowTitle, 0, 1)
        # self.layout.addWidget(spacer, 0, 4)
        
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(5, 5)
        
        self.layout.addWidget(self.btn_minimize, 0, 6)
        self.layout.addWidget(self.btn_maximize, 0, 7)
        self.layout.addWidget(self.btn_close, 0, 8)

        self.windowIconLabel.setProperty("CustomWindowDecoration", "WindowIcon")
        self.windowTitle.setProperty("CustomWindowDecoration", "WindowTitle")

        self.btn_minimize.setProperty("CustomWindowDecoration", "MinimizeActionButton")
        self.btn_maximize.setProperty("CustomWindowDecoration", "MaximizeActionButton")
        self.btn_close.setProperty("CustomWindowDecoration", "CloseActionButton")

        self.setWindowTitle(f"{self.application.application_name}") 
        self.refresh_ui()

    def setMenuBar(self, menubar):
        separator = QtWidgets.QLabel("||")
        separator.setProperty("CustomWindowDecoration", "TitleBarSeparator")
        self.layout.addWidget(separator, 0, 2, alignment=QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(menubar, 0, 3, alignment=QtCore.Qt.AlignmentFlag.AlignVCenter)
        # self.layout.setColumnStretch(1, 1)
        # self.layout.setColumnStretch(4, 6)

    def refresh_ui(self):
        self.managed_window.setStyleSheet(self.application.styleSheet())

    def setWindowTitle(self, title):
        self.windowTitle.setText(title)
        self.windowIconLabel.setToolTip(title)

    def mouseDoubleClickEvent(self, event=None) -> None:
        self.maximizeEvent()

    def mousePressEvent(self, event) -> None:
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            # self.startPosition = event.position().toPoint()
            # print(type(self.managed_window))
            self.window().windowHandle().startSystemMove()
        # event.accept()
        

    def minimizeEvent(self):
        self.window().showMinimized()
    
    def maximizeEvent(self):
        if not self.window().isMaximized():
            self.btn_maximize.setProperty("CustomWindowDecoration", "RestoreActionButton")
            self.btn_maximize.setText("[-]")
            self.window().showMaximized()
            self.window_state = 1
        else:
            self.btn_maximize.setProperty("CustomWindowDecoration", "MaximizeActionButton")
            self.btn_maximize.setText("[ ]")
            self.window().showNormal()
            self.window_state = 0
        self.setStyleSheet(self.styleSheet())
    
    def closeEvent(self):
        self.managed_window.close()