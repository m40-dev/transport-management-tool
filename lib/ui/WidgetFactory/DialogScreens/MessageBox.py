from PyQt6 import QtCore, QtGui, QtWidgets


class MsgBox(QtWidgets.QDialog):
    def __init__(self, application=None, message=None, detailed_message=None):
        super(MsgBox, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application

        self.setWindowTitle(self.application.windowTitle() + " - Exception") 
        self.setMinimumSize(500, 500)
        self.setModal(True)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setObjectName("layout")

        self.label = QtWidgets.QLabel(self)
        self.textinput = QtWidgets.QPlainTextEdit(self)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Close)
        self.buttonBox.setObjectName("buttonBox")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.label, 0, 0, 1, 2)
        self.layout.addWidget(self.textinput, 1, 0, 1, 2)
        self.layout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.label.setText(message)

        if detailed_message is not None:
            self.textinput.appendPlainText(detailed_message)
        
        self.exec()

