ObjectModelConfigurationWidget = {
    "SectionName": "ObjectModelConfigurationWidget",
    "IsEditable": False,
    "Description": "Object Model configuration widget data",
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
            "FieldType":
                {
                    "Display": "Field Type",
                    "FieldType": "FixedInput",
                    "DefaultValue": "StringInput",
                    "Options": {
                        "String": "StringInput", 
                        "Text": "TextInput",
                        "Number": "IntegerInput",
                        "Boolean": "BooleanInput",
                        "Child Reference": "ChildObjectReference",
                        "File Path": "FileInput",
                        "Predefined List": "FixedInput",
                        "Multivalue field":"ListInput"}
                },
            "IsMandatory":
                {
                    "Display": "Is Mandatory",
                    "FieldType": "BooleanInput",
                    "DefaultValue": "False"
                },
            "ShowInEditor":
                {
                    "Display": "Show in Form Editor",
                    "FieldType": "BooleanInput",
                    "DefaultValue": "True"
                },
            "ShowInTreeView":
                {
                    "Display": "Show in TreeView",
                    "FieldType": "BooleanInput",
                    "DefaultValue": "False"
                },
            "FieldRole":
                {
                    "Display": "Field Role",
                    "FieldType": "FixedInput",
                    "DefaultValue": "",
                    "Options": {
                        "Display Role": "DisplayRole", 
                        "Description Role": "DescriptionRole",
                        "Sort Order": "SortOrder",
                        "Unique Identifier": "UniqueIdentifier",
                        "": ""
                        }
                },
            "DefaultValue":
                {
                    "Display": "Default Value",
                    "FieldType": "StringInput"
                },
            "PlaceholderText":
                {
                    "FieldType": "StringInput",
                    "Display": "Placeholder Text"
                },
            "MapValueFromParent":
                {
                    "Display": "Map Value From Parent Definition",
                    "FieldType": "BooleanInput",
                    "DefaultValue": "False"
                },
            "MinValue":
                {
                    "Display": "Minimum Value Range",
                    "FieldType": "IntegerInput"
                },
            "MaxValue":
                {
                    "Display": "Maximum Value Range",
                    "FieldType": "IntegerInput"
                },
            "ChildObjectClass":
                {
                    "FieldType": "FixedInput",
                    "DefaultValue": "",
                    "Options": {
                        "Transport Task Definition": "PackageManager_TaskDefinition", 
                        "Transport Execution Task": "ExecutionPlanner_ExecutionTask",
                        }
                }
            
            
        }
}