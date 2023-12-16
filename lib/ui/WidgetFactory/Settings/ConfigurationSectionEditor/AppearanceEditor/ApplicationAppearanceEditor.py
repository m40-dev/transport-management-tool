
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
        
        # print("column configuration", self._section_source.ConfigurationParameters.get("BaseColor", {}))
        self.addToFormLayout(self.editor_layout, "UseDarkTheme", self._section_source.ConfigurationParameters.get("UseDarkTheme", {}), 0, 0 )

        if self._section_source.ConfigurationParameters:
            # row = 0
            for configuration_key, field_configuration in self._section_source.ConfigurationParameters.items():
                # skip this for now, manually added
                if configuration_key == "UseDarkTheme":
                    continue
                self.addToFormLayout(self.editor_layout, configuration_key, field_configuration, self.editor_layout.rowCount(), 0, 2, 1)
                # row += 1

        # self.addToFormLayout(self.editor_layout, "BaseColor", self._section_source.ConfigurationParameters.get("BaseColor", {}), self.editor_layout.rowCount(), 0)
        self.editor_layout.setSpacing(10)
        self.editor_layout.setColumnStretch(0, 2)
        self.editor_layout.setColumnStretch(1, 5)
        self.editor_layout.setRowStretch(self.editor_layout.rowCount(), 15)


    