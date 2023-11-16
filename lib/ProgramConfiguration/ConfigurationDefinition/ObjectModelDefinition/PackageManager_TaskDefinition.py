from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor import ObjectModelConfigurationEditor
PackageManager_TaskDefinition = {
    "SectionName": "PackageManager_TaskDefinition",
    "DisplayName": "Object Definition - Transport Task",
    "Description": "Configuration Parameters section for the Transport Task object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
        "TaskName": 
            {
                "FieldType": "StringInput",
                "FieldRole": "DisplayRole",
                "IsMandatory": "True",
                "RowId": 0
            },
        "Description": 
            {
                "FieldType": "TextInput",
                "FieldRole": "DescriptionRole",
                "ShowInTreeView": "False",
                "RowId": 1
            },
        "SortOrder": 
            {
                "FieldType": "IntegerInput",
                "FieldRole": "SortOrder",
                "MinValue": 1,
                "MaxValue": 99,
                "DefaultValue": 99,
                "DistributeEvenly": "True",
                "RowId": 2
            },
        "TaskType": 
            {
                "FieldType": "FixedInput",
                "Options": {"Transport Package": "Transport", "SQL Script": "SQL", "Schema Extension": "Schema", "Bug Fix Package": "BugFix"},
                "DefaultValue": "Transport",
                "Display": "Task Type",
                "IsMandatory": "True",
                "XMLTemplateTypes": ["Transport", "BugFix"],
                "RowId": 3
            },
        "DefinitionFile": 
            {
                "FieldType": "FileInput",
                "FileSelectionMode": "FileName",
                "RedirectDirectoryStatic": "Task_Definitions",
                "RedirectDirectoryRelativeTo": "Parent",
                "IsMandatory": "True",
                "RowId": 4
            },
        "ExportFile":
            {
                "FieldType": "FileInput",
                "FileSelectionMode": "FileName",
                "RedirectDirectoryDynamic": "Package_Data/%Parent.PackageName%/%TaskType%",
                "RowId": 5
            },
        "CompilerOption": 
            {
                "FieldType": "FixedInput",
                "Options": {"No Compilation": "None", "Full Compilation": "Full", "Skip Web Projects Compilation":"NoWeb"},
                "DefaultValue": "NoWeb",
                "RowId": 6
            },
        "AutoUpdate": 
            {
                "FieldType": "BooleanInput",
                "DefaultValue": "False",
                "RowId": 7
            },
        "Tag": 
            {
                "FieldType": "ListInput",
                "Separator": ",",
                "RowId": 8
            }
        }
}