
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
        # print("adding section",self.SectionName, self.DisplayName)
        self.settings_module.configurationReloaded.connect(self.reloadSection)

        sub_sections = section_data.get("SubSections", None)
        if sub_sections and len(sub_sections) > 0:
            for sub_section_name, sub_section_data in sub_sections.items():
                if sub_section_data.get("IsEditable", True) is False:
                    continue
                
                ConfigurationSectionTreeWidgetItem(
                    parent=self, 
                    application=self.application, 
                    settings_module=settings_module,
                    section_name=sub_section_name, 
                    section_data=sub_section_data)
    
    def reloadSection(self):
        # section_data = self.application.ProgramConfiguration.getConfigurationSection(self.SectionName)
        # self.section_data = section_data
        if self.section_editor:
            self.section_editor.deleteLater()
            self.section_editor = None

    def getSectionEditorWidget(self):
        #refresh the configuration section data
        section_data = self.application.ProgramConfiguration.getConfigurationSection(self.SectionName)
        # print("Section Data for section", self.SectionName, section_data)
        if section_data:
            self._section_data = section_data
        
        if self.section_editor:
            return self.section_editor
            

        if self.ConfigurationEditor:
            self.section_editor = self.ConfigurationEditor(
                application=self.application, 
                section_name=self.SectionName,
                section_source=self
            )
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
        if attribute in self.__dict__.keys():
            return self.__getattribute__(attribute)
        return None
    
    @property
    def section_data(self):
        return self._section_data

    @section_data.setter
    def section_data(self, value):
        self._section_data = value