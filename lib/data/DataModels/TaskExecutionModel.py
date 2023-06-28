from . import JSONDataItem, JSONDataModel
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData
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
    def __init__(self, application, task_class="ExecutionPlanner_ExecutionTask", task_data=None, parent=None, model_reference=None):
        super().__init__(
            application=application,
            parent=parent, 
            task_class=task_class, 
            task_data=task_data,
            model_reference=model_reference
            )
        self._package_definition_data = {}
        self.migrate(task_class)
        #Configure Default Value
        if task_data: 
            if not task_data.get("ExecutionType", None):
                self.setData("ExecutionType", "Export")

    def itemDataDropped(self, source_dict):
        # print("foreign object dropped into task execution view", source_dict.get("objectclass", None), self.task_class)
        source_object_class = source_dict.get("objectclass", None)
        if source_object_class == "PackageManager_PackageDefinition":
            # print("package definition dropped, update child items")
            for child_task in self.children():
                child_task.package_definition = source_dict
        
        if source_object_class == "PackageManager_TaskDefinition":
            # print("task definition dropped, update this item with parent data only")
            parent_object = source_dict.get("parent", None)
            if parent_object:
                self.package_definition = parent_object


    def itemLocationChanged(self, source_item):
        print("execution planner item moved")
        #pass the package definition over to new item
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

        # print("migrate source class object to execution planner object", source_class)
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