
PACKAGE_MANAGER_CONFIGURATION = {
    "Package Manager":{
        "SectionName": "Package Manager",
        "DisplayName": "Package Manager Configuration",
        "Description": "Configuration Parameters section for the Package manager module.",
        "TargetConfigurationFile": "ProgramConfiguration",
        "ConfigurationParameters":
            {
                "WorkdirDirectoryBlacklist": {
                    "FieldType": "ListInput",
                    "Display": "Directory Blacklist",
                    "Description": "Configures the directory blacklist handling when the working directory is being loaded.\n\nComma delimited list of workspace relative folder locations is expected.",
                    "DefaultValue": [],
                    "Separator": ","
                },
                "WorkdirDirectoryWhitelist": {
                    "FieldType": "ListInput",
                    "Display": "Directory Whitelist",
                    "Description": "Configures the directory whitelist handling when the working directory is being loaded.\n\nComma delimited list of workspace relative folder locations is expected.",
                    "DefaultValue": [],
                    "Separator": ","
                },
                "ExcludedFiles": {
                    "FieldType": "ListInput",
                    "Display": "File Blacklist",
                    "Description": "Configures the individual files to be excluded when the working directory is being loaded.\n\nComma delimited list of workspace relative file locations is expected.",
                    "DefaultValue": [],
                    "Separator": ","
                },
                "ProcessQueueSize":{
                    "FieldType": "IntegerInput",
                    "Display": "Process Queue Size",
                    "Description": "Configures the queue size to be processed at once, when the working directory is being set (in 0.5s intervals). This can speed up data processing at cost of interface lockup.",
                    "DefaultValue": 5
                },
                "InitialWorkdir":{
                    "FieldType": "FileInput",
                    "Display": "Initial Working Directory",
                    "Description":"Configure the default working directory to load automatically when the program is started.",
                    "FileSelectionMode": "DirectoryPath",
                    "DefaultValue": None
                },
                "ExportBooleanAsString":{
                    "FieldType": "BooleanInput",
                    "Display": "Export Boolean As String",
                    "Description":"Wraps the Boolean values during JSON data export to be saved as string rather than raw boolean value.",
                    "DefaultValue": False
                },
                "ExportIntegerAsString":{
                    "FieldType": "BooleanInput",
                    "Display": "Export Integer As String",
                    "Description":"Wraps the Integer values during JSON data export to be saved as string rather than raw integer value.",
                    "DefaultValue": False
                }
            }
    }
}