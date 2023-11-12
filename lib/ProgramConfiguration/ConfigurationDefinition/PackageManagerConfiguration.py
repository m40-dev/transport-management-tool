
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
                    "Description": "Configures the directory blacklist handling when the working directory is being loaded.",
                    "DefaultValue": [],
                    "isMultivalue": True
                },
                "WorkdirDirectoryWhitelist": {
                    "DataType": "String",
                    "Display": "Directory Whitelist",
                    "Description": "Configures the directory whitelist handling when the working directory is being loaded.",
                    "DefaultValue": [],
                    "isMultivalue": True
                },
                "ExcludedFiles": {
                    "DataType": "String",
                    "Display": "File Blacklist",
                    "Description": "Configures the individual files to be excluded when the working directory is being loaded.",
                    "DefaultValue": [],
                    "isMultivalue": True
                }
            }
    }
}