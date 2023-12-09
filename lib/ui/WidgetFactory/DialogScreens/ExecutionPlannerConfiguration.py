from PyQt6 import QtCore, QtGui, QtWidgets
from pathlib import Path
import os


class ExecutionPlannerConfigDialog(QtWidgets.QDialog):

    def __init__(self, application):
        super(ExecutionPlannerConfigDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application

        self.setWindowTitle(self.application.application_name + " - Execution Planner Configuration") 

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        
        self.import_label = QtWidgets.QLabel("Import Task Command:")
        self.import_command_input = QtWidgets.QLineEdit(self)

        self.export_label = QtWidgets.QLabel("Export Task Command:")
        self.export_command_input = QtWidgets.QLineEdit(self)
    
        self.module_init_label = QtWidgets.QLabel("Task Execution Preparation Script:")
        self.module_init_input = QtWidgets.QTextEdit(self)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")


        self.layout.addWidget(self.import_label, 0, 0)
        self.layout.addWidget(self.import_command_input, 0, 1)

        self.layout.addWidget(self.export_label, 1, 0)
        self.layout.addWidget(self.export_command_input, 1, 1)

        self.layout.addWidget(self.module_init_label, 2, 0, 1, 2)
        self.layout.addWidget(self.module_init_input, 3, 0, 1, 2)

        self.layout.addWidget(self.buttonBox, 4, 1, 1, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        QtCore.QMetaObject.connectSlotsByName(self)
        
    @property 
    def to_dict(self):
        configuration = {}
        configuration["ImportCommand"] = self.import_command_input.text()
        configuration["ExportCommand"] = self.export_command_input.text()
        configuration["ExecutionPreScript"] = self.module_init_input.toPlainText()
        return configuration
    
    
    def setupForm(self, configuration):
        if configuration:
            self.import_command_input.setText(configuration.get("ImportCommand", ""))
            self.export_command_input.setText(configuration.get("ExportCommand", ""))
            self.module_init_input.setText(configuration.get("ExecutionPreScript", ""))
