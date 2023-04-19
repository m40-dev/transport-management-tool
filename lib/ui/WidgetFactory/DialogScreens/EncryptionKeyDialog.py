from PyQt6 import QtCore, QtGui, QtWidgets


class EncryptionKeyDialog(QtWidgets.QDialog):

    def __init__(self, application, initial=False):
        super(EncryptionKeyDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application

        self.setWindowTitle(self.application.windowTitle() + " - Encryption Key") 

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        
        description_text = "Please provide the main password to decrypt session details:"
        
        if initial:
            description_text = "Please set the main password that will be used to encrypt the session details:"

        self.description = QtWidgets.QLabel(description_text)
        self.key_label = QtWidgets.QLabel("Encryption Key:")
        self.key_input = QtWidgets.QLineEdit(self)
        self.key_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)


        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.layout.addWidget(self.description, 0, 0, 1, 0)
        self.layout.addWidget(self.key_label, 1, 0, 1, 1)
        self.layout.addWidget(self.key_input, 1, 1, 1, 1)
        self.layout.addWidget(self.buttonBox, 2, 1, 2, 1)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        QtCore.QMetaObject.connectSlotsByName(self)


    @property 
    def encryption_key(self):
        return self.key_input.text()
        