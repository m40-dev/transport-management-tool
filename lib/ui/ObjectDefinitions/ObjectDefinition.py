from PyQt6.QtCore import QObject
import json

DEFINITION_FILE = "./object_definitions.json"

class ObjectDefinition(QObject):
    def __init__(self, application):
        super().__init__()
        self.application = application
        self.is_loaded = False
        self.object_definition = None
        self.reload_definition_file()

    def load_file(self, file_path):
        file_content = ""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return file_content

    def get(self, object_definition_class):
        if not self.is_loaded and self.object_definition is None:
            self.reload_definition_file()
        
        return self.object_definition.get(object_definition_class, None)

    def reload_definition_file(self, file_path=DEFINITION_FILE):
        json_data  = self.load_file(file_path)
        if len(json_data.strip()) > 0:
            self.object_definition = json.loads(json_data)
            self.is_loaded = True
