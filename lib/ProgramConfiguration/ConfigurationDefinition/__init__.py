from .GeneralConfiguration import *
from .PackageManagerConfiguration import *
from .ObjectModelDefinition import *


PROGRAM_CONFIGURATION = GENERAL_CONFIGURATION | PACKAGE_MANAGER_CONFIGURATION | OBJECT_MODEL_CONFIGURATION


