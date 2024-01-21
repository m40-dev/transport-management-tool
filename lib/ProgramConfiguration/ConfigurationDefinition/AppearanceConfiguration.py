    
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
                "Description": "Configures global application background color for most of the views and windows.",
                "DefaultValue": "rgba(42, 42, 42, 255)"
            },
            "AltBaseColor":{
                "FieldType": "ColorInput",
                "Display": "Alternative Background Color",
                "Description": "Configures Alternative Background Color used in the displayed widgets (editor widgets, context menu etc).",
                "DefaultValue": "rgba(33, 33, 33, 120)"
            },
            "AltBaseColor2":{
                "FieldType": "ColorInput",
                "Display": "Alternative Background Color 2",
                "Description": "Configures Alternative Background Color used in the displayed widgets (window decorations, section headers etc).",
                "DefaultValue": "rgba(35, 35, 35, 255)"
            },
            "BorderColor":{
                "FieldType": "ColorInput",
                "Display": "Default Border Color",
                "Description": "Configures most of the application visible border lines.",
                "DefaultValue": "rgba(59, 59, 59, 255)"
            },
            "AltBorderColor":{
                "FieldType": "ColorInput",
                "Display": "Alternative Border Color",
                "Description": "Configures Alternative Border Color used in the displayed widgets",
                "DefaultValue": "rgba(91, 95, 95, 255)"
            },
            "TextColor":{
                "FieldType": "ColorInput",
                "Display": "Default Text Color",
                "Description": "Configures the global application text color for all widgets.",
                "DefaultValue": "rgba(203, 203, 203, 230)"
            },
            "AltTextColor":{
                "FieldType": "ColorInput",
                "Display": "Alternative Text Color",
                "Description": "Configures the alternative text color (used in buttons, tabs, menus and other navigation/action elements)",
                "DefaultValue": "rgba(64, 174, 243, 255)"
            },
            "AltTextColor2":{
                "FieldType": "ColorInput",
                "Display": "Alternative Text Color 2",
                "Description": "Configures the second alternative text color for the widgets.",
                "DefaultValue": "rgba(221, 80, 202, 255)"
            },
            "PlaceholderTextColor":{
                "FieldType": "ColorInput",
                "Display": "Placeholder Text Color",
                "Description": "Configures the placeholder text color on input widget fields.",
                "DefaultValue": "rgba(84, 148, 146, 255)"
            },
            "DescriptionTextColor":{
                "FieldType": "ColorInput",
                "Display": "Descriptions Text Color",
                "Description": "Configures the global application text color for description fields.",
                "DefaultValue": "rgba(53, 145, 142, 255)"
            },
            "HighlightColor":{
                "FieldType": "ColorInput",
                "Display": "Default Highlight Color",
                "Description": "Configure the standard background for the highlighted text and widgets.",
                "DefaultValue": "rgba(67, 72, 71, 255)"
            },
            "HighlightedText":{
                "FieldType": "ColorInput",
                "Display": "Highlighted Text Color",
                "Description": "Configures the color of the highlighted/selected text.",
                "DefaultValue": "rgba(113, 184, 231, 255)"
            },
            "ButtonColor":{
                "FieldType": "ColorInput",
                "Display": "Default Buttons Color",
                "Description": "Configure default background color for buttons.",
                "DefaultValue": "rgba(52, 52, 52, 120)"
            },
            "SelectedObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Selected/Highlighted Object Color",
                "Description": "Configures default background and also highlight color for widgets (selected and on hover).",
                "DefaultValue": "rgba(134, 139, 126, 65)"
            },
            "InactiveObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Inactive Object Color",
                "Description": "Configure background color of the inactive/disabled widgets.",
                "DefaultValue": "rgba(127, 127, 127, 80)"
            },
            "ParentObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Parent Object Color",
                "Description": "Configure background color of the Package Definition or Execution Planner Group custom view widgets.",
                "DefaultValue": "rgba(14, 13, 22, 55)"
            },
            "ChildObjectColor":{
                "FieldType": "ColorInput",
                "Display": "Child Object Color",
                "Description": "Configure background color of the Package Task Definition or Execution Planner Task custom view widgets.",
                "DefaultValue": "rgba(21, 26, 26, 55)"
            },
            "CodeEditBGColor":{
                "FieldType": "ColorInput",
                "Display": "Code Editor Background Color",
                "Description": "Code Editors Background color.",
                "DefaultValue": "rgba(37, 38, 37, 185)"
            },
            "CodeEditTextNormal":{
                "FieldType": "ColorInput",
                "Display": "Code Editor Normal Text Color",
                "Description": "Text color of the standard text.",
                "DefaultValue": "rgba(188, 200, 208, 255)"
            },
            "CodeEditTextComment":{
                "FieldType": "ColorInput",
                "Display": "Code Editor Comment",
                "Description": "Text Color of Comment nodes.",
                "DefaultValue": "rgba(222, 139, 37, 255)"
            },
            "CodeEditTextKeyword1":{
                "FieldType": "ColorInput",
                "Display": "Code Editor KeyWord1 Text Color",
                "Description": "Configures the keyword group styling in the code editors.",
                "DefaultValue": "rgba(185, 193, 191, 255)"
            },
            "CodeEditTextKeyword2":{
                "FieldType": "ColorInput",
                "Display": "Code Editor KeyWord2 Text Color",
                "Description": "Configures the keyword group styling in the code editors.",
                "DefaultValue": "rgba(145, 151, 154, 255)"
            },
            "CodeEditTextKeyword3":{
                "FieldType": "ColorInput",
                "Display": "Code Editor KeyWord3 Text Color",
                "Description": "Configures the keyword group styling in the code editors.",
                "DefaultValue": "rgba(89, 165, 200, 255)"
            },
            "CodeEditCaret":{
                "FieldType": "ColorInput",
                "Display": "Code Editor Caret Frame Color",
                "Description": "Configures the caret/line highlight color in the code editors.",
                "DefaultValue": "rgba(81, 134, 167, 255)"
            },
            "ExecutionLogBGColor":{
                "FieldType": "ColorInput",
                "Display": "Execution Log Console Background Color",
                "Description": "Base color for the console.",
                "DefaultValue": "rgba(29, 29, 29, 255)"
            },
            "ExecutionLogTextColor":{
                "FieldType": "ColorInput",
                "Display": "Execution Log Console Text Color",
                "Description": "Standard text color of the execution console logs.",
                "DefaultValue": "rgba(249, 175, 27, 255)"
            },
            "ExecutionLogAltTextColor":{
                "FieldType": "ColorInput",
                "Display": "Execution Log Console Alternative Text Color",
                "Description": "Configurens Execution Planner information messages",
                "DefaultValue": "rgba(69, 161, 171, 255)"
            },
            "ExecutionLogInitTextColor":{
                "FieldType": "ColorInput",
                "Display": "Execution Log Console Task Initialization Color",
                "Description": "Configures the initialization section main text color.",
                "DefaultValue": "rgba(243, 108, 18, 255)"
            },
            "ExecutionLogSuccessText":{
                "FieldType": "ColorInput",
                "Display": "Execution Log Console Success Text Color",
                "Description": "Configures the Execution log summary text color for tasks which completed successfully.",
                "DefaultValue": "rgba(236, 236, 208, 255)"
            },
            "ExecutionLogSuccess":{
                "FieldType": "ColorInput",
                "Display": "Execution Log Console Success Text Background Color (Summary)",
                "Description": "Configures the Execution log summary text background color for tasks which completed successfully.",
                "DefaultValue": "rgba(15, 113, 22, 255)"
            },
            "ExecutionLogErrorText":{
                "FieldType": "ColorInput",
                "Display": "Execution Log Console Error Text Color",
                "Description": "Configures the Execution log summary text color for tasks which completed with errors.",
                "DefaultValue": "rgba(236, 236, 208, 255)"
            },
            "ExecutionLogError":{
                "FieldType": "ColorInput",
                "Display": "Execution Log Console Error Text Background Color (Summary)",
                "Description": "Configures the Execution log summary text background color for tasks which completed with errors.",
                "DefaultValue": "rgba(156, 48, 50, 255)"
            },
        },
        "ConfigurationParameterGroups":{
            "BaseColorPalette":{
                "DisplayName": "Base Color Palette",
                "Description": "Configure the basic color palette of the entire application.",
                "ConfigurationKeys":["BaseColor", "AltBaseColor", "AltBaseColor2", "BorderColor", "AltBorderColor", "ButtonColor", "SelectedObjectColor", "InactiveObjectColor"]
            },
            "GlobalTextColorPalette":{
                "DisplayName": "Text Color Palette",
                "Description": "Configure the visible text color palette of the entire application.",
                "ConfigurationKeys":["TextColor", "AltTextColor", "AltTextColor2", "DescriptionTextColor", "PlaceholderTextColor", "HighlightColor", "HighlightedText" ]
            },
            "CodeEditorColorPalette":{
                "DisplayName": "Code Editors Color Palette",
                "Description": "Configure Code Editors Appearance.",
                "ConfigurationKeys":["CodeEditBGColor", "CodeEditTextNormal", "CodeEditTextComment", "CodeEditTextKeyword1", "CodeEditTextKeyword2", "CodeEditTextKeyword3", "CodeEditCaret" ]
            },
            "GlobalObjectColorPalette":{
                "DisplayName": "Custom Object Color Palette",
                "Description": "Configure Basic Package Manager Custom Widgets Appearance.",
                "ConfigurationKeys":["ParentObjectColor", "ChildObjectColor" ]
            },
            "ExecutionPlannerConsolePalette":{
                "DisplayName": "Execution Log Console Color Palette",
                "Description": "Configure Execution Log Console Appearance",
                "ConfigurationKeys":["ExecutionLogBGColor", "ExecutionLogTextColor", "ExecutionLogAltTextColor", "ExecutionLogInitTextColor", "ExecutionLogSuccess",  "ExecutionLogSuccessText", "ExecutionLogError", "ExecutionLogErrorText"]
            }
        }
    }
}
