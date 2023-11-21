from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor.ObjectModelEditor import ObjectModelConfigurationEditor
ExecutionPlanner_ExecutionGroup = {
    "SectionName": "ExecutionPlanner_ExecutionGroup",
    "DisplayName": "Object Definition - Execution Planner Group",
    "Description": "Configuration Parameters section for the Execution Planner Group object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
        "GroupName": 
            {
                "FieldType": "StringInput",
                "Display": "Group Name",
                "PlaceholderText": "Provide Group Name",
                "FieldRole": "DisplayRole"
            },
        "Description": 
            {
                "FieldType": "TextInput",
                "Display": "Package Description",
                "PlaceholderText": "Provide Package Description",
                "FieldRole": "DescriptionRole",
                "ShowInTreeView": "False"
            },
        "ExecutionTasks":
            {
                "FieldType": "ChildObjectReference",
                "Class": "ExecutionPlanner_ExecutionTask",
                "ShowInEditor": "False"
            }
        },
    "SubSections":{
        
    },
    "DefaultConfigurationItems":{
    }
}