from PyQt6 import QtCore, QtGui, QtWidgets
from pathlib import Path
import os


class PackageDefinitionDialog(QtWidgets.QDialog):

    def __init__(self, application, directory, extension="xml"):
        super(PackageDefinitionDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

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
    

class TaskDefinitionDialog(QtWidgets.QDialog):

    def __init__(self, application, source_item=None):
        super(TaskDefinitionDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application
        self.source_item = source_item
        self._form_data = {}
        if source_item:
            self._form_data = source_item.edit_data
        self.setMinimumSize(400, 400)

        self.setWindowTitle(self.application.windowTitle() + " - Task Definition") 

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        self.setup_form()

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.setRowStretch(self.layout.rowCount(), 2)
        self.layout.addWidget(self.buttonBox, self.layout.rowCount()+1, 1, 1, 2)

    def setup_form(self):
        # print("setup form")
        # print(self._form_data)
        for key, value in self._form_data.items():
            row_id = self.layout.rowCount()
            label = QtWidgets.QLabel(str(key))
            edit_field = QtWidgets.QLineEdit()
            edit_field.setText(str(value))
            self.layout.addWidget(label, row_id, 0, 1, 1)
            self.layout.addWidget(edit_field, row_id, 1, 1, 1)
            edit_field.textChanged.connect(
                lambda value, column=label.text(), editor=edit_field: 
                self.update_form_data(column, editor, value)
                )

    def update_form_data(self, column, editor, value):
        # print("update form data", column, editor, value)
        self._form_data[column] = value
        

    @property
    def form_data(self):
        # print("return form data", self._form_data)
        return self._form_data