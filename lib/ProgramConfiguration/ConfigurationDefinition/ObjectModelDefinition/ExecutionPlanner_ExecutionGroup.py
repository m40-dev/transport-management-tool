from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor.ObjectModelEditor import ObjectModelConfigurationEditor
ExecutionPlanner_ExecutionGroup = {
    "SectionName": "ExecutionPlanner_ExecutionGroup",
    "DisplayName": "Object Definition - Execution Planner Group",
    "Description": "Configuration Parameters section for the Execution Planner Group object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
        "GroupName":{
            "Display":"Group Name",
            "Description":"Configures the Execution Group display name.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Group Name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False
        },
        "Description":{
            
            "Display":"Package Description",
            "Description":"Holds the description of the execution group.",
            "FieldType":"TextInput",
            "FieldRole":"DescriptionRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Group Description",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "ExecutionTasks":{
            
            "Display":"Execution Tasks",
            "Description":"Keeps the reference to the tasks and task groups to be executed as part of the execution group.",
            "FieldType":"ChildObjectReference",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":False,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Class":"ExecutionPlanner_ExecutionTask"
        }
        },
    "SubSections":{
        
    },
    "DefaultConfigurationItems":{
        "GroupName":{
            
            "Display":"Group Name",
            "Description":"Configures the Execution Group display name.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Group Name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False
        },
        "Description":{
            
            "Display":"Package Description",
            "Description":"Holds the description of the execution group.",
            "FieldType":"TextInput",
            "FieldRole":"DescriptionRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Group Description",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "ExecutionTasks":{
            
            "Display":"Execution Tasks",
            "Description":"Keeps the reference to the tasks and task groups to be executed as part of the execution group.",
            "FieldType":"ChildObjectReference",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":False,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Class":"ExecutionPlanner_ExecutionTask"
        }
    }
}