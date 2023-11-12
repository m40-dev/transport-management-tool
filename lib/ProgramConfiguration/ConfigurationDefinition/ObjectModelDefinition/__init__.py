from .PackageManager_PackageDefinition import *
from .PackageManager_TaskDefinition import *
from .ExecutionPlanner_ExecutionGroup import *
from .ExecutionPlanner_ExecutionTask import *
from .XMLTemplateEditor_RelationPreset import *

OBJECT_MODEL_CONFIGURATION = {
    "ObjectModel":{
        "SectionName": "ObjectModel",
        "DisplayName": "Object Model Configuration",
        "Description": "Configuration Parameters section definition for the global application appearance configuration.",
        "TargetConfigurationFile": "ObjectModelConfiguration",
        "ConfigurationParameters":{
            "TestParameter": {
                "DataType": "Boolean",
                "Display": "Use Test Model",
                "Description": "Defines whether the Test Model should be used.",
                "DefaultValue": False
                }
            },
        "SubSections": {
            "PackageManager_PackageDefinition": PackageManager_PackageDefinition,
            "PackageManager_TaskDefinition": PackageManager_TaskDefinition,
            "ExecutionPlanner_ExecutionGroup": ExecutionPlanner_ExecutionGroup,
            "ExecutionPlanner_ExecutionTask": ExecutionPlanner_ExecutionTask,
            "XMLTemplateEditor_RelationPreset": XMLTemplateEditor_RelationPreset
        }
    }
}