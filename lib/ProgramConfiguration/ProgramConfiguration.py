from PyQt6.QtCore import QObject
import json
from pathlib import Path
from .ConfigurationDefinition import PROGRAM_CONFIGURATION

class ProgramConfiguration(QObject):
    CONFIGURATION_FILE = "./program_configuration.json"
    BACKUP_FILE = "./program_configuration_default.json"

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.is_loaded = False
        self.configuration = None
        self.target_configuration = "ProgramConfiguration"

        self.configuration_file = self.CONFIGURATION_FILE
        if not Path(self.configuration_file).is_file():
            self.configuration_file = self.BACKUP_FILE
            
        self.reload_configuration_file()

    def load_file(self, file_path):
        file_content = ""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return file_content

    def get(self, configuration_key):
        if not self.is_loaded and self.configuration is None:
            self.reload_configuration_file()
        return self.configuration.get(configuration_key, None)

    def reload_configuration_file(self, file_path=None):
        if not file_path:
            file_path = self.configuration_file

        json_data  = self.load_file(file_path)
        if len(json_data.strip()) > 0:
            self.configuration = json.loads(json_data)
            self.is_loaded = True

    def isValidConfigurationSection(self, configuration_section):
        if configuration_section in self.configuration.keys():
            return True
        
        if configuration_section in PROGRAM_CONFIGURATION.keys():
            config = PROGRAM_CONFIGURATION[configuration_section]
            if config.get("TargetConfigurationFile", None) == self.target_configuration:
                return True
        
        #as last resort try to lookup if there are any subsections to check
        found_section = self.getConfigurationSection(configuration_section)
        if found_section and found_section.get("TargetConfigurationFile", False):
            return found_section["TargetConfigurationFile"] == self.target_configuration
        
        return False

    def getConfigurationSection(self, configuration_section, configuration_data=None):
        if not configuration_data:
            configuration_data = PROGRAM_CONFIGURATION
        
        if len(configuration_data) == 0:
            return False

        for section_key, section_configuration in configuration_data.items():
            if section_configuration.get("SectionName", False) == configuration_section:
                return section_configuration

            if "SubSections" in section_configuration.keys() and len(section_configuration["SubSections"]) > 0:
                return self.getConfigurationSection(configuration_section, section_configuration["SubSections"])
        
        return False
        
    def getConfigurationValue(self, configuration_section, configuration_key):
        if configuration_section in self.configuration.keys() and configuration_key in self.configuration[configuration_section].keys():
            return self.configuration[configuration_section][configuration_key]
        
        # not found in the user configuration
        # get the configuration from the default settings
        if (configuration_section in PROGRAM_CONFIGURATION.keys() 
            and "ConfigurationParameters" in PROGRAM_CONFIGURATION[configuration_section].keys()
            and configuration_key in PROGRAM_CONFIGURATION[configuration_section]["ConfigurationParameters"].keys()):
                default_configuration = PROGRAM_CONFIGURATION[configuration_section]["ConfigurationParameters"][configuration_key]
                return default_configuration.get("DefaultValue", None)
        return None

    def setConfigurationValue(self, configuration_section, configuration_key, configuration_value):
        if configuration_section in self.configuration.keys():
            self.configuration[configuration_section][configuration_key] = configuration_value

    def exportConfiguration(self):
        export_data = {}
        for configuration_section, configuration_data in PROGRAM_CONFIGURATION.items():
            if configuration_data.get("TargetConfigurationFile", None) == self.target_configuration:
                configuration_parameters = configuration_data.get("ConfigurationParameters", None)
                if len(configuration_parameters) > 0:
                    # print(configuration_parameters)
                    for configuration_key, configuration_details in configuration_parameters.items():
                        configuration_value = configuration_details.get("ConfigurationValue", None)
                        configuration_parameter = {configuration_key: configuration_value }
                        if configuration_section not in export_data.keys():
                            export_data[configuration_section] = {}
                        export_data[configuration_section].update(configuration_parameter)
        return export_data

    def saveConfiguration(self):
        export_data = self.exportConfiguration()
        export_json = json.dumps(export_data, indent=4, separators=(',',':'))

        export_file = self.CONFIGURATION_FILE
        
        with open(str(export_file), 'w', encoding="utf-8") as doc:
            doc.write(export_json)
        self.application.refresh_ui()
        
            
                            