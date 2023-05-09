from . import JSONDataItem, JSONDataModel
from copy import deepcopy

class PackageDefinitionModel(JSONDataModel):
    def __init__(self, data, parent=None):
        super().__init__(parent=parent, data=data, model_item_class=PackageDefinitionItem)
        self.headers = ["Actions"]
        

class PackageDefinitionItem(JSONDataItem):
    def __init__(self, task_class="PackageDefinition", task_data=None, parent=None):
        super().__init__(parent=parent, task_class=task_class, task_data=task_data)
        
        if task_data is not None and self.data("Description") is None:
            self.setData("Description", "")

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
        task_data = deepcopy(self._task_data)
        task_data['uid'] = self.uid
        task_data['objectclass'] = self.task_class
        task_data['row'] = self.row()
        if self.parent().task_class == "PackageDefinition":
            task_data['FeatureName'] = self.parent().data("FeatureName")
    
        return task_data

    @property
    def edit_data(self):
        return self._task_data

    def update_data(self, dict_data):
        for key, value in dict_data.items():
            self.setData(key, value)
        self.data_changed.emit(self)

    @property
    def export_data(self):
        if self._task_data is None:
            return self._task_data
        export_data = deepcopy(self._task_data)
        if self.task_class == "PackageDefinition":
            children = []
            for i in range(self.childCount()):
                child_item = self.child(i)
                child_data = child_item.export_data
                children.append(child_data)
            
            export_data["Tasks"] = children
        return export_data