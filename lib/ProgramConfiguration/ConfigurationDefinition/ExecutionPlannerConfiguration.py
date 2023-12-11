
EXECUTION_PLANNER_CONFIGURATION = {
    "ExecutionPlannerSettings":{
        "SectionName": "ExecutionPlannerSettings",
        "DisplayName": "Execution Planner Configuration",
        "Description": "Configuration Parameters section for the Execution planner module.",
        "TargetConfigurationFile": "ExecutionPlannerSettings",
        "ConfigurationParameters":
            {
                "ExecutionPreScript":{
                    "Display":"Execution Pre-Script",
                    "Description":"Configures the Execution Planner Pre-Script (powershell) that should be started before every Import/Export operation in the Execution Planner Queue.",
                    "FieldType":"CodeInput",
                    "CodeSyntax":"Powershell",
                    "FieldRole":"",
                    "DefaultValue":"",
                    "PlaceholderText":"Configure Custom Execution Planner Pre-Script...",
                    "IsMandatory":False,
                    "ShowInEditor":True,
                    "ShowInTreeView":False,
                    "IsForDataExport":True,
                    "UseTemplates":False
                },
                "ImportCommand":{
                    "Display":"Import Command",
                    "Description":"Configures custom Import command (Powershell) to be used instead of the native Transport Management Tool integration.",
                    "FieldType":"CodeInput",
                    "CodeSyntax":"Powershell",
                    "FieldRole":"",
                    "DefaultValue":"",
                    "PlaceholderText":"Configure Custom Import Command...",
                    "IsMandatory":False,
                    "ShowInEditor":True,
                    "ShowInTreeView":False,
                    "IsForDataExport":False,
                    "UseTemplates":False,
                    "IsSensitive":False
                },
                "ExportCommand":{
                    "Display":"Export Command",
                    "Description":"Configures custom Import command (Powershell) to be used instead of the native Transport Management Tool integration.",
                    "FieldType":"CodeInput",
                    "CodeSyntax":"Powershell",
                    "FieldRole":"",
                    "DefaultValue":"",
                    "PlaceholderText":"Configure Custom Export Command...",
                    "IsMandatory":False,
                    "ShowInEditor":True,
                    "ShowInTreeView":False,
                    "IsForDataExport":False,
                    "UseTemplates":False,
                    "IsSensitive":False
                },
                "ExecutionPostScript":{
                    "Display":"Execution Post-Script",
                    "Description":"Configures the Execution Planner Post-Script (powershell) that should be started after all Import/Export operations in the Execution Planner Queue are completed.",
                    "FieldType":"CodeInput",
                    "CodeSyntax":"Powershell",
                    "FieldRole":"",
                    "DefaultValue":"",
                    "PlaceholderText":"Configure Custom Execution Planner Post-Script...",
                    "IsMandatory":False,
                    "ShowInEditor":True,
                    "ShowInTreeView":False,
                    "IsForDataExport":False,
                    "UseTemplates":False
                },
                "AlwaysRunPostScript":{
                    "Display":"Always Run Post Script",
                    "Description":"Defines if the execution post-script should be started for every task in the Execution Planner Queue.",
                    "FieldType":"BooleanInput",
                    "FieldRole":"",
                    "DefaultValue":False,
                    "PlaceholderText":"Boolean field attribute",
                    "IsMandatory":False,
                    "ShowInEditor":True,
                    "ShowInTreeView":False,
                    "IsForDataExport":True,
                    "UseTemplates":False
                },
                "IgnoreExecutionErrors":{
                    "Display":"Ignore Execution Errors",
                    "Description":"Defines if the execution errors should end up in the execution queue termination.",
                    "FieldType":"BooleanInput",
                    "FieldRole":"",
                    "DefaultValue":False,
                    "PlaceholderText":"",
                    "IsMandatory":False,
                    "ShowInEditor":True,
                    "ShowInTreeView":False,
                    "IsForDataExport":True,
                    "UseTemplates":False
                }
            }
    }
}