from .GeneralConfiguration import *
from .PackageManagerConfiguration import *
from .ObjectModelDefinition import *
from .ExecutionPlannerConfiguration import *

CONFIGURATION_FILES = {
    "ProgramConfiguration": "program_configuration.json", 
    "ObjectModelConfiguration": "object_configuration.json",
    # "DevelopmentConfiguration": "development_configuration.json"
    }

PROGRAM_CONFIGURATION = GENERAL_CONFIGURATION | PACKAGE_MANAGER_CONFIGURATION | EXECUTION_PLANNER_CONFIGURATION | OBJECT_MODEL_CONFIGURATION | DEVELOPMENT_CONFIGURATION
