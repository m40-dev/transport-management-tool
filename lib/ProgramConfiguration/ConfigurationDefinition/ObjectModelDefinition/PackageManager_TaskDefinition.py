from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor import ObjectModelConfigurationEditor
PackageManager_TaskDefinition = {
    "SectionName": "PackageManager_TaskDefinition",
    "IsEditable": True,
    "DisplayName": "Object Definition - Transport Task",
    "Description": "Configuration Parameters section for the Transport Task object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
        "TaskName":{
            
            "Display":"Task Name",
            "Description":"Holds the friendly name of the transport package object.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False
        },
        "Description":{
            
            "Display":"Task Description",
            "Description":"Holds the description of the transport package object.",
            "FieldType":"TextInput",
            "FieldRole":"DescriptionRole",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "SortOrder":{
            
            "Display":"Sort Order",
            "Description":"Holds the sort order of the object in the list.",
            "FieldType":"IntegerInput",
            "FieldRole":"SortOrder",
            "DefaultValue":99,
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "MinValue":1,
            "MaxValue":99,
            "DistributeEvenly":True
        },
        "DefinitionFile":{
            
            "Display":"Transport Definition file name",
            "Description":"Holds the effective task definition file name and location in the workspace.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "FileSelectionMode":"FileName",
            "RedirectDirectoryStatic":"Task_Definitions",
            "RedirectDirectoryDynamic":"",
            "RedirectDirectoryRelativeTo":"Parent"
        },
        "ExportFile":{
            
            "Display":"Export file name",
            "Description":"Holds the effective transport package export file name and location in the workspace.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "FileSelectionMode":"FileName",
            "RedirectDirectoryStatic":"",
            "RedirectDirectoryDynamic":"Package_Data/%Parent.PackageName%/%TaskType%",
            "RedirectDirectoryRelativeTo":"Parent"
        },
        "TaskType":{
            
            "Display":"Task Type",
            "Description":"Holds the type of the transport task associated with the export file.",
            "FieldType":"FixedInput",
            "FieldRole":"",
            "DefaultValue":"Transport",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Options":{
                "Transport Package":"Transport",
                "SQL Script":"SQL",
                "Schema Extension":"Schema",
                "Bug Fix Package":"BugFix"
            },
            "XMLTemplateTypes":[
                "Transport",
                "BugFix"
            ]
        },
        "CompilerOption":{
            
            "Display":"Compiler Configuration",
            "Description":"Holds the instructions for the compilation required when this transport package is being installed in the target system.",
            "FieldType":"FixedInput",
            "FieldRole":"",
            "DefaultValue":"NoWeb",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Options":{
                "No Compilation":"None",
                "Full Compilation":"Full",
                "Skip Web Projects Compilation":"NoWeb"
            }
        },
        "AutoUpdate":{
            
            "Display":"AutoUpdate Required",
            "Description":"Holds the instruction for the installer, whether the automatic local files update is required before the database compiler can be initiated.",
            "FieldType":"BooleanInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "Tag":{
            
            "Display":"Object Tags",
            "Description":"Holds the list of tags which can be used for quick access and task object filtering.",
            "FieldType":"ListInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Separator":","
        }
        },
    "DefaultConfigurationItems":{
        "TaskName":{
            
            "Display":"Task Name",
            "Description":"Holds the friendly name of the transport package object.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False
        },
        "Description":{
            
            "Display":"Task Description",
            "Description":"Holds the description of the transport package object.",
            "FieldType":"TextInput",
            "FieldRole":"DescriptionRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide task description..",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "DefinitionFile":{
            
            "Display":"Transport Definition file name",
            "Description":"Holds the effective task definition file name and location in the workspace.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide task source/definition file name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "FileSelectionMode":"FileName",
            "RedirectDirectoryStatic":"Task_Definitions",
            "RedirectDirectoryDynamic":"",
            "RedirectDirectoryRelativeTo":"Parent"
        },
        "ExportFile":{
            
            "Display":"Export file name",
            "Description":"Holds the effective transport package export file name and location in the workspace.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide task export file name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "FileSelectionMode":"FileName",
            "RedirectDirectoryStatic":"",
            "RedirectDirectoryDynamic":"Package_Data/%Parent.PackageName%/%TaskType%",
            "RedirectDirectoryRelativeTo":"Parent"
        },
        "TaskType":{
            
            "Display":"Task Type",
            "Description":"Holds the type of the transport task associated with the export file.",
            "FieldType":"FixedInput",
            "FieldRole":"",
            "DefaultValue":"Transport",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Options":{
                "Transport Package":"Transport",
                "SQL Script":"SQL",
                "Schema Extension":"Schema",
                "Bug Fix Package":"BugFix"
            },
            "XMLTemplateTypes":[
                "Transport",
                "BugFix"
            ]
        },
        "CompilerOption":{
            
            "Display":"Compiler Configuration",
            "Description":"Holds the instructions for the compilation required when this transport package is being installed in the target system.",
            "FieldType":"FixedInput",
            "FieldRole":"",
            "DefaultValue":"NoWeb",
            "PlaceholderText":"",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Options":{
                "No Compilation":"None",
                "Full Compilation":"Full",
                "Skip Web Projects Compilation":"NoWeb"
            }
        },
        "AutoUpdate":{
            
            "Display":"AutoUpdate Required",
            "Description":"Holds the instruction for the installer, whether the automatic local files update is required before the database compiler can be initiated.",
            "FieldType":"BooleanInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        }
    }
}