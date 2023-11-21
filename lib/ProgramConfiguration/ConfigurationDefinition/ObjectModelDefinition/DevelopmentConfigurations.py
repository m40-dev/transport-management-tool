from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor import ObjectModelConfigurationEditor

DEVELOPMENT_CONFIGURATION = {
    "ObjectModelDevelopment":{
        "SectionName": "ObjectModelDevelopmentConfiguration",
        "IsEditable": False,
        "DisplayName": "Object Model Development Configurations",
        "Description": "Configuration Parameters section for the object model definitions.",
        "TargetConfigurationFile": "DevelopmentConfiguration",
        "ConfigurationEditor": ObjectModelConfigurationEditor,
        "ExportType": "ExportKeys",
        "ConfigurationParameters":{
            }
    }
}