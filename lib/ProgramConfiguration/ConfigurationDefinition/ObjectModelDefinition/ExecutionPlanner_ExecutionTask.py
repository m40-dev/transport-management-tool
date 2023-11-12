ExecutionPlanner_ExecutionTask = {
    "SectionName": "ExecutionPlanner_ExecutionTask",
    "DisplayName": "Object Definition - Execution Planner Task",
    "Description": "Configuration Parameters section for the Execution Planner Task object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
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
        "PackageName":
            {
                "FieldType": "StringInput",
                "Source": "PARENT_DEF.PackageName"
            },
        "ParentDescription":
            {
                "FieldType": "StringInput",
                "Source": "PARENT_DEF.Description"
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
        }
}