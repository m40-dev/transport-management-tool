
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, Qt
from ..ConfigurationSectionEditor import ConfigurationSectionEditor
from lib.ui.WidgetFactory import MsgBox

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
        
        MsgBox(
            application=self.application,
            window_mode=MsgBox.INFO,
            window_title="Configuration Saved",
            message="Program Configuration saved."
        ).exec()

        # info = QtWidgets.QMessageBox(
        #     QtWidgets.QMessageBox.Icon.Information, 
        #     "Configuration Applied", 
        #     "Program Configuration saved.")
        # info.exec()

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

        if self._section_source.ConfigurationParameters and self._section_source.ConfigurationParameterGroups:
            for parameter_group_configuration in self._section_source.ConfigurationParameterGroups.values():
                #Add Configuration Group Header and description
                display_name = parameter_group_configuration.get("DisplayName", None)
                description = parameter_group_configuration.get("Description", None)
                
                if display_name:
                    group_display = QtWidgets.QLabel(display_name)
                    group_display.setWordWrap(True)
                    group_display.setMinimumWidth(self.width())
                    group_display.setProperty("ConfigurationEditor", "ParameterGroupHeader")
                    group_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.editor_layout.addWidget(group_display, self.editor_layout.rowCount(), 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

                if description:
                    group_description = QtWidgets.QLabel(description)
                    group_description.setWordWrap(True)
                    group_description.setProperty("ConfigurationEditor", "ParameterGroupDescription")
                    group_description.setMinimumWidth(self.width())
                    group_description.setMinimumHeight(75)
                    group_description.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    row = self.editor_layout.rowCount()
                    self.editor_layout.addWidget(group_description, row, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)
                    self.editor_layout.setRowStretch(row, 5)

                # load defined parameters
                configuration_parameter_keys = parameter_group_configuration.get("ConfigurationKeys", None)
                if configuration_parameter_keys is not None:
                    for configuration_key in configuration_parameter_keys:
                        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, None)
                        if field_configuration:
                            self.addToFormLayout(self.editor_layout, configuration_key, field_configuration, self.editor_layout.rowCount(), 1, 2, 1)
                
                separator = QtWidgets.QFrame(self)
                separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
                separator.setProperty("ConfigurationEditor", "ParameterGroupSeparator")
                
                self.editor_layout.addWidget(separator, self.editor_layout.rowCount(), 0, 1, 3, Qt.AlignmentFlag.AlignTop)
                
            # for configuration_key, field_configuration in self._section_source.ConfigurationParameters.items():
            #     self.addToFormLayout(self.editor_layout, configuration_key, field_configuration, self.editor_layout.rowCount(), 0, 2, 1)

        self.editor_layout.setSpacing(10)
        self.editor_layout.setColumnStretch(0, 1)
        self.editor_layout.setColumnStretch(1, 2)
        self.editor_layout.setColumnStretch(2, 2)
        self.editor_layout.setRowStretch(self.editor_layout.rowCount(), 10)


    