from PyQt6 import QtCore, QtGui, QtWidgets
from lib.ui.WidgetFactory.CustomWindowDecorations import WindowTitleBarDecoration
from .ExecutionLogConsole import ExecutionLogConsole

class ExecutionLogDialog(QtWidgets.QDialog):

    def __init__(self, parent, application, model_item):
        super(ExecutionLogDialog, self).__init__(flags=QtCore.Qt.WindowType.CustomizeWindowHint|QtCore.Qt.WindowType.Dialog)
        
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

        self.windowDecoration = WindowTitleBarDecoration(self, self.application)
        self.console = ExecutionLogConsole(self, self.application)

        self.layout.addWidget(self.windowDecoration, 0, 0)
        self.layout.addWidget(self.console, 1, 0)

        self.model_item.logExecutionState.connect(self.console.appendLogs)
        

    def showLogs(self):
        # self.console.setHtml("\n".join(self.model_item.execution_log))
        self.setWindowTitle(f"Execution Logs: {self.model_item.display}")
        self.windowDecoration.setWindowTitle(f"<b>{self.application.application_name}</b> - <i>Execution Logs:</i> {self.model_item.display}")
        self.show()
        self.window().raise_()

        if self.window().isMinimized():
            if self.window_state == 1:
                self.window().showMaximized()
            else:
                self.window().showNormal()

