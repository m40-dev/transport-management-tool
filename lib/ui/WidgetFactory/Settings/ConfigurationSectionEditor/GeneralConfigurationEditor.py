
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
from .ConfigurationSectionEditor import ConfigurationSectionEditor
from lib.ui.WidgetFactory.DialogScreens.FormEditorDialog import FormEditorObject

class GeneralConfigurationEditor(ConfigurationSectionEditor):
    def __init__(self, application, section_name, section_source):
        super().__init__(application=application, section_name=section_name, section_source=section_source)
        self.editors = {}
        if self._section_source.ConfigurationParameters:
            # row = 0
            for configuration_key, field_configuration in self._section_source.ConfigurationParameters.items():
                self.addToFormLayout(self.editor_layout, configuration_key, field_configuration, self.editor_layout.rowCount(), 0, 1, 1)
                # row += 1
        self.editor_layout.setRowStretch(self.editor_layout.rowCount()+1, 10)
        self.editor_layout.setColumnStretch(1, 2)
    
    def updateTempDisplay(self, configuration_key, test_label):
        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, "")
        test_label.setText(str(field_configuration))

    def updateConfigurationKey(self, configuration_key, new_value):
        # print(configuration_key, new_value)
        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, None)
        
        field_configuration["ConfigurationValue"] = new_value
    
    def getCurrentValue(self, configuration_key):
        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, {})
        configuration_value = field_configuration.get("ConfigurationValue", None)
        
        if not configuration_value:
            configuration_value = field_configuration.get("DefaultValue", None)

        return configuration_value


    def addToFormLayout(self, layout, column_name, field_configuration, row, column, rowSpan=1, colSpan=1):
        # current_value = self.configuration_item.data(column_name, None)
        current_value = self.getCurrentValue(column_name)
        
        # field_configuration = self.widget_data.get(column_name, None)
        if field_configuration:
            if current_value is None and "DefaultValue" in field_configuration.keys():
                current_value = field_configuration["DefaultValue"]
                # self.configuration_item.setData(column_name, current_value)
                
            field_editor = FormEditorObject(
                parent=self,
                application=self.application,
                column_name=column_name,
                column_configuration=field_configuration)

            if field_editor.editor:
                layout.addWidget(field_editor.label, row, column, rowSpan, 1)

                column+=1
                layout.addWidget(field_editor.editor, row, column, rowSpan, colSpan)
                
                # if current_value:
                field_editor.set_editor_data(current_value)

                field_editor.dataChanged.connect(self.updateConfigurationKey)

                field_editor.label.setProperty("ConfigurationEditor", "PropertyLabel")
                field_editor.editor.setProperty("ConfigurationEditor", "PropertyEditor")
            else:
                if field_editor.label:
                    field_editor.label.deleteLater()
                field_editor.label=None
            self.editors[column_name] = field_editor
            return field_editor
        return None

