
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from .ConfigurationSectionEditor import ConfigurationSectionEditor

class GeneralConfigurationEditor(ConfigurationSectionEditor):
    def __init__(self, application, section_name, section_source):
        super().__init__(application=application, section_name=section_name, section_source=section_source)

        for configuration_key, field_configuration in self._section_source.ConfigurationParameters.items():
            # print(configuration_key, field_configuration.get("DataType", None), field_configuration.get("Display", configuration_key))
            # test_label = QtWidgets.QLabel(str(field_configuration))
            # test_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard)
            # test_label.setWordWrap(True)
            # self.editor_layout.addWidget(test_label, self.editor_layout.rowCount(), 0)

            editor_widget = self.get_editorWidget(configuration_key, field_configuration)
            # editor_widget.editorValueChanged.connect(lambda configuration_key, value, label=test_label: self.updateTempDisplay(configuration_key, label))

            self.editor_layout.addWidget(editor_widget, self.editor_layout.rowCount()-1, 0)
            self.editor_layout.setRowStretch(self.editor_layout.rowCount(), 10)
            # self.editor_layout.setColumnStretch(0, 10)
    
    def updateTempDisplay(self, configuration_key, test_label):
        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, "")
        test_label.setText(str(field_configuration))

    def get_editorWidget(self, configuration_key, field_configuration):
        editor_widget = ConfigurationFieldEditorWidget(
            application=self.application, 
            section_name=self._section_name,
            configuration_key=configuration_key,
            field_configuration=field_configuration)
        editor_widget.editorValueChanged.connect(self.updateConfigurationKey)
        return editor_widget

    def updateConfigurationKey(self, configuration_key, new_value):
        print("configuration updated!", configuration_key, "new value", new_value)
        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, None)

        DataType = field_configuration.get("DataType", None)
        if not DataType:
            return False

        if DataType == "Boolean":
            new_value = new_value == 2

        field_configuration["ConfigurationValue"] = new_value

class ConfigurationFieldEditorWidget(QtWidgets.QWidget):
    editorValueChanged = pyqtSignal(str, object)

    def __init__(self, application, section_name, configuration_key, field_configuration):
        super().__init__()
        self.application = application
        self.field_configuration = field_configuration
        self.section_name = section_name
        self.configuration_key = configuration_key
        self.setupUi()

    def setupUi(self):
        self.layout = QtWidgets.QHBoxLayout(self)
        label = QtWidgets.QLabel(f'{str(self.field_configuration.get("Display", ""))}')
        label.setToolTip(str(self.field_configuration.get("Description", "")))
        label.setProperty("Label", "PropertyName")
        label.setFixedWidth(155)
        self.layout.addWidget(label)
        
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
        self.layout.addWidget(self.editor)
        self.layout.addStretch()

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