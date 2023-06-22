from . import JSONDataItem, JSONDataModel, pyqtSignal
from copy import deepcopy
from pathlib import Path
import json

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


    def itemLocationChanged(self, source_item):
        # handle the package definition objects relocation
        # relocation handling works purely on the fact that structure can have max 2 levels: Package as parent and Task as child item
        if source_item.parent() != self.parent() and self.task_class == "PackageManager_TaskDefinition":
            #handle file relocation for the task definition items
            # print("workdir location:", self.application.current_workdir)
            definition_file = self.data("DefinitionFile")
            self.moveDefinitionFile(
                source_path = source_item.parent().data("ExportFilesLocation"), 
                destination_path = self.parent().data("ExportFilesLocation"), 
                file_name = definition_file)

            # source_file_path = "/".join([self.application.current_workdir, source_item.parent().data("ExportFilesLocation"), definition_file])
            # destination_file_path = "/".join([self.application.current_workdir, self.parent().data("ExportFilesLocation"), definition_file])
            # source_path = Path(source_file_path)
            # destination_path = Path(destination_file_path)
            # # print("source location:", source_path, "exists:", source_path.is_file())
            # # print("target location:", destination_path, "exists:", destination_path.is_file())
            # destination_path.parent.mkdir(parents=True, exist_ok=True)
            # destination_path = source_path.replace(destination_path)
    
    def moveDefinitionFile(self, source_path, destination_path, file_name=""):
        source_file_path = "/".join([self.application.current_workdir, source_path, file_name])
        destination_file_path = "/".join([self.application.current_workdir, destination_path, file_name])


        source_path = Path(source_file_path)
        if not source_path.is_file():
            # source file not found
            print("source file not found:", source_path)
            return False
        
        destination_path = Path(destination_file_path)

        # print("source location:", source_path, "exists:", source_path.is_file())
        # print("target location:", destination_path, "exists:", destination_path.is_file())

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path = source_path.replace(destination_path)
            

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
            # print("update package definition")
            new_location = data.get("DefinitionFile", "")
            old_location = self._task_data.get("DefinitionFile", "")
            if old_location != new_location:
                print("Definition location changed to new location", new_location)
                workdir_path = Path(self.application.current_workdir).absolute()
                new_file_path = Path(self.application.current_workdir + "/" + new_location)
                old_file_path = Path(self.application.current_workdir + "/" + old_location)

                old_export_directory = self._task_data["ExportFilesLocation"]
                new_feature_definition_location = new_file_path.parent.relative_to(workdir_path)
                new_export_directory = str(new_feature_definition_location) +  "/Export"

                print("file exists status. source file", old_file_path.is_file(), "target file", new_file_path.is_file())

                # try to move the definition file
                if old_file_path.is_file():
                    self.moveDefinitionFile(old_location, new_location)

                # update location data
                self._task_data["ExportFilesLocation"] = new_export_directory
                self._task_data["DefinitionDirectory"] = str(new_feature_definition_location)

                # move task definition files
                if new_export_directory and new_export_directory != old_export_directory:
                    print(f"move all tasks from {old_export_directory} to {new_export_directory}")
                    for task_definition_item in self.children():
                        task_definition_item.moveDefinitionFile(old_export_directory, new_export_directory, task_definition_item.data("DefinitionFile"))


        super().update_data(data)

    def save(self):
        if self.task_class != "PackageManager_PackageDefinition":
            super().save()
            return False

        export = self.export_data
        if "ExportFilesLocation" in export.keys():
            export.pop("ExportFilesLocation")
        if "DefinitionDirectory" in export.keys():
            export.pop("DefinitionDirectory")
        if "DefinitionFile" in export.keys():
            export.pop("DefinitionFile")

        export_data = json.dumps(export, indent=4, separators=(',',':'))
        # print("Export Data" , export_data)

        definition_file = self.data("DefinitionFile")

        if definition_file and self.application.current_workdir:
            export_file = f"{self.application.current_workdir}/{definition_file}"
            print(f"PD: export {self.display} to: ", export_file)
            Path(export_file).parent.mkdir(parents=True, exist_ok=True)
            with open(export_file, 'w') as doc:
                doc.write(export_data)
            super().save()