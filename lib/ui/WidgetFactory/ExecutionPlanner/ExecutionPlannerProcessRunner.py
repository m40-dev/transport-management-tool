    
from PyQt6.QtCore import QProcess, pyqtSignal, QIODeviceBase

class ProcessRunner(QProcess):
    message = pyqtSignal(str, str)
    taskStatusChanged = pyqtSignal(object, str)
    taskCompleted = pyqtSignal(object)

    def __init__(self, planner_widget):
        super().__init__()
        self.planner_widget = planner_widget
        self.application = self.planner_widget.application
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
        action_type = task_item.task_data.get("ExecutionType", None)
        connection = task_item.task_data.get("Connection", None)

        if queued_task and len(self.task_queue) > 0:
            self.task_queue.remove(self.task_queue[0])
        
        if self.state() == QProcess.ProcessState.Running:
            if task_item.task_class == "TaskItem":
                self.task_queue.append(task_item)
                
                self.message.emit(f"Adding task to the execution queue.. ({task_name})", "Transport Manager")
                return True
            return False

        self.message.emit(f"Starting task execution ({task_name}). Action: [{action_type}]. Connection: [{connection}]", "Transport Manager")

        self.current_item = task_item
        workdir = self.application.current_workdir
        variables_script = f"$WORKDIR='{workdir}'\r\n"
        for param_name, param_value in task_item.task_data.items():
            variables_script += f"${param_name} = '{param_value}'\r\n"
        variables_script += "\r\n"

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