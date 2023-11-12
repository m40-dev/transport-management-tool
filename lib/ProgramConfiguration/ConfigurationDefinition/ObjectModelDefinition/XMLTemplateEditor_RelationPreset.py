XMLTemplateEditor_RelationPreset = {
    "SectionName": "XMLTemplateEditor_RelationPreset",
    "DisplayName": "Object Definition - Relation Preset",
    "Description": "Configuration Parameters section for the Relation Preset object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationParameters":{
            "name":
                {
                    "FieldType": "StringInput",
                    "Display": "Relation Preset Name"
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
                    "FieldType": "ChildObjectReference",
                    "ShowInEditor": "False"
                }
        }
}