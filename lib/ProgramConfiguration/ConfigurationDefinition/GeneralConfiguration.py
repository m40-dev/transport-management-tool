    
from lib.ui.WidgetFactory.Settings.ConfigurationSectionEditor.AppearanceEditor import ApplicationAppearanceEditor

APPEARANCE_CONFIGURATION = {
    "Appearance":{
        "SectionName": "Appearance",
        "DisplayName": "Program Appearance Configuration",
        "Description": "Configuration Parameters section for the global application look and feel configuration.",
        "TargetConfigurationFile": "ProgramConfiguration",
        "ConfigurationEditor": ApplicationAppearanceEditor,
        "ConfigurationParameters":{
            "BaseColor":{
                "FieldType": "ColorInput",
                "Display": "Default Background Color",
                "Description": "Configure global application background.",
                "DefaultValue": "rgba(27, 27, 27, 255)"
            },
            "AlternativeBaseColor":{
                "FieldType": "ColorInput",
                "Display": "Alternative Background Color",
                "Description": "Configure global application background.",
                "DefaultValue": "rgba(56, 56, 55, 255)"
            },
            "DarkerBaseColor":{
                "FieldType": "ColorInput",
                "Display": "Darker Background Color",
                "Description": "Configure global application background.",
                "DefaultValue": "rgba(35, 35, 35, 255)"
            },
            "BorderColor":{
                "FieldType": "ColorInput",
                "Display": "Default Border Color",
                "Description": "Configure most of the application visible border lines.",
                "DefaultValue": "rgba(59, 59, 59, 255)"
            },
            "HighlightColor":{
                "FieldType": "ColorInput",
                "Display": "Default Highlight Color",
                "Description": "Configure most of the application visible border lines.",
                "DefaultValue": "rgba(37, 38, 37, 120)"
            },
            "TextColor":{
                "FieldType": "ColorInput",
                "Display": "Default Text Color",
                "Description": "Configures the global application text color.",
                "DefaultValue": "rgba(239, 239, 239, 220)"
            },
            "AltTextColor":{
                "FieldType": "ColorInput",
                "Display": "Alternative Text Color",
                "Description": "Configures the alternative text color (mostly used in code editors for syntax highlighting - e.g. xml attribute names).",
                "DefaultValue": "rgba(204, 26, 106, 255)"
            },
            "AltTextColor2":{
                "FieldType": "ColorInput",
                "Display": "Alternative Text Color",
                "Description": "Configures the alternative text color (mostly used in code editors for syntax highlighting - e.g. xml tag nodes).",
                "DefaultValue": "rgba(77, 195, 221, 255)"
            },
            "DescriptionTextColor":{
                "FieldType": "ColorInput",
                "Display": "Descriptions Text Color",
                "Description": "Configures the global application text color for description fields.",
                "DefaultValue": "rgba(11, 170, 151, 255)"
            },
            "HighlightedText":{
                "FieldType": "ColorInput",
                "Display": "Highlighted Text Color",
                "Description": "Configures the highlighted text color.",
                "DefaultValue": "rgba(24, 169, 185, 255)"
            },
            "ButtonColor":{
                "FieldType": "ColorInput",
                "Display": "Default Buttons Color",
                "Description": "Configure default background color of the buttons.",
                "DefaultValue": "rgba(52, 52, 52, 120)"
            },
            "SelectedObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Selected Object Color",
                "Description": "Configure background color of the selected objects.",
                "DefaultValue": "rgba(0, 38, 34, 155)"
            },
            "InactiveObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Inactive Object Color",
                "Description": "Configure background color of the inactive widgets.",
                "DefaultValue": "rgba(195, 195, 195, 100)"
            },
            "GroupObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Group Object Color",
                "Description": "Configure background color of the Package Definition or Execution Planner Group widgets.",
                "DefaultValue": "rgba(40, 42, 43, 55)"
            },
            "TaskObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Task Object Color",
                "Description": "Configure background color of the Package Task Definition or Execution Planner Task widgets.",
                "DefaultValue": "rgba(74, 75, 75, 55)"
            }
        }
    }
}
