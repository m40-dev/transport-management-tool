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

PROGRAM_ICONS = {
    "VI.Transport.ObjectTransport, VI.Transport": "./lib/ui/img/icons/ObjectTransportTask.png",
    "VI.Transport.SQLTransport, VI.Transport": "./lib/ui/img/icons/SQLTransportTask.png",
    "VI.Transport.TagTransport, VI.Transport": "./lib/ui/img/icons/TagTransportTask.png",
    "VI.Transport.SchemaTransport, VI.Transport": "./lib/ui/img/icons/SchemaTransportTask.png",
    "VI.Transport.FileTransport, VI.Transport": "./lib/ui/img/icons/FileTransportTask.png",
    "VI.Transport.DPR.ShellTransport, VI.Transport.DPR": "./lib/ui/img/icons/ShellTransportTask.png",
    "VI.Transport.BufferTransport, VI.Transport": "./lib/ui/img/icons/BufferTransportTask.png",
    "Table_Object_Reference": "./lib/ui/img/icons/ObjectReference.png",
    "Transport_Object": "./lib/ui/img/icons/TransportObject.png",
    "Transport_SQL_Object": "./lib/ui/img/icons/Script.png",
    "TableDataItem": "./lib/ui/img/icons/TableDataItem.png",
    "ObjectDataItem": "./lib/ui/img/icons/ObjectDataItem.png",
    "PackageManager": "./lib/ui/img/icons/PackageManager.png",
    "XMLTemplateEditor":"./lib/ui/img/icons/XMLTemplateEditor.png",
    "Settings": "./lib/ui/img/icons/Settings.png"

}