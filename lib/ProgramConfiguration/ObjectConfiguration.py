from . import ProgramConfiguration

DEFINITION_FILE = "./object_definitions.json"

class ObjectConfiguration(ProgramConfiguration):
    def __init__(self, application, configuration_file=DEFINITION_FILE):
        super().__init__(application=application, configuration_file=configuration_file)


    def get_column_configuration(self, definition_class, column):
        object_configuration = self.get(definition_class)
        if object_configuration:
            return object_configuration.get(column, None)
        return None

