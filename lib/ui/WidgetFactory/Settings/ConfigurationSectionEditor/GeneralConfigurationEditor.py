
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
from .ConfigurationSectionEditor import ConfigurationSectionEditor

class GeneralConfigurationEditor(ConfigurationSectionEditor):
    def __init__(self, application, section_name, section_source):
        super().__init__(application=application, section_name=section_name, section_source=section_source)
        
        if self._section_source.ConfigurationParameters:
            # row = 0
            for configuration_key, field_configuration in self._section_source.ConfigurationParameters.items():
                self.addToFormLayout(self.editor_layout, configuration_key, field_configuration, self.editor_layout.rowCount(), 0, 1, 1)
                # row += 1
        self.editor_layout.setSpacing(10)
        
        self.editor_layout.setColumnStretch(0, 2)
        self.editor_layout.setColumnStretch(1, 5)
        
        self.editor_layout.setRowStretch(self.editor_layout.rowCount(), 50)



