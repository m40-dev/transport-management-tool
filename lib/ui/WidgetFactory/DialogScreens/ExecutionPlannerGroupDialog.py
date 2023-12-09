from PyQt6 import QtCore, QtGui, QtWidgets
from pathlib import Path
import os


class ExecutionPlannerGroupDialog(QtWidgets.QDialog):

    def __init__(self, application, form_data):
        super(ExecutionPlannerGroupDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application
        self._form_data = form_data

        self.setWindowTitle(self.application.application_name + " - Execution Planner Group Configuration") 

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        
        self.name_label = QtWidgets.QLabel("Group Name:")
        self.name_input = QtWidgets.QLineEdit(self)

        self.description_label = QtWidgets.QLabel("Group Description:")
        self.description_input = QtWidgets.QTextEdit(self)
    

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.layout.addWidget(self.name_label, 0, 0)
        self.layout.addWidget(self.name_input, 0, 1)

        self.layout.addWidget(self.description_label, 1, 0)
        self.layout.addWidget(self.description_input, 1, 1, 2, 1)

        self.layout.addWidget(self.buttonBox, 3, 1, 1, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.setupForm()

        """ Connect Signals """
        self.name_input.textChanged.connect(self.update_form_data)
        self.description_input.textChanged.connect(self.update_form_data)


    def update_form_data(self):
        self._form_data["Name"] = self.name_input.text()
        self._form_data["Description"] = self.description_input.toPlainText()
        
    @property 
    def form_data(self):
        return self._form_data
    
    def setupForm(self):
        self.name_input.setText(self._form_data.get("Name", ""))
        self.description_input.setPlainText(self._form_data.get("Description", ""))
