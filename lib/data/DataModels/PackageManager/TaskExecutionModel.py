from . import JSONDataItem, JSONDataModel
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData, pyqtSignal
import json

class TaskExecutionModel(JSONDataModel):
    def __init__(self, application, data, parent_widget=None):
        super().__init__(
            application=application,
            parent_widget=parent_widget, 
            data=data, 
            model_item_class=TaskExecutionItem
            )

        self.headers = ["Actions"]
        
    def addExecutionGroup(self, task_data, parentIndex):
        parent_item = self.rootItem
        if parentIndex.isValid():
            parent_item = parentIndex.internalPointer()

        new_item = TaskExecutionItem(
            application=self.application,
            task_class="ExecutionPlanner_ExecutionGroup", 
            task_data=task_data, 
            parent=parent_item,
            model_reference=self
            )
        self.insert_items(parentIndex, [new_item])
    
    def mimeTypes(self):
        return ["application/vnd.jsondataitem", "application/vnd.ExecutionPlannerItem"]

    def mimeData(self, indexes):
        mimedata = QMimeData()
        items_data = []
        for index in indexes:
            if index.isValid():
                item = index.internalPointer()
                export = item.task_data()
                if export not in items_data:
                    items_data.append(export)
        
        items_data_sorted = sorted(
                            items_data, 
                            key=lambda d: (d['row'])
                            )
        # print(items_data_sorted)
        jsondata = json.dumps(items_data_sorted, indent=4)
        encodedJson = jsondata.encode('utf-8')

        mimedata.setData("application/vnd.ExecutionPlannerItem", encodedJson)
        # mimedata.setData("application/vnd.jsondataitem", encodedJson)
        return mimedata

    def dropMimeData(self, data, action, row, column, parentIndex):
        if (not data.hasFormat("application/vnd.jsondataitem") 
            and not data.hasFormat("application/vnd.ExecutionPlannerItem")):
            return False

        if data.hasFormat("application/vnd.ExecutionPlannerItem"):
            encodedJson = data.data("application/vnd.ExecutionPlannerItem")
            data.setData("application/vnd.jsondataitem", encodedJson)
        
        return super().dropMimeData(data, action, row, column, parentIndex)

class TaskExecutionItem(JSONDataItem):
    # executionStateChanged = pyqtSignal(bool, bool, bool)
    executionStateChanged = pyqtSignal(str)

    def __init__(self, application, task_class="ExecutionPlanner_ExecutionTask", task_data=None, parent=None, model_reference=None):
        super().__init__(
            application=application,
            parent=parent, 
            task_class=task_class, 
            task_data=task_data,
            model_reference=model_reference
            )
        self._package_definition_data = {}
        self.definition_file_path = None
        #Configure Default Value
        if task_data: 
            source_files_data = task_data.get("source_file_data", {})

            if source_files_data:
                for column, value in source_files_data.items():
                    self.setData(column, value)
            
            parent_data = task_data.get("PARENT_DEF", None)
            if parent_data:
                # print("parent data found", parent_data)
                self.package_definition = parent_data
            if not task_data.get("ExecutionType", None):
                self.setData("ExecutionType", "Export")
        self.migrate(task_class)
        self.initializeObjectData()


    def itemDataDropped(self, source_dict):
        if source_dict.get("children", None):
            for child_task in self.children():
                # child_task.setData("PARENT_DEF", source_dict)
                child_task.package_definition = source_dict

    def itemLocationChanged(self, source_item):
        print("execution planner item moved")
        #pass the package definition over to new item
        super().itemLocationChanged(source_item)
        self.package_definition = source_item.package_definition

    @property
    def package_definition(self):
        return self._package_definition_data

    @package_definition.setter
    def package_definition(self, value):
        self._package_definition_data = value

    def migrate(self, source_class):
        if source_class in ["ExecutionPlanner_ExecutionTask", "ExecutionPlanner_ExecutionGroup"]:
            return False
            
        source_display = self.display
        source_description = self.description
        
        if source_class == "JSONDataItem":
            self.task_class = "ExecutionPlanner_ExecutionTask"

        if source_class == "PackageManager_PackageDefinition":
            self.task_class = "ExecutionPlanner_ExecutionGroup"
            
        if source_class == "PackageManager_TaskDefinition":
            self.task_class = "ExecutionPlanner_ExecutionTask"

        self.display = source_display
        self.description = source_description

    def initializeObjectData(self):
        application_connections = self.application.ConnectionHandler.connections
        # if self.data("Connection"):
        if self.task_class == "ExecutionPlanner_ExecutionTask" and self.data("Connection") is None and len(application_connections.keys()):
            #TODO: add connection preference for the initial task setup
            self.setData("Connection", list(application_connections.keys())[0])

    @property
    def Connection(self):
        return self.task_data().get("Connection", None)

    @property
    def TaskType(self):
        return self.task_data().get("TaskType", None)

    @property
    def CompilerOption(self):
        return self.task_data().get("CompilerOption", None)

    @property
    def AutoUpdate(self):
        return self.task_data().get("AutoUpdate", None)

    @property
    def ExecutionType(self):
        return self.task_data().get("ExecutionType", None)

    @property
    def ExecutionState(self):
        return self.task_data().get("ExecutionState", None)
        
    @ExecutionState.setter
    def ExecutionState(self, state):
        self.setData("ExecutionState", state)
        self.executionStateChanged.emit(state)
        if self.parent():
            self.parent().ExecutionState = state

    def onTaskExecutionFinished(self, exitCode):
        print("handle execution exitCode status", exitCode)
        if exitCode == 1:
            self.ExecutionState = "Finished with Errors"
        if exitCode == 0:
            self.ExecutionState = "Finished"
        if exitCode == 62097:
            self.ExecutionState = "Terminated"
