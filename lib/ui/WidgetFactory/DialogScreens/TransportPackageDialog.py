from PyQt6 import QtCore, QtGui, QtWidgets
from pathlib import Path
import os


class TransportPackageDialog(QtWidgets.QDialog):

    def __init__(self, application, directory, extension="xml"):
        super(TransportPackageDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application
        self.directory = directory
        self.extension = extension

        self.setWindowTitle(self.application.windowTitle() + " - Transport Package") 

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        
        description_text = "Please provide the Transport package details:"

        description = QtWidgets.QLabel(description_text)
        self.name_label = QtWidgets.QLabel("Package Name:")
        self.name_input = QtWidgets.QLineEdit(self)
    
        self.description_label = QtWidgets.QLabel("Package Description:")
        self.description_input = QtWidgets.QTextEdit(self)


        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.layout.addWidget(description, 0, 0, 1, 0)
        self.layout.addWidget(self.name_label, 1, 0, 1, 1)
        self.layout.addWidget(self.name_input, 1, 1, 1, 1)
        self.layout.addWidget(self.description_label, 2, 0, 1, 1)
        self.layout.addWidget(self.description_input, 2, 1, 1, 1)

        self.layout.addWidget(self.buttonBox, 3, 1, 3, 1)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        QtCore.QMetaObject.connectSlotsByName(self)

    def accept(self) -> None:
        self.file_path = f"{self.directory}{os.sep}{self.name}.{self.extension}"
        path_exists = Path(self.file_path).exists()
        if not path_exists:
            return super().accept()
        decision = QtWidgets.QMessageBox.information(self, "File Exists", f"Following file already exists: {self.name}.{self.extension}")
        
        
    @property 
    def name(self):
        return self.name_input.text()
    
    @property 
    def description(self):
        return self.description_input.toPlainText()
    
        