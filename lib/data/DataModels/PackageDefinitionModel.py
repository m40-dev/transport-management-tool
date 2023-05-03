from . import JSONDataItem, JSONDataModel

class PackageDefinitionModel(JSONDataModel):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent, data=data, model_item_class=PackageDefinitionItem)
        self.headers = ["Actions"]
        

class PackageDefinitionItem(JSONDataItem):
    def __init__(self, task_class="PackageDefinition", task_data=None, parent=None):
        super().__init__(parent=parent, task_class=task_class, task_data=task_data)

        if task_data:
            child_tasks = task_data.get("Tasks", None)

            if child_tasks:
                self.task_class = "PackageDefinition"
                self.loadChildren(child_tasks)

    def loadChildren(self, child_tasks):
        if child_tasks:
            for task_object in child_tasks:
                task_class = task_object.get("objectclass", "TaskItem")

                task_item = PackageDefinitionItem(task_class, task_object, parent=self)
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
        self._task_data['uid'] = self.uid
        self._task_data['objectclass'] = self.task_class
        self._task_data['row'] = self.row()
        if self.parent().task_class == "PackageDefinition":
            self._task_data['FeatureName'] = self.parent().data("FeatureName")
    
        return(self._task_data)