    
from PyQt6.QtCore import QProcess, pyqtSignal, QIODeviceBase

class ProcessRunner(QProcess):
    message = pyqtSignal(str, str)
    taskStatusChanged = pyqtSignal(object, str)
    taskCompleted = pyqtSignal(object)

    def __init__(self, planner_widget):
        super().__init__()
        self.planner_widget = planner_widget
        self.application = self.planner_widget.application
        self.object_configuration = self.application.object_configuration
        self.readyReadStandardOutput.connect(self.handle_stdout)
        self.readyReadStandardError.connect(self.handle_stderr)
        self.finished.connect(self.process_finished)
        self.stateChanged.connect(self.handle_state)
        
        self.is_running = False
        self.current_item = None
        self.task_queue = []

    def stop_planner_execution(self):
        self.task_queue = []
        self.kill()

    def execute_planner_tasks(self, task_items):
        for task_item in task_items:
            task_data = task_item.task_data
            print("execute stuff here:", task_data)
            self.start_process(task_item)

    def load_file(self, file_path):
        file_content = ""
        with open(file_path, 'r') as f:
            file_content = f.read()
        return file_content

    def start_process(self, task_item, queued_task=False):
        task_name = task_item.task_data.get("TaskName", None)
        
        if self.state() == QProcess.ProcessState.Running:
            if task_item.task_class in ["ExecutionPlanner_ExecutionTask", "PackageManager_TaskDefinition"]:
                self.task_queue.append(task_item)
                
                self.message.emit(f"Adding task to the execution queue.. ({task_name})", "Transport Manager")
                return True
            return False
        
        action_type = task_item.task_data.get("ExecutionType", None)
        connection = task_item.task_data.get("Connection", None)

        if queued_task and len(self.task_queue) > 0:
            self.task_queue.remove(self.task_queue[0])

        self.message.emit(
            f"Starting task execution ({task_name}). Action: [{action_type}]. Connection: [{connection}]",
            "Transport Manager")
        task_configuration = self.object_configuration.get("ExecutionPlanner_ExecutionTask")
        
        self.current_item = task_item
        workdir = self.application.current_workdir
        variables_script = f"$WORKDIR='{workdir}'\r\n"

        if task_configuration:
            for column, column_confguration in task_configuration.items():
                column_value = task_item.task_data.get(column, None)

                source_column = column_confguration.get("Source", None)
                if source_column:
                    # map column with source object attributes
                    column_value = self.get_source_value(column, source_column)

                if column_value:
                    if isinstance(column_value, list):
                        separator = column_confguration.get("Separator", ",")
                        column_value = separator.join(column_value).replace(separator, '", "')
                        variables_script += f'${column} = @("{column_value}")\r\n'
                        continue
                    column_value = column_value.strip()
                    variables_script += f"${column} = '{column_value}'\r\n"

        variables_script += "\r\n"

        self.message.emit(f" variables set: {variables_script}", "Transport Manager")
        
        configuration = self.application.settings.value("ExecutionPlannerSettings")
        initializer_script = configuration.get("ExecutionPreScript", "") + "\r\n"

        command = ""
        execution_command = ""
        
        if action_type is not None:
            if action_type.upper() == "IMPORT":
                execution_command = configuration.get("ImportCommand", "")
        
            if action_type.upper() == "EXPORT":
                execution_command = configuration.get("ExportCommand", "")

        command += execution_command + "\r\n"

        self.start("powershell", 
        [variables_script, initializer_script, command], 
        mode=QIODeviceBase.OpenModeFlag.ReadWrite)

        return True

    def get_source_value(self, column, source_column):
        # map column with source object attributes
        source_value = self.current_item.task_data.get(source_column, None)
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

    def handle_stderr(self):
        data = self.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message.emit(stderr, "Error")

    def handle_stdout(self):
        data = self.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message.emit(stdout, "")

    def handle_state(self, state):
        states = {
            QProcess.ProcessState.NotRunning: 'Not running',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Running',
        }
        state_name = states[state]
        self.current_item.setData("task_execution_status", state_name)
        self.message.emit(f"State changed: {state_name}", "Transport Manager")

    def process_finished(self):
        self.message.emit("Process finished.", "Transport Manager")
        self.current_item.setData("task_execution_status", "Finished")
        self.is_running = False
        if len(self.task_queue) > 0:
            self.start_process(self.task_queue[0], queued_task=True)