from PyQt6 import QtCore, QtGui, QtWidgets
from pathlib import Path
import os
import json
from copy import deepcopy

class TaskDefinitionDialog(QtWidgets.QDialog):

    def __init__(self, application, source_item=None):
        super(TaskDefinitionDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application
        self.source_item = source_item
        self._form_data = {}
        if source_item:
            self._form_data = deepcopy(source_item.edit_data)
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

        print(json.dumps(self._form_data))


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