from .PackageManager_PackageDefinition import *
from .PackageManager_TaskDefinition import *
from .ExecutionPlanner_ExecutionGroup import *
from .ExecutionPlanner_ExecutionTask import *
from .XMLTemplateEditor_RelationPreset import *
from .ObjectModelConfiguration import *
from .DevelopmentConfigurations import *

OBJECT_MODEL_CONFIGURATION = {
    "ObjectModel":{
        "SectionName": "ObjectModel",
        "DisplayName": "Object Model Configuration",
        "Description": "Configuration Parameters section definition for the global application appearance configuration.",
        "TargetConfigurationFile": "ProgramConfiguration",
        "ExportType": "ExportValues",
        "ConfigurationParameters":{
            "UseExperimental": {
                "FieldType": "BooleanInput",
                "Display": "Use Experimental Object Model",
                "Description": "Turns on Experimental Object model features.",
                "DefaultValue": False
                }
            },
        "SubSections": {
            "PackageManager_PackageDefinition": PackageManager_PackageDefinition,
            "PackageManager_TaskDefinition": PackageManager_TaskDefinition,
            "ExecutionPlanner_ExecutionGroup": ExecutionPlanner_ExecutionGroup,
            "ExecutionPlanner_ExecutionTask": ExecutionPlanner_ExecutionTask,
            "XMLTemplateEditor_RelationPreset": XMLTemplateEditor_RelationPreset,
            "ObjectModelConfiguration": ObjectModelConfiguration
        }
    }
}

