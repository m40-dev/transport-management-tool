
from PyQt6 import QtWidgets

class ConfigurationSectionEditor(QtWidgets.QWidget):
    def __init__(self, application, section_name, section_source):
        super().__init__()

        self.application = application
        self.program_configuration = self.application.program_configuration
        self.object_configuration = self.application.object_configuration

        self._section_source = section_source
        self._section_name = section_name
    
        self.setupUi()

    def setupUi(self):

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setObjectName("MainLayout")
        self.layout.setSpacing(2)

        name_label = QtWidgets.QLabel(f"<h2>{self._section_source.DisplayName}</h2>")
        description_label = QtWidgets.QLabel(f"<p>{self._section_source.Description}</p>")
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        
        #layout for any dedicated editor widgets
        self.editor_layout = QtWidgets.QGridLayout()
        self.layout.setObjectName("EditorLayout")

        #Add Widgets to the main layout
        self.layout.addWidget(name_label)
        self.layout.addWidget(description_label)
        self.layout.addWidget(separator)
        self.layout.addLayout(self.editor_layout)
        self.layout.addStretch(2)