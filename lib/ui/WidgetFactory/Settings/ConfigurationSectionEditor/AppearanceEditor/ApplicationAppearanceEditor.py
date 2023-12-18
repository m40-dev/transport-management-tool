
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, Qt
from ..ConfigurationSectionEditor import ConfigurationSectionEditor

class ApplicationAppearanceEditor(ConfigurationSectionEditor):

    def __init__(self, application, section_name, section_source):
        super().__init__(application=application, section_name=section_name, section_source=section_source)

        self.setupEditorUi()

    def TestConfiguration(self):
        styleSheet = self.ProgramConfiguration.reloadStyleSheet()
        self.setStyleSheet(styleSheet)
        self.application.styleSheetChanged.emit()


    def ApplyConfiguration(self):
        self.ProgramConfiguration.saveConfiguration(self.section_source.TargetConfigurationFile)

        info = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Icon.Information, 
            "Configuration Applied", 
            "Program Configuration saved.")
        info.exec()

    def setupEditorUi(self):

        TestButton = QtWidgets.QToolButton(self)
        TestButton.setText("Test Configuration")

        TestButton.clicked.connect(self.TestConfiguration)

        ApplyButton = QtWidgets.QToolButton(self)
        ApplyButton.setText("Apply and Save")
        ApplyButton.clicked.connect(self.ApplyConfiguration)

        self.layout.addWidget(TestButton, 1, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(ApplyButton, 1, 3, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.layout.setColumnStretch(0, 10)

        if self._section_source.ConfigurationParameters:
            for configuration_key, field_configuration in self._section_source.ConfigurationParameters.items():
                self.addToFormLayout(self.editor_layout, configuration_key, field_configuration, self.editor_layout.rowCount(), 0, 2, 1)

        self.editor_layout.setSpacing(10)
        self.editor_layout.setColumnStretch(0, 2)
        self.editor_layout.setColumnStretch(1, 5)
        self.editor_layout.setRowStretch(self.editor_layout.rowCount(), 15)


    