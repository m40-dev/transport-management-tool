PackageManager_TaskDefinition = {
    "SectionName": "PackageManager_TaskDefinition",
    "DisplayName": "Object Definition - Transport Task",
    "Description": "Configuration Parameters section for the Transport Task object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationParameters":{
        "TaskName": 
            {
                "FieldType": "StringInput",
                "FieldRole": "DisplayRole",
                "IsMandatory": "True"
            },
        "Description": 
            {
                "FieldType": "TextInput",
                "FieldRole": "DescriptionRole",
                "ShowInTreeView": "False"
            },
        "SortOrder": 
            {
                "FieldType": "IntegerInput",
                "FieldRole": "SortOrder",
                "MinValue": 1,
                "MaxValue": 99,
                "DistributeEvenly": "True"
            },
        "TaskType": 
            {
                "FieldType": "FixedInput",
                "Options": {"Transport Package": "Transport", "SQL Script": "SQL", "Schema Extension": "Schema", "Bug Fix Package": "BugFix"},
                "DefaultValue": "Transport",
                "Display": "Task Type",
                "IsMandatory": "True",
                "XMLTemplateTypes": ["Transport", "BugFix"]
            },
        "DefinitionFile": 
            {
                "FieldType": "FileInput",
                "FileSelectionMode": "FileName",
                "RedirectDirectoryStatic": "Task_Definitions",
                "RedirectDirectoryRelativeTo": "Parent",
                "IsMandatory": "True"
            },
        "ExportFile":
            {
                "FieldType": "FileInput",
                "FileSelectionMode": "FileName",
                "RedirectDirectoryDynamic": "Package_Data/%Parent.PackageName%/%TaskType%"
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
            },
        "Tag": 
            {
                "FieldType": "ListInput",
                "Separator": ","
            }
        }
}