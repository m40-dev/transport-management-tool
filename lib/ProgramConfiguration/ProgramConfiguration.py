from PyQt6.QtCore import QObject
import json
from pathlib import Path

class ProgramConfiguration(QObject):
    CONFIGURATION_FILE = "./program_configuration.json"
    BACKUP_FILE = "./program_configuration_default.json"

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.is_loaded = False
        self.configuration = None

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



