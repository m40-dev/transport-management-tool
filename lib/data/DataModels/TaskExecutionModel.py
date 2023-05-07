from . import JSONDataItem, JSONDataModel

class TaskExecutionModel(JSONDataModel):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent, data=data, model_item_class=TaskExecutionItem)
        self.headers = ["Actions"]
        
    def addExecutionGroup(self, task_data, parentIndex):
        parent_item = self.rootItem
        if parentIndex.isValid():
            parent_item = parentIndex.internalPointer()

        new_item = TaskExecutionItem(task_data=task_data, parent=parent_item)
        self.insert_items(parentIndex, [new_item])


class TaskExecutionItem(JSONDataItem):
    def __init__(self, task_class="TaskGroup", task_data=None, parent=None):
        super().__init__(parent=parent, task_class=task_class, task_data=task_data)

        if task_data:
            child_tasks = task_data.get("Tasks", None)
            # # Alternate keyword for child items
            # children = task_data.get("children", None)
                
            # if not child_tasks and children:
            #     child_tasks = children

            if child_tasks:
                self.loadChildren(child_tasks)

    def loadChildren(self, child_tasks):
        if child_tasks:
            for task_object in child_tasks:
                task_class = task_object.get("objectclass", "TaskItem")
                # if not task_class:
                #     print("Mandatory task object attribute missing: objectclass")
                #     continue

                task_item = TaskExecutionItem(task_class, task_object, parent=self)
                self.addChild(task_item)

    @property
    def task_data(self):
        if self._task_data is None:
            return self._task_data

        children = []

        for i in range(self.childCount()):
            child_item = self.child(i)
            child_data = child_item.task_data
            children.append(child_data)

        # self._task_data['children'] = children
        self._task_data['Tasks'] = children
        self._task_data['uid'] = self.uid
        self._task_data['objectclass'] = self.task_class
        self._task_data['row'] = self.row()
    
        return(self._task_data)