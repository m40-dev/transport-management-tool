from PyQt6 import QtCore, QtWidgets


class RelationPresetDialog(QtWidgets.QDialog):

    def __init__(self, application):
        super(RelationPresetDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application
        self.setWindowTitle(self.application.application_name + " - Preset Configuration") 
        self.relations = []
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        
        description_text = "Please provide the preset details:"

        description = QtWidgets.QLabel(description_text)
        self.preset_name_label = QtWidgets.QLabel("Preset Name:")
        self.preset_name = QtWidgets.QLineEdit(self)

        self.preset_description_label = QtWidgets.QLabel("Preset Description:")
        self.preset_description = QtWidgets.QLineEdit(self)

        self.always_apply_checkbox = QtWidgets.QCheckBox(self)
        self.always_apply_checkbox.setText("Always apply relation for table")

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.layout.addWidget(description, 0, 0, 1, 0)

        self.layout.addWidget(self.preset_name_label, 1, 0, 1, 1)
        self.layout.addWidget(self.preset_name, 1, 1, 1, 1)

        self.layout.addWidget(self.preset_description_label, 2, 0, 1, 1)
        self.layout.addWidget(self.preset_description, 2, 1, 1, 1)
        self.layout.addWidget(self.always_apply_checkbox, 3, 1, 1, 1)
        
        """ Button Box - always in the bottom """
        self.layout.addWidget(self.buttonBox, self.layout.rowCount()+1, 1, 2, 1)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        QtCore.QMetaObject.connectSlotsByName(self)

    @property 
    def name(self):
        return self.preset_name.text()
    
    @property 
    def description(self):
        return self.preset_description.text()
    
    @property 
    def always_apply(self):
        return self.always_apply_checkbox.isChecked()

        
    @property
    def preset_data(self):
        preset_data = {
            "name": self.name,
            "description": self.description,
            "always_apply": self.always_apply,
            "table_relations": self.relations 
        }
        return preset_data
