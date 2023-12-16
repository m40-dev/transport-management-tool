    
from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor.AppearanceEditor import ApplicationAppearanceEditor

APPEARANCE_CONFIGURATION = {
    "Appearance":{
        "SectionName": "Appearance",
        "DisplayName": "Program Appearance Configuration",
        "Description": "Configuration Parameters section for the global application look and feel configuration.",
        "TargetConfigurationFile": "ProgramConfiguration",
        "ConfigurationEditor": ApplicationAppearanceEditor,
        "ConfigurationParameters":{
            "UseDarkTheme": {
                "FieldType": "BooleanInput",
                "Display": "Use Dark Theme",
                "Description": "Turn on the dark color palette.",
                "DefaultValue": False
                },
            "BaseColor":{
                "FieldType": "ColorInput",
                "Display": "Default Background Color",
                "Description": "Configure global application background.",
                "DefaultValue": "#ffeeff"
            },
            "AlternativeBaseColor":{
                "FieldType": "ColorInput",
                "Display": "Alternative Background Color",
                "Description": "Configure global application background.",
                "DefaultValue": "#fff"
            },
            "DarkerBaseColor":{
                "FieldType": "ColorInput",
                "Display": "Darker Background Color",
                "Description": "Configure global application background.",
                "DefaultValue": "#ffeeff"
            },
            "BorderColor":{
                "FieldType": "ColorInput",
                "Display": "Default Border Color",
                "Description": "Configure most of the application visible border lines.",
                "DefaultValue": "#ffeeff"
            },
            "HighlightColor":{
                "FieldType": "ColorInput",
                "Display": "Default Highlight Color",
                "Description": "Configure most of the application visible border lines.",
                "DefaultValue": "#f00"
            },
            "TextColor":{
                "FieldType": "ColorInput",
                "Display": "Default Text Color",
                "Description": "Configures the global application text color.",
                "DefaultValue": "#444"
            },
            "DescriptionTextColor":{
                "FieldType": "ColorInput",
                "Display": "Descriptions Text Color",
                "Description": "Configures the global application text color for description fields.",
                "DefaultValue": "#444"
            },
            "HighlightedText":{
                "FieldType": "ColorInput",
                "Display": "Highlighted Text Color",
                "Description": "Configures the highlighted text color.",
                "DefaultValue": "#444"
            },
            "ButtonColor":{
                "FieldType": "ColorInput",
                "Display": "Default Buttons Color",
                "Description": "Configure default background color of the buttons.",
                "DefaultValue": "#f00"
            },
            "SelectedObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Selected Object Color",
                "Description": "Configure background color of the selected objects.",
                "DefaultValue": "#f00"
            },
            "InactiveObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Inactive Object Color",
                "Description": "Configure background color of the inactive widgets.",
                "DefaultValue": "#f00"
            },
            "GroupObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Group Object Color",
                "Description": "Configure background color of the Package Definition or Execution Planner Group widgets.",
                "DefaultValue": "#f00"
            },
            "TaskObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Task Object Color",
                "Description": "Configure background color of the Package Task Definition or Execution Planner Task widgets.",
                "DefaultValue": "#f00"
            }
        }
    }
}
