from PyQt6 import QtCore, QtWidgets, QtGui
from lib.ui.WidgetFactory.CustomWindowDecorations import WindowTitleDecoration
from lib.ui.CustomWindow.custom_window import CustomDialog

class CustomDialogWindow(CustomDialog):

    def __init__(self, application, dialog_name="", restore_window_state=True, window_mode=WindowTitleDecoration.Dialog):
        # super(CustomWindow, self).__init__()
        super(CustomDialogWindow, self).__init__(parent=self)
        
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration

        self.setMinimumSize(600, 450)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0,0,0,0)

        self.windowDecoration = WindowTitleDecoration(self, self.application, WindowMode=window_mode)

        self.form_layout = QtWidgets.QGridLayout()
        self.form_layout.setSpacing(5)
        self.form_layout.setContentsMargins(10, 10, 10, 10)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setContentsMargins(10, 10, 10, 10)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.windowDecoration, 0, 0)
        self.layout.addLayout(self.form_layout, 1, 0)
        self.layout.addWidget(self.buttonBox, 2, 0)

        if restore_window_state:
            self.restoreWindowState()

        self.setSizeGripEnabled(False)
        
        self.accepted = False
        self.cancelled = False

        if dialog_name:
            self.setWindowTitle(f"{self.application.application_name} - {dialog_name}") 
        else:
            self.setWindowTitle(f"{self.application.application_name}")
        
        
        self.windowDecoration.raise_()
        # self.show()
        
        

    def restoreWindowState(self):
        """ Restore window settings """
        # print("restore window")
        self.settings = self.application.settings
        if self.settings.value("CustomDialogWindow") is not None:
            self.restoreGeometry(self.settings.value("CustomDialogWindow"))

    def saveWindowState(self):
        # print("save window")
        self.application.settings.setValue("CustomDialogWindow", self.saveGeometry())

    def accept(self):
        self.saveWindowState()
        self.accepted = True
        return self.close(accepted=True)

    def reject(self):
        self.saveWindowState()
        self.accepted = False
        return self.close(accepted=False)

    def setWindowTitle(self, title):
        super().setWindowTitle(title)
        self.windowDecoration.setWindowTitle(title)

    def setIcon(self, icon):
        self.windowDecoration.setWindowIcon(icon)

    def close(self, accepted=None):
        if self.accepted:
            return super().accept()
        
        if accepted is None:
            self.cancelled = True
        
        return super().reject()
