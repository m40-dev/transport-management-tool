from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor import ObjectModelConfigurationEditor

PackageManager_PackageDefinition = {
    "SectionName": "PackageManager_PackageDefinition",
    "DisplayName": "Object Definition - Transport Package",
    "Description": "Configuration Parameters section for the Transport Package object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
        "PackageName": 
            {
                "FieldType": "StringInput",
                "Display": "Package Name",
                "PlaceholderText": "Provide Package Name",
                "FieldRole": "DisplayRole",
                "IsMandatory": "True",
                "RowId": 0
            },
        "Description": 
            {
                "FieldType": "TextInput",
                "Display": "Package Description",
                "PlaceholderText": "Provide Package Description",
                "FieldRole": "DescriptionRole",
                "IsMandatory": "True",
                "ShowInTreeView": "False",
                "RowId": 1
            },
        "DefinitionFile": 
            {
                "FieldType": "FileInput",
                "Display": "Definition File Name",
                "DefaultValue": "definition.json",
                "IsForDataExport": "False",
                "FileExtension": "*.json",
                "FileSelectionMode": "FileName",
                "RedirectDirectoryDynamic": "Source_Files/%PackageName%",
                "IsMandatory": "True",
                "RowId": 2
            },
        "SortOrder":
            {
                "FieldType": "IntegerInput",
                "FieldRole": "SortOrder",
                "MinValue": 100,
                "MaxValue": 999,
                "DefaultValue": 100,
                "DistributeEvenly": "True",
                "ShowInTreeView": "False",
                "RowId": 3
            },
        "ChildTasks": 
            {
                "FieldType": "ChildObjectReference",
                "Class": "PackageManager_TaskDefinition",
                "ShowInEditor": "False",
                "RowId": 4
            },
        "GUID":
            {
                "FieldType": "StringInput",
                "FieldRole": "UniqueIdentifier",
                "RowId": 5
            }
        }
}