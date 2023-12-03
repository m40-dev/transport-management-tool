from .task_containers import *
from .transport_task import *
from .file_transport_task import *
from .object_transport_task import *
from .schema_transport_task import *
from .shell_transport_task import *
from .sql_transport_task import *
from .sysconfig_transport_task import *
from .tag_transport_task import *

TASKS = {
    "VI.Transport.ObjectTransport, VI.Transport": object_transport_task,
    "VI.Transport.SQLTransport, VI.Transport": sql_script_transport_task,
    "VI.Transport.TagTransport, VI.Transport": tag_transport_task,
    "VI.Transport.SchemaTransport, VI.Transport": schema_transport_task,
    "VI.Transport.FileTransport, VI.Transport": file_transport_task,
    "VI.Transport.DPR.ShellTransport, VI.Transport.DPR": shell_transport_task,
    "VI.Transport.BufferTransport, VI.Transport": sysconfig_transport_task
}