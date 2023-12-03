from .object_container import *
from .object_reference import *
from .sql_script_container import *

TASK_CONTAINERS = {
    "Table_Object_Reference": object_reference,
    "Transport_Object": object_container,
    "Transport_SQL_Object": sql_script_container
}