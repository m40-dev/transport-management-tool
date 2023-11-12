
from PyQt6 import QtWidgets
from .ConfigurationSectionEditor import GeneralConfigurationEditor


class ConfigurationSectionTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, application, settings_module, section_name, section_data):
        super().__init__(parent)

        self._section_data = section_data
        self.application = application
        self.settings_module = settings_module
        self.section_editor = None
        self.setText(0, self.DisplayName)

        sub_sections = section_data.get("SubSections", None)
        if sub_sections and len(sub_sections) > 0:
            for sub_section_name, sub_section_data in sub_sections.items():
                ConfigurationSectionTreeWidgetItem(
                    parent=self, 
                    application=self.application, 
                    settings_module=settings_module,
                    section_name=sub_section_name, 
                    section_data=sub_section_data)
        
        for configuration_key, field_configuration in self.ConfigurationParameters.items():
            current_configuration = self.application.getConfigurationValue(section_name, configuration_key)
            field_configuration["ConfigurationValue"] = current_configuration
        
    def getSectionEditorWidget(self):
        if self.section_editor:
            return self.section_editor
        
        self.section_editor = GeneralConfigurationEditor(
            application=self.application, 
            section_name=self.SectionName,
            section_source=self)

        return self.section_editor
    
    def __getattr__(self, attribute):
        if attribute in self._section_data.keys():
            dict_data = self._section_data.get(attribute, None)
            if dict_data:
                return dict_data
        
        return self.__getattribute__(attribute)