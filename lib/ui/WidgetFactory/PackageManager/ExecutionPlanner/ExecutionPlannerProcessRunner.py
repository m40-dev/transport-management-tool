    
from PyQt6.QtCore import QProcess, pyqtSignal, QIODeviceBase, QThread
from lib.db.database import DatabaseConnection 
import pathlib, shutil
from lib.ui.WidgetFactory import MsgBox
from timeit import default_timer as timer
from datetime import timedelta

class ProcessRunner(QProcess):
    message = pyqtSignal(str, str)
    taskStatusChanged = pyqtSignal(object, str)
    taskCompleted = pyqtSignal(object)
    stageFinished = pyqtSignal(object, object)

    def __init__(self, planner_widget):
        super().__init__()
        self.planner_widget = planner_widget
        self.application = self.planner_widget.application
        self.ConnectionHandler = self.application.ConnectionHandler
        self._current_workdir = None
        self.readyReadStandardOutput.connect(self.handleProcessStdOut)
        self.readyReadStandardError.connect(self.handleProcessStdErr)
        self.finished.connect(self.processExecutionFinished)
        self.stateChanged.connect(self.handleProcessState)
        
        self.is_running = False
        self.start_time = timer()
        self.current_item = None
        self.operation = "Export"
        self.connection_name = ""
        self.task_queue = []
        self.sql_thread = None
        self.was_error = False
        self.hasExecutionErrors = False

    @property
    def current_workdir(self):
        if self._current_workdir:
            return self._current_workdir
        return self.planner_widget.current_workdir

    def stopExecutionPlanner(self):
        for task in self.task_queue:
            task.ExecutionState = "Terminated"
        self.task_queue = []
        self.kill()
        if self.sql_thread:
            self.sql_thread.terminate()

    def queuePlannerTasks(self, task_items):
        for task_item in task_items:
            if task_item.task_class in ["ExecutionPlanner_ExecutionTask", "PackageManager_TaskDefinition"]:
                self.message.emit(f"Adding task to the execution queue.. ({task_item.display})", "Transport Manager")
                task_item.ExecutionState = "Queued"
                self.task_queue.append(task_item)
    
    def continueExecutionQueue(self):
        if len(self.task_queue) > 0 and self.state() != QProcess.ProcessState.Running:
            self.startProcessTask(self.task_queue[0], queued_task=True)

    def checkTaskType(self, task_type):
        task_configuration = self.application.getConfigurationParameters("ExecutionPlanner_ExecutionTask")
        task_type_configuration = task_configuration.get("TaskType", None)
        # configure task according to the task type settings
        if task_configuration and task_type_configuration:
            transporter_configuration = task_type_configuration.get("Transporter", [])
            if task_type in transporter_configuration:
                return "Transport"
            
            schema_configuration = task_type_configuration.get("SchemaExtension", [])
            if task_type in schema_configuration:
                return "SchemaExtension"
            
            sql_script_configuration = task_type_configuration.get("SQLScript", [])
            if task_type in sql_script_configuration:
                return "SQLScript"
        return None

    def getSourceValue(self, column, source_column):
        # map column with source object attributes
        source_value = self.current_item.task_data().get(source_column, None)
        if "PARENT_DEF." in source_column:
            parent_definition = self.current_item.package_definition
            parent_column = source_column.split(".")[1]
            if parent_definition:
                parent_value = parent_definition.get(parent_column, None)
                if not parent_value:
                    self.message.emit(
                    f"Unable to map the parent property [{parent_column}] or there is no value to be mapped.",
                    "Transport Manager")
                source_value = parent_value
        return source_value

    def startProcessTask(self, task_item, queued_task=False):
        task_name = task_item.display
        task_data = task_item.task_data()
        action_type = task_data.get("ExecutionType", None)
        self.operation = action_type
        task_type = task_data.get("TaskType", None)
        configuration_task_type = self.checkTaskType(task_type)

        # Get the up-to-date workdir configuration
        if not self.current_workdir and self.planner_widget.current_workdir:
            self.current_workdir = self.planner_widget.current_workdir

        if not self.current_workdir:
            self.message.emit(
            f"Task execution ({task_name}) cannot be started, working directory was not set.",
            "Transport Manager")
            return False
        
        if action_type == "Import" and configuration_task_type == "SQLScript":
            script_definition = task_data.get("DefinitionFile", None)
            if script_definition:
                script_path = pathlib.Path("/".join([self.current_workdir, script_definition]))
                script_content = ""
                if script_path.is_file():
                    script_content = self.application.load_file(str(script_path))
                
                if len(script_content.strip()) == 0:
                    self.message.emit(f"SQL script execution task skipped ({task_name}). There is no content in the sql script definition file.", "Transport Manager")
                    return False

                message = "SQL Script Execution Detected.\n\n"
                message += "Running raw SQL scripts can lead to potentially dangerous situations and can cause unexpected database behavior.\n\n"
                message += "Are you sure you want to execute this script?\n\n"
                message += "Selecting 'No' will skip this task and will not add script to the execution queue.\n\n"
                message += "You can preview the script by clicking on the 'Show Details' button."
                
                confirmation_dialog = MsgBox(self.application, message, script_content, MsgBox.QUESTION)
                if not confirmation_dialog.accepted:
                    return False
        
        if action_type == "Export":
            export_file = task_data.get("ExportFile", "")
            definition_file = task_data.get("DefinitionFile", "")

            if definition_file and export_file and len(export_file.strip()) == 0 or len(definition_file.strip()) == 0:
                self.message.emit(f"Export task execution skipped ({task_name}). There is no source or/and export file configured.", "Transport Manager")
                return False

        if self.state() == QProcess.ProcessState.Running:
            if task_item.task_class in ["ExecutionPlanner_ExecutionTask", "PackageManager_TaskDefinition"]:
                self.task_queue.append(task_item)
                self.message.emit(f"Adding task to the execution queue.. ({task_name})", "Transport Manager")
                task_item.ExecutionState = "Queued"
                return True
            return False
        
        if queued_task and len(self.task_queue) > 0:
            self.task_queue.remove(self.task_queue[0])
        
        # prepare some task variables
        self.current_item = task_item
        self.hasExecutionErrors = False
        self.start_time = timer()
        
        connection_name = task_data.get("Connection", None)
        self.connection_name = connection_name
        planner_configuration = self.application.settings.value("ExecutionPlannerSettings")

        # if action or task type are not known, we cant do much
        if not action_type or not task_type:
            self.message.emit("Missing Action Type or Task Type. Operation cancelled.", "Transport Manager")
            return False

        # moving forward
        self.message.emit(
            f"Starting task execution ({task_name}).",
            "INIT")

        # prepare variables script
        variables_script = self.prepareProcessVariables(task_data)
        self.message.emit("Local variables generated.", "Transport Manager")
        
        
        initializer_script = planner_configuration.get("ExecutionPreScript", "") + "\r\n"
        self.message.emit("Initializer script ready.", "Transport Manager")

        command = ""
        execution_command = ""
        post_processing_commands = ""
        
        if action_type is not None:
            # check for planner configuration, if there are preferred commands, use this
            if action_type.upper() == "IMPORT":
                execution_command = planner_configuration.get("ImportCommand", None)
            if action_type.upper() == "EXPORT":
                execution_command = planner_configuration.get("ExportCommand", None)
            
            # no configuration detected, use Transport Manager Tool logic
            if not execution_command:
                #no overwrite for the import/export commands
                command = self.prepareExecutionCommand(task_item, action_type, connection_name)
                if not command:
                    # there is no command available to run the process so just skip this and move on
                    self.processExecutionFinished()
                    return False
                
                if action_type.upper() == "IMPORT":
                    post_processing_commands = self.preparePostProcessingCommands(task_item, action_type, connection_name)
    
        command += execution_command + "\r\n"

        self.message.emit("Execution command ready.", "Transport Manager")
        
        if len(post_processing_commands) > 0:
            self.message.emit("Post processing commands ready.", "Transport Manager")

        post_script = ""
        always_run_post_script = self.application.getConfigurationValue("ExecutionPlannerSettings", "AlwaysRunPostScript")
        
        if always_run_post_script or len(self.task_queue) == 0:
            print("add post script", len(self.task_queue))
            post_script = self.application.getConfigurationValue("ExecutionPlannerSettings", "ExecutionPostScript") + "\r\n"

        self.start("powershell", 
        [variables_script, initializer_script, command, post_processing_commands, post_script], 
        mode=QIODeviceBase.OpenModeFlag.ReadWrite)

        return True

    def handleProcessStdErr(self):
        data = self.readAllStandardError()
        stderr = bytes(data).decode("cp1252")
        self.hasExecutionErrors = True
        continue_on_error = self.application.getConfigurationValue("ExecutionPlannerSettings", "IgnoreExecutionErrors")
       
        if not continue_on_error:
            self.stopExecutionPlanner()

        self.message.emit(stderr, "Error")

    def handleProcessStdOut(self):
        data = self.readAllStandardOutput()
        stdout = bytes(data).decode("cp1252")
        self.message.emit(stdout, "")

    def handleProcessState(self, state):
        states = {
            QProcess.ProcessState.NotRunning: 'Not running',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Running',
        }
        state_name = states[state]
        self.current_item.ExecutionState = state_name
        self.message.emit(f"State changed: {state_name}", "Transport Manager")

    def processExecutionFinished(self, exitCode=0, exitStatus=QProcess.ExitStatus.NormalExit):
        # print("Task Execution Finished", exitCode, exitStatus, self.hasExecutionErrors)
        end_time = timer()
        self.execution_time = timedelta(seconds=end_time - self.start_time)
        self.was_error = (exitCode != 0) or self.hasExecutionErrors
        self.message.emit("Task Execution Finished", "FINISHED")
        self.current_item.onTaskExecutionFinished(exitCode)
        self.is_running = False
        
        continue_on_error = self.application.getConfigurationValue("ExecutionPlannerSettings", "IgnoreExecutionErrors")

        if self.was_error and not continue_on_error:
            self.stopExecutionPlanner()

        if len(self.task_queue) > 0:
            self.continueExecutionQueue()
        
    def prepareProcessVariables(self, task_data):
        task_configuration = self.application.getConfigurationParameters("ExecutionPlanner_ExecutionTask")
        
        workdir = self.current_workdir
        variables_script = f"$WORKDIR='{workdir}'\r\n"

        if task_configuration:
            for column, column_confguration in task_configuration.items():
                column_value = task_data.get(column, None)

                # source_column = column_confguration.get("ValuePattern", None)
                # if source_column:
                #     # map column with source object attributes
                #     column_value = self.getSourceValue(column, source_column)

                if column_value:
                    if isinstance(column_value, list):
                        separator = column_confguration.get("Separator", ",")
                        column_value = separator.join(column_value).replace(separator, '", "')
                        variables_script += f'${column} = @("{column_value}")\r\n'
                        continue
                    column_value = str(column_value).strip()
                    variables_script += f"${column} = '{column_value}'\r\n"
        variables_script += "\r\n"
        return variables_script

    def preparePostProcessingCommands(self, task_item, action_type, connection_name):
        commands = []
        # only continue for the Import action types for now
        if action_type.upper() != "IMPORT":
            return ""
        
        connection_data = self.ConnectionHandler.connections.get(connection_name, None)
        if not connection_data:
            # connection data not available
            return ""

        task_name = task_item.display
        task_data = task_item.task_data()
        # print("auto update", task_data.get("AutoUpdate", False))
        run_auto_update = task_data.get("AutoUpdate", False)
        if run_auto_update:
            command = self.getAutoUpdateCommand(
                connection_data=connection_data)
            if command:
                self.message.emit(
                f"({task_name}) - adding AutoUpdate execution to the post processing commands.",
                "Transport Manager")
                commands.append(command)
        
        compiler_setting = task_data.get("CompilerOption", "None")
        if compiler_setting.upper() != "NONE":
            # some compiler options were provided
            command = self.getDBCompilerCommand(compiler_setting=compiler_setting, connection_data=connection_data)
            if command:
                self.message.emit(
                f"({task_name}) - adding compilation ({compiler_setting}) to the post processing commands.",
                "Transport Manager")
                commands.append(command)
        return "\r\n".join(commands)

    def prepareExecutionCommand(self, task_item, action_type, connection_name):
        #get the direct command the task execution
        # do not start additional session, just run the transport command directly
        command = ""
        task_name = task_item.display
        task_data = task_item.task_data()
        task_type = task_data.get("TaskType", None)
        
        if not task_type:
            self.message.emit(
            f"Task execution ({task_name}) cannot be started, Task type (attribute: TaskType) is not configured.",
            "Transport Manager")
            return False

        configuration_task_type = self.checkTaskType(task_type)
        is_transport = configuration_task_type == "Transport"
        is_schema_extension = configuration_task_type == "SchemaExtension"
        is_sql = configuration_task_type == "SQLScript"

        if not task_data.get("DefinitionFile", None) or not task_data.get("ExportFile", None):
            self.message.emit(
            f"Task execution ({task_name}) cannot be started, source/destination files are not configured.",
            "Transport Manager")
            return False

        connection_data = self.ConnectionHandler.connections.get(connection_name, None)
        export_file = task_data.get("ExportFile", None)
        definition_file = task_data.get("DefinitionFile", None)

        # Re-map the relative paths to absolute paths
        if definition_file:
            definition_file = "/".join([self.current_workdir, definition_file])

        if export_file:
            export_file = "/".join([self.current_workdir, export_file])
            #create required directories
            if action_type.upper() == "EXPORT":
                pathlib.Path(export_file).parent.mkdir(parents=True, exist_ok=True)

        if is_transport and connection_data:
            return self.getTransporterCommand(
                action_type=action_type, 
                export_file=export_file,
                definition_file=definition_file,
                connection_data=connection_data)
        
        if is_schema_extension and connection_data:
            return self.getSchemaExtensionCommand(
                action_type=action_type, 
                export_file=export_file,
                definition_file=definition_file,
                connection_data=connection_data)
        
        if is_sql and connection_data and action_type.upper() == "IMPORT":
            #run scripts
            self.sql_thread = SQLThread(
                    action_type=action_type,
                    definition_file=definition_file,
                    connection_data=connection_data,
                    target_function=self.runSQLScript,
                    call_back=self.processExecutionFinished)
            self.sql_thread.start()

            #returning False so there is no powershell subprocess started
            return False

        # task type is not supported, copy the files to target directory if this is an export task
        if action_type == "Export":
            self.message.emit(f"Task type was not handled with known configuration: Task Type: [{task_type}] Task Name: {task_name}. Source File will be copied over to export destination.", 
            "Transport Manager")
            self.copyDefinitionFile()

        return command

    def getTransporterCommand(self, action_type, export_file, definition_file, connection_data):
        tools_directory = connection_data.get("ToolsDirectory", None)
        connection_name = connection_data.get("ConnectionName", "")
        if not tools_directory:
            self.message.emit(
            f"Task execution cannot be started, tools directory is not configured for this connection ({connection_name})",
            "Transport Manager")
            return False
        command = None
        program = f'& "{tools_directory}\DBTransporterCmd.exe"'
        temp_db = DatabaseConnection(connection_data)
        conn_string = temp_db.get_connection_string()
        auth_string = temp_db.get_authentication_string()
        
        if action_type and action_type == "Export":
            command = f'{program} /File="{export_file}" /Template="{definition_file}" /Conn="{conn_string}" /Auth="{auth_string}"'
        
        if action_type and action_type == "Import":
            command = f'{program} /File="{export_file}" /Conn="{conn_string}" /Auth="{auth_string}"'
        return command

    def getSchemaExtensionCommand(self, action_type, definition_file, connection_data):
        tools_directory = connection_data.get("ToolsDirectory", None)
        connection_name = connection_data.get("ConnectionName", "")
        if not tools_directory:
            self.message.emit(
            f"Task execution cannot be started, tools directory is not configured for this connection ({connection_name})",
            "Transport Manager")
            return False
        command = None
        program = f'& "{tools_directory}\SchemaExtensionCmd.exe"'
        temp_db = DatabaseConnection(connection_data)
        conn_string = temp_db.get_connection_string()
        auth_string = temp_db.get_authentication_string()

        if action_type and action_type == "Import":
            command = f'{program} /Definition="{definition_file}" /Conn="{conn_string}" /Auth="{auth_string}"'
        return command

    def getDBCompilerCommand(self, compiler_setting, connection_data):
        tools_directory = connection_data.get("ToolsDirectory", None)
        connection_name = connection_data.get("ConnectionName", "")
        if not tools_directory:
            self.message.emit(
            f"Task execution cannot be started, tools directory is not configured for this connection ({connection_name})",
            "Transport Manager")
            return False
        
        command = ""
        program = f'& "{tools_directory}\DBCompilerCMD.exe"'
        temp_db = DatabaseConnection(connection_data)
        conn_string = temp_db.get_connection_string()
        auth_string = temp_db.get_authentication_string()
        command = f'{program} /Conn="{conn_string}" /Auth="{auth_string}"'
        
        if compiler_setting.upper() == "NOWEB":
            blacklist = f"CompileWebServices CompileApiProjects CompileHtmlApps CompileWebProjects"
            command = f'{program} -W /Conn="{conn_string}" /Auth="{auth_string}" /Blacklist={blacklist}'
        return command

    def getAutoUpdateCommand(self, connection_data):
        tools_directory = connection_data.get("ToolsDirectory", None)
        connection_name = connection_data.get("ConnectionName", "")
        if not tools_directory:
            self.message.emit(
            f"Task execution cannot be started, tools directory is not configured for this connection ({connection_name})",
            "Transport Manager")
            return False
        
        command = ""
        
        program = f'& "{tools_directory}\AutoUpdate.exe"'
        temp_db = DatabaseConnection(connection_data)
        conn_string = temp_db.get_connection_string()

        command = f'{program} /conn="{conn_string}" --install="{tools_directory}"'
        return command

    def copyDefinitionFile(self):
        task_data = self.current_item.task_data()
        export_file = task_data.get("ExportFile", None)
        definition_file = task_data.get("DefinitionFile", None)
        if definition_file and export_file and self.current_workdir:
            definition_path = pathlib.Path("/".join([self.current_workdir, definition_file]))
            export_path = pathlib.Path("/".join([self.current_workdir, export_file]))
            export_path.parent.mkdir(parents=True, exist_ok=True)
            if definition_path.is_file():
                #copy only if the source file exists
                self.message.emit(
                f"Copy {str(definition_path)} to {str(export_path)}.",
                "Transport Manager")
                shutil.copy(definition_path, export_path)

    def runSQLScript(self, action_type, definition_file, connection_data):
        self.stateChanged.emit(QProcess.ProcessState.Running)
        # print("Running SQL Script")
        if action_type != "Import":
            return False
        sql_script = ""
        if definition_file:
            definition_path = pathlib.Path(definition_file)
            if definition_path.is_file():
                sql_script = self.application.load_file(definition_file)

        if len(sql_script.strip()) == 0:
            self.message.emit(
            f"SQL Script could not be loaded or have no content ({definition_file}). Operation cancelled.",
            "Transport Manager")
            return False

        connection = DatabaseConnection(connection_data)
        if connection.connect_db():
            # run script if connected
            self.message.emit(
            "Starting SQL Script.",
            "Transport Manager")
            response = connection.run_db_query(sql_script)
            response_data = []
            for row in response:
                row_to_list = [str(elem) for elem in row]
                response_data.append("\t".join(row_to_list))
            self.message.emit(
            "\n".join(response_data),
            "SQL Script Result")
        return False

class SQLThread(QThread):
    def __init__(self, action_type, definition_file, connection_data, target_function, call_back):
        super(SQLThread, self).__init__()
        self.target_function = target_function
        self.definition_file = definition_file
        self.connection_data = connection_data
        self.action_type = action_type

        if call_back:
            self.finished.connect(call_back)

    def run(self, *args, **kwargs):
        self.target_function(self.action_type, self.definition_file, self.connection_data)

    