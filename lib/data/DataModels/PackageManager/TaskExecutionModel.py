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
                            key=lambda d: (d.get('row', ''))
                            )
        # print(items_data_sorted)
        jsondata = json.dumps(items_data_sorted, indent=4)
        encodedJson = jsondata.encode('utf-8')

        mimedata.setData("application/vnd.ExecutionPlannerItem", encodedJson)
        # mimedata.setData("application/vnd.jsondataitem", encodedJson)
        return mimedata

    def dropMimeData(self, data, action, row, column, parentIndex):
        migrate = True
        if (not data.hasFormat("application/vnd.jsondataitem") 
            and not data.hasFormat("application/vnd.ExecutionPlannerItem")):
            return False
        
        if data.hasFormat("application/vnd.ExecutionPlannerItem"):
            encodedJson = data.data("application/vnd.ExecutionPlannerItem")            
            data.setData("application/vnd.jsondataitem", encodedJson)
            migrate = False
        
        if data.hasFormat("application/vnd.jsondataitem") and migrate:
            encodedJson = data.data("application/vnd.jsondataitem") 
            decodedData = bytes(encodedJson)
            jsondata = json.loads(decodedData)
            for dropped_item in jsondata:
                self.migrate(source_dict=dropped_item)
            jsondata = json.dumps(jsondata, indent=4)
            encodedJson = jsondata.encode('utf-8')
            data.setData("application/vnd.jsondataitem", encodedJson)
        
        return super().dropMimeData(data, action, row, column, parentIndex)

    def migrate(self, source_dict):
        source_object_class = source_dict.get("objectclass", "JSONDataItem")
        if source_object_class in ["ExecutionPlanner_ExecutionTask", "ExecutionPlanner_ExecutionGroup"]:
            #nothing to migrate
            return source_dict
        
        target_object_class = source_object_class
        if source_object_class == "JSONDataItem":
            target_object_class = "ExecutionPlanner_ExecutionTask"

        if source_object_class == "PackageManager_PackageDefinition":
            target_object_class = "ExecutionPlanner_ExecutionGroup"
            
        if source_object_class == "PackageManager_TaskDefinition":
            target_object_class = "ExecutionPlanner_ExecutionTask"
        
        # map to target object class
        source_dict["objectclass"] = target_object_class

        #map source attributes by standard roles
        source_display_attributes = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_role(source_object_class, "DisplayRole")
        source_description_attributes = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_role(source_object_class, "DescriptionRole")
        # print(f"source object configuration - display columns: {source_display_attributes.keys()}, description columns: {source_description_attributes.keys()}")

        target_display_attributes = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_role(target_object_class, "DisplayRole")
        target_description_attributes = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_role(target_object_class, "DescriptionRole")
        # print(f"target object configuration - display columns: {target_display_attributes.keys()}, description columns: {target_description_attributes.keys()}")
        

        data_dict = self.mapSourceObjectAttributes(
            source_dict=source_dict,
            source_columns=source_display_attributes,
            target_columns=target_display_attributes)

        source_dict.update(data_dict)

        data_dict = self.mapSourceObjectAttributes(
            source_dict=source_dict,
            source_columns=source_description_attributes,
            target_columns=target_description_attributes)

        source_dict.update(data_dict)
        return source_dict
    
    def mapSourceObjectAttributes(self, source_dict, source_columns, target_columns):
        i = 0
        data_dict = {}
        for source_display_column in source_columns.keys():
            #for each target display column
            if source_display_column in target_columns.keys():
                # print(f"Map source display column {source_display_column} with exact target attribute")
                data_dict[source_display_column] = source_dict.get(source_display_column, "")
                i += 1
                continue

            #no direct mapping but something still remains
            if i < len(target_columns.keys()):
                target_display_column = list(target_columns.keys())[i]
                # print(f"Map source display column {source_display_column} with target attribute: {target_display_column}")
                data_dict[target_display_column] = source_dict.get(source_display_column, "")
                i += 1
                continue

            data_dict[source_display_column] = source_dict.get(source_display_column, "")
            i += 1
            # print(f"still something left here, more source columns than target options? map directly", source_display_column)
        return data_dict


class TaskExecutionItem(JSONDataItem):
    # executionStateChanged = pyqtSignal(bool, bool, bool)
    executionStateChanged = pyqtSignal(str)
    logExecutionState = pyqtSignal(str)

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
        self.execution_log = []

        #Configure Default Value
        if task_data: 
            source_files_data = task_data.get("source_file_data", {})

            if source_files_data:
                for column, value in source_files_data.items():
                    self.setData(column, value)
            
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
        # print("execution planner item moved")
        #pass the package definition over to new item
        super().itemLocationChanged(source_item)
        self.package_definition = source_item.package_definition
        self.execution_log = source_item.execution_log

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
        # print("handle execution exitCode status", exitCode)
        if exitCode == 1:
            self.ExecutionState = "Finished with Errors"
        if exitCode == 0:
            self.ExecutionState = "Finished"
        if exitCode == 62097:
            self.ExecutionState = "Terminated"
        print(len(self.execution_log))