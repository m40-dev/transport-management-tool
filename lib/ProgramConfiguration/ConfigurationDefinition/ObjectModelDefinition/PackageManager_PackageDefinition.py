PackageManager_PackageDefinition = {
    "SectionName": "PackageManager_PackageDefinition",
    "DisplayName": "Object Definition - Transport Package",
    "Description": "Configuration Parameters section for the Transport Package object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationParameters":{
        "PackageName": 
            {
                "FieldType": "StringInput",
                "Display": "Package Name",
                "PlaceholderText": "Provide Package Name",
                "FieldRole": "DisplayRole",
                "IsMandatory": "True"
            },
        "Description": 
            {
                "FieldType": "TextInput",
                "Display": "Package Description",
                "PlaceholderText": "Provide Package Description",
                "FieldRole": "DescriptionRole",
                "IsMandatory": "True",
                "ShowInTreeView": "False"
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
                "IsMandatory": "True"
            },
        "SortOrder":
            {
                "FieldType": "IntegerInput",
                "FieldRole": "SortOrder",
                "MinValue": 100,
                "MaxValue": 999,
                "DefaultValue": 100,
                "DistributeEvenly": "True",
                "ShowInTreeView": "False"
            },
        "ChildTasks": 
            {
                "FieldType": "ChildObjectReference",
                "Class": "PackageManager_TaskDefinition",
                "ShowInEditor": "False"
            },
        "GUID":
            {
                "FieldType": "StringInput",
                "FieldRole": "UniqueIdentifier"
            }
        }
}