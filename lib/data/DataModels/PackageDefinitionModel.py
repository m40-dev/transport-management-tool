from . import JSONDataItem, JSONDataModel,pyqtSignal
from copy import deepcopy
from pathlib import Path

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
        
        if task_class is None:
            self.task_class = "PackageManager_PackageDefinition"

        self.object_definitions = application.object_definitions
        
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

    def update_data(self, data):
        if self.task_class == "PackageManager_PackageDefinition":
            print("update package definition")
            new_location = data.get("DefinitionFile", "")
            if self._task_data.get("DefinitionFile", "") != new_location:
                print("Definition location changed, new location", new_location)
                workdir_path = Path(self.application.current_workdir).absolute()
                file_path = Path(self.application.current_workdir + "/" + new_location)
                if file_path.is_file:
                    feature_definition_location = file_path.parent.relative_to(workdir_path)
                    task_definitions_location = str(feature_definition_location) +  "/Export"
                    print(f"location attributes: ExportFilesLocation:{task_definitions_location} DefinitionDirectory:{feature_definition_location} DefinitionFile: {new_location}")
                    self._task_data["ExportFilesLocation"] = task_definitions_location
                    self._task_data["DefinitionDirectory"] = str(feature_definition_location)

        super().update_data(data)