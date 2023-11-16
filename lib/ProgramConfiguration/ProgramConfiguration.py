from PyQt6.QtCore import QObject
import json
from pathlib import Path
from copy import deepcopy
from .ObjectConfiguration import ObjectModel
from .ConfigurationDefinition import PROGRAM_CONFIGURATION, CONFIGURATION_FILES

class ProgramConfiguration(QObject):

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.configuration = {}
        self.ObjectModel = ObjectModel(self, application)
        self.ProgramConfiguration = deepcopy(PROGRAM_CONFIGURATION)
        self.reloadUserConfiguration()

    def load_file(self, file_path):
        file_content = ""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return file_content

    def get(self, configuration_key):
        configuration_data = self.configuration.get(configuration_key, None)
        if not configuration_data:
            return self.getConfigurationSection(configuration_key).get("ConfigurationParameters", None)

    def reloadUserConfiguration(self):
        self.ProgramConfiguration = deepcopy(PROGRAM_CONFIGURATION)
        self.configuration = {}
        for configuration_file in CONFIGURATION_FILES.values():
            if Path(configuration_file).is_file():
                json_data  = self.load_file(configuration_file)
                if len(json_data.strip()) > 0:
                    configuration_dict = json.loads(json_data)
                    if isinstance(configuration_dict, dict):
                        for section, configuration_data in configuration_dict.items():
                            self.configuration[section] = configuration_data
                        
                        self.updateProgramConfiguration(configuration_dict)
        
    def updateProgramConfiguration(self, configuration_dict, sort_items=True):
        for configuration_section, configuration_parameters in configuration_dict.items():
            
            section_configuration = self.getConfigurationSection(configuration_section)
            # section_parameters = section_configuration.get("ConfigurationParameters")

            if section_configuration.get("ExportType", "ExportValues") == "ExportKeys":
                # TODO: check if overwriting here always makes sense, we have some parameters that we rely on and have to be always
                # available (like CompilerOption, TaskType, DefinitionFile. we need those to be always present and if we do not get them from the custom configuration)
                # we will run into issues with the tool. Configuration issue, but still can be prevented
                if sort_items:
                    configuration_parameters = self.sortSectionItems(configuration_parameters)

                section_configuration["ConfigurationParameters"] = configuration_parameters
                self.configuration[configuration_section] = configuration_parameters
                continue
            
            if section_configuration.get("ExportType", "ExportValues") == "ExportValues":
                for configuration_key, parameter_value in configuration_parameters.items():
                    if configuration_key in section_configuration["ConfigurationParameters"].keys():
                        section_configuration["ConfigurationParameters"][configuration_key]["ConfigurationValue"] = parameter_value

    def sortSectionItems(self, section_data):
        i=0
        for entry_key, entry_configuration in section_data.items():
            if "RowId" not in entry_configuration.keys():
                entry_configuration["RowId"] = i
            i += 1

        items_data_sorted = {k: v for k, v in sorted(list(section_data.items()), key=lambda item: item[1].get("RowId",999))}
        return items_data_sorted


    def isValidConfigurationSection(self, configuration_section):
        if configuration_section in self.configuration.keys():
            return True
               
        #as last resort try to lookup if there are any subsections to check
        found_section = self.getConfigurationSection(configuration_section)
        return found_section.get("SectionName", None) == configuration_section

    def getConfigurationSection(self, configuration_section, configuration_data=None):
        if not configuration_data:
            configuration_data = self.ProgramConfiguration
        
        if len(configuration_data) == 0:
            return {}

        for section_key, section_configuration in configuration_data.items():
            if section_configuration.get("SectionName", False) == configuration_section:
                return section_configuration

            if "SubSections" in section_configuration.keys() and len(section_configuration["SubSections"]) > 0:
                return self.getConfigurationSection(configuration_section, section_configuration["SubSections"])
        return {}
    
    def getConfigurationKey(self, configuration_section, configuration_key):
        if configuration_section in self.configuration.keys() and configuration_key in self.configuration[configuration_section].keys():
            return self.configuration[configuration_section][configuration_key]
        
        configuration_parameters = self.getConfigurationParameters(configuration_section)
        if configuration_key in configuration_parameters.keys():
            default_configuration = configuration_parameters[configuration_key]
            return default_configuration
        return {}

    def getConfigurationValue(self, configuration_section, configuration_key):
        if configuration_section in self.configuration.keys() and configuration_key in self.configuration[configuration_section].keys():
            return self.configuration[configuration_section][configuration_key]
        
        # not found in the user configuration
        # get the configuration from the default settings
        configuration_parameters = self.getConfigurationParameters(configuration_section)
        if configuration_key in configuration_parameters.keys():
            default_configuration = configuration_parameters[configuration_key]
            
            configuration_value = default_configuration.get("ConfigurationValue", None)
            if not configuration_value:
                configuration_value = default_configuration.get("DefaultValue", None)
            
            if configuration_value is None and isinstance(default_configuration, dict):
                return default_configuration
            return configuration_value
        return None

    def getConfigurationParameters(self, configuration_section):
        # Search in the program configuration
        if (configuration_section in self.configuration.keys() 
            and self.isValidConfigurationSection(configuration_section)):
                return self.configuration[configuration_section]
        
        # search in default program configuration dictionaries
        section_data = self.getConfigurationSection(configuration_section=configuration_section)
        return section_data.get("ConfigurationParameters", {})

    #currently not in use
    def setConfigurationValue(self, configuration_section, configuration_key, configuration_value):
        if configuration_section in self.configuration.keys():
            self.configuration[configuration_section][configuration_key] = configuration_value

    def exportConfiguration(self, target_configuration="ProgramConfiguration", configuration_data=None, export_data={}):
        if configuration_data is None:
            configuration_data = self.ProgramConfiguration

        for configuration_section, configuration_data in configuration_data.items():
            if configuration_data.get("TargetConfigurationFile", None) == target_configuration:
                
                if configuration_section not in export_data.keys():
                    export_data[configuration_section] = {}

                configuration_parameters = configuration_data.get("ConfigurationParameters", None)
                if configuration_parameters and len(configuration_parameters) > 0:
                    # print(configuration_parameters)
                    if configuration_data.get("ExportType", "ExportValues") == "ExportValues":
                        for configuration_key, configuration_details in configuration_parameters.items():
                            configuration_value = configuration_details.get("ConfigurationValue", None)
                            
                            if configuration_value is None:
                                configuration_value = configuration_details.get("DefaultValue", None)
                            
                            configuration_parameter = {configuration_key: configuration_value}
                            export_data[configuration_section].update(configuration_parameter)

                    if configuration_data.get("ExportType", "ExportValues") == "ExportKeys":
                        configuration_parameters = self.sortSectionItems(configuration_parameters)
                        export_data[configuration_section].update(configuration_parameters)
            child_sections = configuration_data.get("SubSections", False)
            if child_sections and len(child_sections) > 0:
                self.exportConfiguration(target_configuration, child_sections, export_data)
        return export_data

    def saveConfiguration(self):
        #for time being use only the 
        for target_configuration, file_path in CONFIGURATION_FILES.items():
            export_data = self.exportConfiguration(target_configuration, configuration_data=self.ProgramConfiguration, export_data={})
            export_json = json.dumps(export_data, indent=4, separators=(',',':'))
            with open(str(file_path), 'w', encoding="utf-8") as doc:
                doc.write(export_json)
        self.application.refresh_ui()
        
            
                            