from . import ProgramConfiguration

DEFINITION_FILE = "./object_configuration.json"
BACKUP_FILE = "./object_configuration_default.json"

class ObjectConfiguration(ProgramConfiguration):
    def __init__(self, application, configuration_file=DEFINITION_FILE):
        super().__init__(application=application, configuration_file=configuration_file)


    def get_column_configuration(self, definition_class, column):
        object_configuration = self.get(definition_class)
        if object_configuration:
            return object_configuration.get(column, None)
        return None
    
    def get_columns_configuration_by_type(self, definition_class, field_type):
        object_configuration = self.get(definition_class)
        columns = {}
        if object_configuration:
            for column, column_configuration in object_configuration.items():
                column_field_type = column_configuration.get("FieldType", None)
                if column_field_type and column_field_type == field_type:
                    columns[column] = column_configuration
        return columns

    def get_columns_configuration_by_setting(self, definition_class, setting):
        object_configuration = self.get(definition_class)
        columns = {}
        if object_configuration:
            for column, column_configuration in object_configuration.items():
                if column_configuration.get(setting, None):
                    columns[column] = column_configuration
        return columns

