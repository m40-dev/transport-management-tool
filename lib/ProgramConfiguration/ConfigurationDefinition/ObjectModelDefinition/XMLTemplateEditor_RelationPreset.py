from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor import ObjectModelConfigurationEditor

XMLTemplateEditor_RelationPreset = {
    "SectionName": "XMLTemplateEditor_RelationPreset",
    "DisplayName": "Object Definition - Relation Preset",
    "Description": "Configuration Parameters section for the Relation Preset object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
            "name":
                {
                    "FieldType": "StringInput",
                    "FieldRole": "DisplayRole",
                    "Display": "Relation Preset Name",
                    "Description": "Configures the display name of the relation preset in the user interface."
                },
            "description":
                {
                    "FieldType": "TextInput",
                    "Display": "Relation Preset Description"
                },
            "always_apply":
                {
                    "FieldType": "BooleanInput",
                    "DefaultValue": "False",
                    "Display": "Apply Preset Automatically"
                },
            "table_relations":
                {
                    "Display": "Selected Table Relations",
                    "Description": "Stores the selected table relations data for the relation preset.",
                    "FieldType": "ChildObjectReference",
                    "ShowInEditor": "False"
                }
        },
    "DefaultConfigurationItems":
        {
            "name":
                {
                    "FieldType": "StringInput",
                    "FieldRole": "DisplayRole",
                    "Display": "Relation Preset Name",
                    "Description": "Configures the display name of the relation preset in the user interface."
                },
            "table_relations":
                {
                    "Display": "Selected Table Relations",
                    "Description": "Stores the selected table relations data for the relation preset.",
                    "FieldType": "ChildObjectReference",
                    "ShowInEditor": "False"
                }
        }

}