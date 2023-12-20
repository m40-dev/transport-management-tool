from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QCloseEvent, QDragEnterEvent, QDragLeaveEvent, QDragMoveEvent

class ExecutionLogsReader(QtWidgets.QDialog):

    def __init__(self, parent, application, model_item):
        super(ExecutionLogsReader, self).__init__(flags=QtCore.Qt.WindowType.FramelessWindowHint|QtCore.Qt.WindowType.Dialog)
        self.parent = parent
        self.application = application
        self.ProgramConfiguration = application.ProgramConfiguration
        self.model_item = model_item
        self.setStyleSheet(self.application.styleSheet())
        self.setModal(False)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        
        self.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        self.setMinimumSize(800, 500)
        self.setSizeGripEnabled(True)
        
        self.startPosition = None

        # 0 - Normal Window, 1 - Maximized Window
        self.window_state = 0

        self.windowTitleWidget = QtWidgets.QFrame()
        self.windowTitleWidget.setProperty("CustomWindowDecoration", "TitleBar")
        self.windowTitleLayout = QtWidgets.QHBoxLayout(self.windowTitleWidget)
        self.windowTitleLayout.setContentsMargins(0,0,0,0)
        self.windowTitleLayout.setSpacing(1)

        self.titlebar = QtWidgets.QLabel(self.windowTitleWidget)

        self.windowTitleWidget.mousePressEvent = self.titleBarMousePressEvent
        self.windowTitleWidget.mouseMoveEvent = self.titleBarMouseMoveEvent
        self.windowTitleWidget.mouseReleaseEvent = self.titleBarMouseReleaseEvent

        self.titlebar.mousePressEvent = self.titleBarMousePressEvent
        self.titlebar.mouseMoveEvent = self.titleBarMouseMoveEvent
        self.titlebar.mouseReleaseEvent = self.titleBarMouseReleaseEvent

        self.setWindowTitle(f"{self.application.application_name} - Execution Logs - {model_item.display}") 

        window_icon = self.ProgramConfiguration.getIcon("ApplicationLogo")
        self.setWindowIcon(window_icon)
        self.customIcon = QtWidgets.QLabel(self)
        self.customIcon.setMinimumSize(20, 20)
        self.customIcon.setPixmap(window_icon.pixmap(20, 20))
        
        self.windowTitleLayout.addWidget(self.customIcon)
        self.windowTitleLayout.addWidget(self.titlebar)
        self.windowTitleLayout.addStretch(2)

        btn_minimize = QtWidgets.QToolButton()
        btn_maximize = QtWidgets.QToolButton()
        btn_close = QtWidgets.QToolButton()

        btn_minimize.clicked.connect(self.minimizeEvent)
        btn_maximize.clicked.connect(self.maximizeEvent)
        btn_close.clicked.connect(self.closeEvent)

        btn_minimize.setText("__")
        btn_maximize.setText("[  ]")
        btn_close.setText("X")
        
        btn_minimize.setProperty("CustomWindowDecoration", "MinimizeActionButton")
        btn_maximize.setProperty("CustomWindowDecoration", "MaximizeActionButton")
        btn_close.setProperty("CustomWindowDecoration", "CloseActionButton")
        
        self.windowTitleLayout.addWidget(btn_minimize)
        self.windowTitleLayout.addWidget(btn_maximize)
        self.windowTitleLayout.addWidget(btn_close)
        # self.windowTitleLayout.addWidget()

        self.customIcon.setProperty("CustomWindowDecoration", "WindowIcon")
        self.titlebar.setProperty("CustomWindowDecoration", "WindowTitle")
        
        
        self.console = QtWidgets.QTextEdit()
        self.console.setProperty("ExecutionPlanner", "ConsoleReader")

        self.layout.addWidget(self.windowTitleWidget, 0, 0)
        self.layout.addWidget(self.console, 1, 0)

        size_grip_nw = QtWidgets.QSizeGrip(self.windowTitleWidget)
        size_grip_nw.setProperty("Location", "NorthWest")
        size_grip_nw.setEnabled(True)
        self.layout.addWidget(size_grip_nw, 0, 0, alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)

        self.console.setAcceptRichText(True)
        self.console.setWordWrapMode(QtGui.QTextOption.WrapMode.WordWrap)
        self.console.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)
        self.console.setLineWrapColumnOrWidth(self.console.width())

        self.defaultBlockFormat = self.console.textCursor().blockFormat()
        self.defaultBlockFormat.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.defaultBlockFormat.setTopMargin(0)
        self.defaultBlockFormat.setBottomMargin(0)
        self.defaultBlockFormat.setLeftMargin(0)
        self.defaultBlockFormat.setRightMargin(0)

        self.console.textCursor().setBlockFormat(self.defaultBlockFormat)
        self.console.document().setDefaultStyleSheet(self.ProgramConfiguration.styleSheet())

    def showLogs(self):
        # self.console.setHtml("\n".join(self.model_item.execution_log))
        super().setWindowTitle(f"Execution Logs: {self.model_item.display}")
        self.setWindowTitle(f"<b>{self.application.application_name}</b> - <i>Execution Logs:</i> {self.model_item.display}")
        self.show()

        self.window().raise_()

        if self.window().isMinimized():
            if self.window_state == 1:
                self.window().showMaximized()
            else:
                self.window().showNormal()
            
    
    def setWindowTitle(self, title):
        self.titlebar.setText(title)
        self.windowTitleWidget.setToolTip(title)

    def appendLogs(self, formatted_message):
        cursor = self.console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End, QtGui.QTextCursor.MoveMode.MoveAnchor)
        if cursor.blockNumber() > 0:
            cursor.insertBlock(self.defaultBlockFormat)

        cursor.insertHtml(formatted_message)

        # restore cursor location at the end, this effectively scrolls the log view automatically
        self.console.setTextCursor(cursor)

    def titleBarMousePressEvent(self, event) -> None:
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.startPosition = event.position().toPoint()
        # event.accept()
    
    def titleBarMouseMoveEvent(self, event) -> None:
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton and self.startPosition is not None:
            delta = event.position().toPoint() - self.startPosition
            self.window().move(self.window().pos() + delta)
        # event.accept()
        
    def titleBarMouseReleaseEvent(self, event) -> None:
        self.startPosition
        # event.accept()

    def minimizeEvent(self):
        self.window().showMinimized()
    
    def maximizeEvent(self):
        if not self.window().isMaximized():
            self.window().showMaximized()
            self.window_state = 1
        else:
            self.window().showNormal()
            self.window_state = 0

    def closeEvent(self):
        self.hide()

    
