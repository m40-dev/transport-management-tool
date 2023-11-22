from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor import ObjectModelConfigurationEditor

ExecutionPlanner_ExecutionTask = {
    "SectionName": "ExecutionPlanner_ExecutionTask",
    "DisplayName": "Object Definition - Execution Planner Task",
    "Description": "Configuration Parameters section for the Execution Planner Task object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ExportType": "ExportKeys",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ConfigurationParameters":{
        "TaskName":{
            
            "Display":"Task Name",
            "Description":"Holds the execution task display name.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Execution Task Name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False,
            "Source":"TaskName"
        },
        "Description":{
            
            "Display":"Task Description",
            "Description":"Holds the description of the Execution task",
            "FieldType":"TextInput",
            "FieldRole":"DescriptionRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Execution Task Description",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Source":"Description"
        },
        "TaskType":{
            
            "Display":"Task Type",
            "Description":"Defines the task type to be executed when the process is started. Task Type will accordingly determine the right tool to execute against the definition or export file.",
            "FieldType":"FixedInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Options":{
                'Transport Package': 'Transport',
                 'SQL Script': 'SQL',
                 'Schema Extension': 'Schema',
                 'Bug Fix Package': 'BugFix'},
            "Source":"TaskType",
            "Transporter":[
                "Transport",
                "BugFix"
            ],
            "SQLScript":[
                "SQL"
            ],
            "SchemaExtension":[
                "Schema"
            ]
        },
        "Connection":{
            
            "Display":"Connection Name",
            "Description":"Holds the connection name to be used when this task is executed.",
            "FieldType":"StringInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide the connection name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False,
            "Source":""
        },
        "DefinitionFile":{
            
            "Display":"Definition File",
            "Description":"Configures the source file to be used with the execution task.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide relative path to the task definition file..",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "FileSelectionMode":"Relative",
            "RedirectDirectoryStatic":"",
            "RedirectDirectoryDynamic":"",
            "RedirectDirectoryRelativeTo":"Parent",
            "Source":"DefinitionFile"
        },
        "ExportFile":{
            
            "Display":"Export File",
            "Description":"Configures the target file to be used with the execution task.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide relative path to the task export file..",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "FileSelectionMode":"Relative",
            "RedirectDirectoryStatic":"",
            "RedirectDirectoryDynamic":"",
            "RedirectDirectoryRelativeTo":"Parent",
            "Source":"ExportFile"
        },
        "CompilerOption":{
            
            "Display":"Compiler Configuration",
            "Description":"Holds the instructions for the compilation required when this transport package is being installed in the target system.",
            "FieldType":"FixedInput",
            "FieldRole":"",
            "DefaultValue":"NoWeb",
            "PlaceholderText":"Configure the Compiler option",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Options":{
                "No Compilation":"None",
                "Full Compilation":"Full",
                "Skip Web Projects Compilation":"NoWeb"
            },
            "Source":"CompilerOption"
        },
        "AutoUpdate":{
            
            "Display":"Automatic Updates",
            "Description":"Holds the instruction for the installer, whether the automatic local files update is required before the database compiler can be initiated.",
            "FieldType":"BooleanInput",
            "FieldRole":"",
            "DefaultValue":False,
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Source":"AutoUpdate"
        }
        },
    "DefaultConfigurationItems": {
        "TaskName":{
            
            "Display":"Task Name",
            "Description":"Holds the execution task display name.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Execution Task Name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False,
            "Source":"TaskName"
        },
        "Description":{
            
            "Display":"Task Description",
            "Description":"Holds the description of the Execution task",
            "FieldType":"TextInput",
            "FieldRole":"DescriptionRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Execution Task Description",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Source":"Description"
        },
        "TaskType":{
            
            "Display":"Task Type",
            "Description":"Defines the task type to be executed when the process is started. Task Type will accordingly determine the right tool to execute against the definition or export file.",
            "FieldType":"FixedInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Options": {
                'Transport Package': 'Transport', 
                'SQL Script': 'SQL',
                'Schema Extension': 'Schema',
                'Bug Fix Package': 'BugFix'},
            "Source":"TaskType",
            "Transporter":[
                "Transport",
                "BugFix"
            ],
            "SQLScript":[
                "SQL"
            ],
            "SchemaExtension":[
                "Schema"
            ]
        },
        "Connection":{
            
            "Display":"Connection Name",
            "Description":"Holds the connection name to be used when this task is executed.",
            "FieldType":"StringInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide the connection name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False,
            "Source":""
        },
        "DefinitionFile":{
            
            "Display":"Definition File",
            "Description":"Configures the source file to be used with the execution task.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide relative path to the task definition file..",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "FileSelectionMode":"Relative",
            "RedirectDirectoryStatic":"",
            "RedirectDirectoryDynamic":"",
            "RedirectDirectoryRelativeTo":"Parent",
            "Source":""
        },
        "ExportFile":{
            
            "Display":"Export File",
            "Description":"Configures the target file to be used with the execution task.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide relative path to the task export file..",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "FileSelectionMode":"Relative",
            "RedirectDirectoryStatic":"",
            "RedirectDirectoryDynamic":"",
            "RedirectDirectoryRelativeTo":"Parent",
            "Source":""
        },
        "CompilerOption":{
            
            "Display":"Compiler Configuration",
            "Description":"Holds the instructions for the compilation required when this transport package is being installed in the target system.",
            "FieldType":"FixedInput",
            "FieldRole":"",
            "DefaultValue":"NoWeb",
            "PlaceholderText":"Configure the Compiler option",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Options":{
                "No Compilation":"None",
                "Full Compilation":"Full",
                "Skip Web Projects Compilation":"NoWeb"
            },
            "Source":""
        },
        "AutoUpdate":{
            
            "Display":"Automatic Updates",
            "Description":"Holds the instruction for the installer, whether the automatic local files update is required before the database compiler can be initiated.",
            "FieldType":"BooleanInput",
            "FieldRole":"",
            "DefaultValue":False,
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Source":""
        }

    }
}