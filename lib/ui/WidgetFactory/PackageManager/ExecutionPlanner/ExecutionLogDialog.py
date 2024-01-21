from PyQt6 import QtCore, QtGui, QtWidgets
from lib.ui.WidgetFactory.CustomWindowDecorations import WindowTitleDecoration
from .ExecutionLogConsole import ExecutionLogConsole
from lib.ui.WidgetFactory.DialogScreens.CustomDialogWindow import CustomDialogWindow

class ExecutionLogDialog(CustomDialogWindow):

    def __init__(self, parent, application, model_item):
        super(ExecutionLogDialog, self).__init__(application=application, window_mode=WindowTitleDecoration.Window)

        self.model_item = model_item
        self.setModal(False)

        self.setMinimumSize(800, 500)

        self.console = ExecutionLogConsole(self, self.application)

        self.form_layout.addWidget(self.console, 1, 0)

        self.model_item.logExecutionState.connect(self.console.appendLogs)
        self.buttonBox.hide()
        

    def showLogs(self):
        # self.console.setHtml("\n".join(self.model_item.execution_log))
        self.setWindowTitle(f"Execution Logs: {self.model_item.display}")
        # self.windowDecoration.setWindowTitle(f"<b>{self.application.application_name}</b> - <i>Execution Logs:</i> {self.model_item.display}")
        self.show()
        self.window().raise_()

        if self.window().isMinimized():
            if self.window_state == 1:
                self.window().showMaximized()
            else:
                self.window().showNormal()

