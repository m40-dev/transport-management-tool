from PyQt6 import QtCore, QtWidgets
from lib.ui.WidgetFactory.CustomWindowDecorations import WindowTitleBarDecoration

class CustomDialogWindow(QtWidgets.QDialog):

    def __init__(self, application, dialog_name=""):
        super(CustomDialogWindow, self).__init__(flags=QtCore.Qt.WindowType.Dialog | QtCore.Qt.WindowType.FramelessWindowHint, parent=application)

        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration

        self.setMinimumSize(600, 450)
        
        if dialog_name:
            self.setWindowTitle(f"{self.application.application_name} - {dialog_name}") 
        else:
            self.setWindowTitle(f"{self.application.application_name}")

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(1,1,1,1)
        
        window_decoration = WindowTitleBarDecoration(self, self.application)
        window_decoration.setWindowTitle(f"{self.application.application_name} - {dialog_name}")

        self.form_layout = QtWidgets.QGridLayout(self)
        self.form_layout.setSpacing(5)
        self.form_layout.setContentsMargins(10, 10, 10, 10)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setContentsMargins(10, 10, 10, 10)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(window_decoration, 0, 0)
        self.layout.addLayout(self.form_layout, 1, 0)
        self.layout.addWidget(self.buttonBox, 2, 0)
        self.setSizeGripEnabled(True)
        self.restoreWindowState()
        self.accepted = False

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
        super().reject()

    def reject(self):
        self.saveWindowState()
        self.accepted = False
        super().reject()