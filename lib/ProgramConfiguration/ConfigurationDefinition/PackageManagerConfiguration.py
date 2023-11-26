
PACKAGE_MANAGER_CONFIGURATION = {
    "Package Manager":{
        "SectionName": "Package Manager",
        "DisplayName": "Package Manager Configuration",
        "Description": "Configuration Parameters section for the Package manager module.",
        "TargetConfigurationFile": "ProgramConfiguration",
        "ConfigurationParameters":
            {
                "WorkdirDirectoryBlacklist": {
                    "DataType": "String",
                    "Display": "Directory Blacklist",
                    "Description": "Configures the directory blacklist handling when the working directory is being loaded.\n\nComma delimited list of workspace relative folder locations is expected.",
                    "DefaultValue": [],
                    "isMultivalue": True
                },
                "WorkdirDirectoryWhitelist": {
                    "DataType": "String",
                    "Display": "Directory Whitelist",
                    "Description": "Configures the directory whitelist handling when the working directory is being loaded.\n\nComma delimited list of workspace relative folder locations is expected.",
                    "DefaultValue": [],
                    "isMultivalue": True
                },
                "ExcludedFiles": {
                    "DataType": "String",
                    "Display": "File Blacklist",
                    "Description": "Configures the individual files to be excluded when the working directory is being loaded.\n\nComma delimited list of workspace relative file locations is expected.",
                    "DefaultValue": [],
                    "isMultivalue": True
                },
                "ProcessQueueSize":{
                    "DataType": "Integer",
                    "Display": "Process Queue Size",
                    "Description": "Configures the queue size to be processed at once, when the working directory is being set (in 0.5s intervals). This can speed up data processing at cost of interface lockup.",
                    "DefaultValue": 5,
                    "isMultivalue": False

                }
            }
    }
}