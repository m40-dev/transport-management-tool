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
                export = item.task_data
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

        self.migrate(task_class)

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

    # def loadChildren(self, child_tasks):
    #     if child_tasks:
    #         for task_object in child_tasks:
    #             task_class = task_object.get("objectclass", "TaskItem")
    #             # if not task_class:
    #             #     print("Mandatory task object attribute missing: objectclass")
    #             #     continue

    #             task_item = TaskExecutionItem(task_class, task_object, parent=self)
    #             self.addChild(task_item)

    # @property
    # def task_data(self):
    #     if self._task_data is None:
    #         return self._task_data

    #     children = []

    #     for i in range(self.childCount()):
    #         child_item = self.child(i)
    #         child_data = child_item.task_data
    #         children.append(child_data)

    #     # self._task_data['children'] = children
    #     self._task_data['Tasks'] = children
    #     self._task_data['uid'] = self.uid
    #     self._task_data['objectclass'] = self.task_class
    #     self._task_data['row'] = self.row()
    
    #     return(self._task_data)