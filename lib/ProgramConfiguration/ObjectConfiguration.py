from . import ProgramConfiguration
from pathlib import Path


class ObjectConfiguration(ProgramConfiguration):
    CONFIGURATION_FILE = "./object_configuration.json"
    BACKUP_FILE = "./object_configuration_default.json"

    def __init__(self, application):
        super().__init__(application=application)
        self.target_configuration = "ObjectModelConfiguration"

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

    def get_columns_configuration_by_role(self, definition_class, field_role):
        object_configuration = self.get(definition_class)
        columns = {}
        if object_configuration:
            for column, column_configuration in object_configuration.items():
                column_field_type = column_configuration.get("FieldRole", None)
                if column_field_type and column_field_type == field_role:
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

