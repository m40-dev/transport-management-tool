from PyQt6.QtCore import QObject

class ObjectModel(QObject):
    def __init__(self, parent, application):
        super().__init__()
        self.application = application
        self.parent = parent

    def get_column_configuration(self, definition_class, column):
        return self.parent.getConfigurationKey(definition_class, column)

    def get_columns_configuration_by_type(self, definition_class, field_type):
        object_configuration = self.parent.getConfigurationParameters(definition_class)
        columns = {}
        if object_configuration:
            for column, column_configuration in object_configuration.items():
                column_field_type = column_configuration.get("FieldType", None)
                if column_field_type and column_field_type == field_type:
                    columns[column] = column_configuration
        return columns

    def get_columns_configuration_by_role(self, definition_class, field_role):
        object_configuration = self.parent.getConfigurationParameters(definition_class)
        columns = {}
        if object_configuration:
            for column, column_configuration in object_configuration.items():
                column_field_type = column_configuration.get("FieldRole", None)
                if column_field_type and column_field_type == field_role:
                    columns[column] = column_configuration
        return columns

    def get_columns_configuration_by_setting(self, definition_class, setting):
        object_configuration = self.parent.getConfigurationParameters(definition_class)
        columns = {}
        if object_configuration:
            for column, column_configuration in object_configuration.items():
                if column_configuration.get(setting, None):
                    columns[column] = column_configuration
        return columns
