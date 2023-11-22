from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor import ObjectModelConfigurationEditor

XMLTemplateEditor_RelationPreset = {
    "SectionName": "XMLTemplateEditor_RelationPreset",
    "DisplayName": "Object Definition - Relation Preset",
    "Description": "Configuration Parameters section for the Relation Preset object definition.",
    "TargetConfigurationFile": "ObjectModelConfiguration",
    "ConfigurationEditor": ObjectModelConfigurationEditor,
    "ExportType": "ExportKeys",
    "ConfigurationParameters":{
            "name":{
            
            "Display":"Relation Preset Name",
            "Description":"Configures the display name of the relation preset in the user interface.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Relation Preset Name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False
        },
        "description":{
            
            "Display":"Relation Preset Description",
            "Description":"Holds the description of the relation preset.",
            "FieldType":"TextInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide Relation Preset Description",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "always_apply":{
            
            "Display":"Apply Preset Automatically",
            "Description":"Determines if the relation preset should be automatically applied when new object with no relations is being added.",
            "FieldType":"BooleanInput",
            "FieldRole":"",
            "DefaultValue":False,
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "table_relations":{
            
            "Display":"Selected Table Relations",
            "Description":"Holds the selected table relations data for the relation preset.",
            "FieldType":"ChildObjectReference",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":False,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Class":""
        }
        },
    "DefaultConfigurationItems":
        {
            "name":{
            
            "Display":"Relation Preset Name",
            "Description":"Configures the display name of the relation preset in the user interface.",
            "FieldType":"StringInput",
            "FieldRole":"DisplayRole",
            "DefaultValue":"",
            "PlaceholderText":"Provide Relation Preset Name",
            "IsMandatory":True,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "IsSensitive":False
        },
        "description":{
            
            "Display":"Relation Preset Description",
            "Description":"Holds the description of the relation preset.",
            "FieldType":"TextInput",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"Provide Relation Preset Description",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "always_apply":{
            
            "Display":"Apply Preset Automatically",
            "Description":"Determines if the relation preset should be automatically applied when new object with no relations is being added.",
            "FieldType":"BooleanInput",
            "FieldRole":"",
            "DefaultValue":False,
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":True,
            "ShowInTreeView":False,
            "IsForDataExport":True
        },
        "table_relations":{
            
            "Display":"Selected Table Relations",
            "Description":"Holds the selected table relations data for the relation preset.",
            "FieldType":"ChildObjectReference",
            "FieldRole":"",
            "DefaultValue":"",
            "PlaceholderText":"",
            "IsMandatory":False,
            "ShowInEditor":False,
            "ShowInTreeView":False,
            "IsForDataExport":True,
            "Class":""
        }
        }

}