from . import JSONDataItem, JSONDataModel,pyqtSignal
from copy import deepcopy

class PackageDefinitionModel(JSONDataModel):

    def __init__(self, application, data, parent_widget=None):
        super().__init__(
            application=application,
            parent_widget=parent_widget, 
            data=data, 
            model_item_class=PackageDefinitionItem
            )
        self.headers = ["Actions"]
        

class PackageDefinitionItem(JSONDataItem):
    def __init__(self, application, task_class="PackageManager_PackageDefinition", task_data=None, parent=None, model_reference=None):
        super().__init__(
            application=application,
            parent=parent, 
            task_class=task_class, 
            task_data=task_data,
            model_reference=model_reference)
        
        # if task_data is not None and self.data("Description") is None:
        #     self.setData("Description", "")
        
        if task_class is None:
            self._task_class = "PackageManager_PackageDefinition"

        if task_data:
            child_tasks = task_data.get("children", None)
            if not child_tasks:
                #TODO: get child task column from the object configuration
                child_tasks = task_data.get("Tasks", None)
                if child_tasks:
                    # self._task_class = "PackageManager_PackageDefinition"
                    self.loadChildren(child_tasks)

    def loadChildren(self, child_tasks):
        if child_tasks:
            for task_object in child_tasks:
                task_class = task_object.get("objectclass", "PackageManager_TaskDefinition")

                task_item = PackageDefinitionItem(
                    application=self.application, 
                    task_class=task_class, 
                    task_data=task_object, 
                    parent=self,
                    model_reference=self.model_reference)
                self.addChild(task_item)

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
    #     task_data = deepcopy(self._task_data)
    #     task_data['uid'] = self.uid
    #     task_data['objectclass'] = self.task_class
    #     task_data['row'] = self.row()
    #     if self.parent().task_class == "PackageManager_PackageDefinition":
    #         task_data['FeatureName'] = self.parent().data("FeatureName")
    
    #     return task_data

    # @property
    # def export_data(self):
    #     if self._task_data is None:
    #         return self._task_data

    #     export_data = deepcopy(self._task_data)
    #     if self.task_class == "PackageDefinition":
    #         children = []
    #         for i in range(self.childCount()):
    #             child_item = self.child(i)
    #             child_data = child_item.export_data
    #             children.append(child_data)
            
    #         export_data["Tasks"] = children
    #     return export_data

    @property
    def export_data(self):
        if self._task_data is None:
            return self._task_data
        
        configuration = self.object_definitions.get(self.task_class)
        
        export_data = {}
        
        if configuration is None:
            return export_data

        for field, field_configuration in configuration.items():
            is_for_export = field_configuration.get("IsForDataExport", "True") == "True"
            if not is_for_export:
                continue
            
            export_data[field] = self._task_data.get(field, "")

            field_type = field_configuration.get("FieldType", None)
            field_role = field_configuration.get("FieldRole", None)
            min_value = field_configuration.get("MinValue", 1)

            if field_role and field_role == "SortOrder":
                export_data[field] = self.row() + min_value

            if field_type and field_type == "ChildObjectReference":
                child_class = field_configuration.get("Class", None)
                children = []
                for i in range(self.childCount()):
                    child_item = self.child(i)
                    if child_item.task_class == child_class:
                        child_data = child_item.export_data
                        children.append(child_data)
                export_data[field] = children
        return export_data
    
