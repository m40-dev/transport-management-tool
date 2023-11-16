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
                "Source": "TaskName",
                "RowId": 0
            },
        "Description": 
            {
                "FieldType": "TextInput",
                "Display": "Package Description",
                "PlaceholderText": "Provide Package Description",
                "FieldRole": "DescriptionRole",
                "RowId": 1

            },
        "TaskType":
            {
                "FieldType": "StringInput",
                "Source": "TaskType",
                "Transporter": ["Transport", "BugFix"],
                "SQLScript": ["SQL"],
                "SchemaExtension": ["Schema"],
                "RowId": 2
            },
        "PackageName":
            {
                "FieldType": "StringInput",
                "Source": "PARENT_DEF.PackageName",
                "RowId": 3
            },
        "ParentDescription":
            {
                "FieldType": "StringInput",
                "Source": "PARENT_DEF.Description",
                "RowId": 4
            },
        "Connection":
            {
                "FieldType": "StringInput",
                "RowId": 5 
            },
        "DefinitionFile":
            {
                "FieldType": "FileInput",
                "FileSelectionMode": "Relative",
                "RowId": 6
            },
        "ExportFile":
            {
                "FieldType": "FileInput",
                "FileSelectionMode": "Relative",
                "RowId": 7
            },
        "CompilerOption": 
            {
                "FieldType": "FixedInput",
                "Options": {"No Compilation": "None", "Full Compilation": "Full", "Skip Web Projects Compilation":"NoWeb"},
                "DefaultValue": "NoWeb",
                "RowId": 8
            },
        "AutoUpdate":
            {
                "FieldType": "BooleanInput",
                "DefaultValue": "False",
                "RowId": 9
            }
        }
}