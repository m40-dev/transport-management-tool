
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal

class ConfigurationSectionEditor(QtWidgets.QWidget):
    reloadEditor = pyqtSignal()
    
    def __init__(self, application, section_name, section_source):
        super().__init__()

        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration

        self._section_source = section_source
        self._section_name = section_name
        self.setupUi()

    def setupUi(self):

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("MainLayout")
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(2,2,2,2)

        name_label = QtWidgets.QLabel(f"<h2>{self._section_source.DisplayName}</h2>")
        description_label = QtWidgets.QLabel(f"<p>{self._section_source.Description}</p>")
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        
        #layout for any dedicated editor widgets
        self.editor_layout = QtWidgets.QGridLayout()
        self.editor_layout.setObjectName("EditorLayout")

        #Add Widgets to the main layout
        self.layout.addWidget(name_label, 0, 0)
        self.layout.addWidget(description_label,1, 0)
        self.layout.addWidget(separator, 2, 0, 1, -1)
        self.layout.addLayout(self.editor_layout, 3, 0, -1, -1)
