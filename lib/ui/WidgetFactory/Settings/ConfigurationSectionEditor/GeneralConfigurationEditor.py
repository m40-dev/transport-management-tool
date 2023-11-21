
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from .ConfigurationSectionEditor import ConfigurationSectionEditor

class GeneralConfigurationEditor(ConfigurationSectionEditor):
    def __init__(self, application, section_name, section_source):
        super().__init__(application=application, section_name=section_name, section_source=section_source)
        if self._section_source.ConfigurationParameters:
            for configuration_key, field_configuration in self._section_source.ConfigurationParameters.items():
                editor_widget = self.get_editorWidget(configuration_key, field_configuration)
                if editor_widget:
                    self.editor_layout.addWidget(editor_widget, self.editor_layout.rowCount(), 0, 1, 1)
        self.editor_layout.setRowStretch(self.editor_layout.rowCount()+1, 10)
    
    def updateTempDisplay(self, configuration_key, test_label):
        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, "")
        test_label.setText(str(field_configuration))

    def get_editorWidget(self, configuration_key, field_configuration):
        editor_widget = ConfigurationFieldEditorWidget(
            section_editor=self,
            application=self.application,
            configuration_key=configuration_key,
            field_configuration=field_configuration)
        editor_widget.editorValueChanged.connect(self.updateConfigurationKey)
        return editor_widget

    def updateConfigurationKey(self, configuration_key, new_value):
        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, None)

        DataType = field_configuration.get("DataType", None)
        if not DataType:
            return False

        if DataType == "Boolean":
            new_value = new_value == 2

        field_configuration["ConfigurationValue"] = new_value

    

class ConfigurationFieldEditorWidget(QtWidgets.QWidget):
    editorValueChanged = pyqtSignal(str, object)

    def __init__(self, section_editor, application, configuration_key, field_configuration):
        super().__init__()
        self.section_editor = section_editor
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self.field_configuration = field_configuration
        self.section_name = section_editor._section_name
        self.configuration_key = configuration_key
        self.section_editor.reloadEditor.connect(self.reload)
        self.setupUi()

    def reload(self):
        if self.editor:
            current_value = self.field_configuration.get("ConfigurationValue", None)
            print("reload widget", current_value)

    def setupUi(self):
        self.layout = QtWidgets.QGridLayout(self)
        label = QtWidgets.QLabel(f'{str(self.field_configuration.get("Display", ""))}')
        label.setWordWrap(True)

        label.setToolTip(str(self.field_configuration.get("Description", "")))
        label.setProperty("Label", "PropertyName")
        
        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 10)

        description_label = QtWidgets.QLabel(f'{str(self.field_configuration.get("Description", ""))}')
        description_label.setWordWrap(True)

        self.layout.addWidget(label, 0, 0)
        self.layout.addWidget(description_label, 1, 0)
        
        self.editor = None
        current_value = self.field_configuration.get("ConfigurationValue", None)

        DataType = self.field_configuration.get("DataType", None)
        if not DataType:
            return False
        
        if DataType == "Boolean":
            self.editor = QtWidgets.QCheckBox()

            if current_value:
                self.editor.setChecked(current_value)

            self.editor.stateChanged.connect(
                lambda value, column=self.configuration_key: 
                self.editorValueChanged.emit(column, value)
                )
        if DataType == "String":
            if self.field_configuration.get("isMultivalue", None):
                self.editor = QtWidgets.QPlainTextEdit()

                if current_value:
                    self.setValues(current_value)

                self.editor.textChanged.connect(self.updateValues)
            else:
                self.editor = QtWidgets.QLineEdit()
                if current_value:
                    self.editor.setText(str(current_value))

                self.editor.textChanged.connect(
                    lambda value=self.editor.text(), column=self.configuration_key: 
                    self.editorValueChanged.emit(column, value)
                    )

        if not self.editor:
            temp_label = QtWidgets.QLabel("Data Type not yet supported...")
            self.layout.addWidget(temp_label)
            return False

        self.editor.setProperty("Label", "PropertyValue")
        self.layout.addWidget(self.editor, 0, 1, 3, 1)
        self.layout.setRowStretch(3, 10)


    def setValues(self, value_list):
        if value_list is None:
            return False
        separator = ", "
        self.editor.setPlainText(separator.join(value_list))

    def getValues(self):
        separator = ","
        editor_text = self.editor.toPlainText().strip()
        if len(editor_text) == 0:
            return []

        values = editor_text.split(separator)

        return list(map(str.strip, values))

    def updateValues(self):
        self.editorValueChanged.emit(self.configuration_key, self.getValues())