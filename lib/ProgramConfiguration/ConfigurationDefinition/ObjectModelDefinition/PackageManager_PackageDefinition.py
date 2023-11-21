from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor import ObjectModelConfigurationEditor

PackageManager_PackageDefinition = {
    "SectionName": "PackageManager_PackageDefinition",
    "DisplayName": "Object Definition - Transport Package",
    "Description": "Configuration Parameters section for the Transport Package object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
        "PackageName":{
            "RowId":0,
            "Display":"Package Name",
            "Description":"Holds the friendly name of the transport package object.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Package Name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "Description":{
            "RowId":1,
            "Display":"Package Description",
            "Description":"Holds the description of the transport package object.",
            "FieldType":"TextInput",
            "FieldRole":"DescriptionRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Package Description",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "SortOrder":{
            "RowId":2,
            "Display":"Sort Order",
            "Description":"Holds the sort order of the object in the list.",
            "FieldType":"IntegerInput",
            "FieldRole":"SortOrder",
            "DefaultValue":999,
            "PlaceholderText":"Provide Sort Order id",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "MinValue":100,
            "MaxValue":999,
            "DistributeEvenly":True
        },
        "DefinitionFile":{
            "RowId":3,
            "Display":"Package Definition File Name",
            "Description":"Holds the effective package definition file name and location in the workspace.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"definition.json",
            "PlaceholderText":"Enter Package Definition file name.",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":False,
            "FileSelectionMode":"FileName",
            "RedirectDirectoryStatic":"",
            "RedirectDirectoryDynamic":"Source_Files/%PackageName%",
            "RedirectDirectoryRelativeTo":"Parent"
        },
        "ChildTasks":{
            "RowId":4,
            "Display":"Package Tasks",
            "Description":"Child object class items to be exported into the package definition.",
            "FieldType":"ChildObjectReference",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Package Definition child tasks.",
            "IsMandatory":False,
            "ShowInEditor":False,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Class":"PackageManager_TaskDefinition"
        },
        "GUID":{
            "RowId":5,
            "Display":"",
            "Description":"Holds the unique identifier of the Transport Package definition object.",
            "FieldType":"StringInput",
            "FieldRole":"UniqueIdentifier",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        }
        },
    "DefaultConfigurationItems": {
        "PackageName":{
            "Display":"Package Name",
            "Description":"Holds the friendly name of the transport package object.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Package Name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
            },
        "DefinitionFile":{
            "Display":"Package Definition File Name",
            "Description":"Configures the effective package definition file name and location in the workspace.",
            "FieldType":"FileInput",
            "FieldRole":"",
            "DefaultValue":"definition.json",
            "PlaceholderText":"Enter Package Definition file name.",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":False,
            "FileSelectionMode":"FileName",
            "RedirectDirectoryStatic":"",
            "RedirectDirectoryDynamic":"Source_Files/%PackageName%",
            "RedirectDirectoryRelativeTo":"Parent"
        },
        "ChildTasks":{
            "Display":"Package Tasks",
            "Description":"Child object class items to be exported into the package definition.",
            "FieldType":"ChildObjectReference",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Package Definition child tasks.",
            "IsMandatory":False,
            "ShowInEditor":False,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Class":"PackageManager_TaskDefinition"
        }
    }
}


