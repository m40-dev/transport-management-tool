from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor import ObjectModelConfigurationEditor

ExecutionPlanner_ExecutionTask = {
    "SectionName": "ExecutionPlanner_ExecutionTask",
    "DisplayName": "Object Definition - Execution Planner Task",
    "Description": "Configuration Parameters section for the Execution Planner Task object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ExportType": "ExportKeys",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ConfigurationParameters":{
        "TaskName": 
            {
                "FieldType": "StringInput",
                "Display": "Task Name",
                "PlaceholderText": "Provide Task Name",
                "FieldRole": "DisplayRole",
                "Source": "TaskName"
            },
        "Description": 
            {
                "FieldType": "TextInput",
                "Display": "Package Description",
                "PlaceholderText": "Provide Package Description",
                "FieldRole": "DescriptionRole"
            },
        "TaskType":
            {
                "FieldType": "StringInput",
                "Source": "TaskType",
                "Transporter": ["Transport", "BugFix"],
                "SQLScript": ["SQL"],
                "SchemaExtension": ["Schema"]
            },
        "Connection":
            {
                "FieldType": "StringInput" 
            },
        "DefinitionFile":
            {
                "FieldType": "FileInput",
                "FileSelectionMode": "Relative"
            },
        "ExportFile":
            {
                "FieldType": "FileInput",
                "FileSelectionMode": "Relative"
            },
        "CompilerOption": 
            {
                "FieldType": "FixedInput",
                "Options": {"No Compilation": "None", "Full Compilation": "Full", "Skip Web Projects Compilation":"NoWeb"},
                "DefaultValue": "NoWeb"
            },
        "AutoUpdate":
            {
                "FieldType": "BooleanInput",
                "DefaultValue": "False"
            }
        },
    "DefaultConfigurationItems": {
    }
}