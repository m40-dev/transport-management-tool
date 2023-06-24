from . import JSONDataItem, JSONDataModel, pyqtSignal
from copy import deepcopy
from pathlib import Path
import json
import os

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
    objectFileLocationChanged = pyqtSignal(Path, Path, str)

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
        self.objectFileLocationChanged.connect(self.fileLocationChangeHandler)

        # object_configuration = self.object_definitions.get(self.task_class)
        if self.parent():
            self.parent().objectFileLocationChanged.connect(self.parentDefinitionChanged)

        if task_data:
            # children object handling
            child_tasks = task_data.get("children", None)
            if not child_tasks:
                #TODO: get child task column from the object configuration
                child_tasks = task_data.get("Tasks", None)
                if child_tasks:
                    # self._task_class = "PackageManager_PackageDefinition"
                    self.loadChildren(child_tasks)

    def fileLocationChangeHandler(self, source_path, target_path, file_column):
        self.moveFile(source_path, target_path)

    def parentDefinitionChanged(self, source_file, target_file, file_column):
        print(self.display, "parent definition moved", self.parent().display, "from", source_file, "to", target_file, "affected column", file_column)
        if self.application.current_workdir:
            # print("old definition file directory", source_file.parent, self.get_file_path())
            # print("new definition file directory", target_file.parent, self.get_file_path())
            parent_directory = str(target_file.parent)
            if file_column == "DefinitionFile":
                # parent definition location changed, move relevant task files
                object_configuration = self.object_definitions.get(self.task_class)
                if object_configuration and self.parent():
                    for column, column_configuration in object_configuration.items():
                        if (column_configuration.get("FileSelectionMode", None) == "FileName"):
                            self.moveTaskFile(new_parent_directory=parent_directory, file_column=column)
    
    def moveTaskFile(self, new_parent_directory, file_column="DefinitionFile"):
        # print("move task file", file_column, new_parent_directory)
        file_name = self.data(file_column)
        if not file_name:
            #file name not in data, there is nothing to do
            return False
        # print("move task file:", file_name, "column", file_column)
        object_configuration = self.object_definitions.get(self.task_class)
        if object_configuration:
            definition_config = object_configuration.get(file_column, None)
            if definition_config:
                if (definition_config.get("FileSelectionMode", None) == "FileName" and 
                    definition_config.get("RedirectDirectoryRelativeTo", "").lower() == "parent"):
                    #making sure that we meet the relocation criteria
                    source_file = self.get_file_path(file_column=file_column)
                    target_file = Path("/".join([new_parent_directory, file_name]))

                    redirect_folder = definition_config.get("RedirectDirectoryStatic", None)
                    if redirect_folder:
                        target_file = Path("/".join([new_parent_directory, redirect_folder, file_name]))
                    self.moveFile(source_file, target_file)

    def get_file_path(self, file_location=None, file_column="DefinitionFile"):
        if not file_location:
            file_location = self.data(file_column)
        object_configuration = self.object_definitions.get(self.task_class)
        if object_configuration:
            definition_file_configuration = object_configuration.get(file_column, None)
            if definition_file_configuration:
                if definition_file_configuration.get("FileSelectionMode", "") == "Relative":
                    file_path = Path(os.sep.join([self.application.current_workdir, file_location]))
                    return file_path

                if definition_file_configuration.get("FileSelectionMode", "") == "Absolute":
                    file_path = Path(file_location)
                    return file_path

                if definition_file_configuration.get("FileSelectionMode", "") == "FileName":
                    file_path = Path(os.sep.join([self.application.current_workdir, file_location]))
                    redirection_path = definition_file_configuration.get("RedirectDirectoryStatic", None)
                    if redirection_path:
                        # Redirect File To different Directory
                        file_path = Path(os.sep.join([self.application.current_workdir, str(redirection_path), file_location]))
                        redirection_relative_to = definition_file_configuration.get("RedirectDirectoryRelativeTo", None)
                        if redirection_relative_to and redirection_relative_to.lower() == "parent":
                            # target directory should be relative to parent object, not to workdir
                            parent_directory_path = self.parent().get_file_path().parent
                            file_path = Path(os.sep.join([str(parent_directory_path), str(redirection_path), file_location]))
                    return file_path
        return file_location
    
    def moveFile(self, source_path, destination_path):
        if not source_path or not destination_path:
            return False
        if not source_path.is_file():
            # source file not found
            print("source file not found:", source_path)
            return False

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
        object_configuration = self.object_definitions.get(self.task_class)
        if object_configuration:
            for column, column_configuration in object_configuration.items():
                field_type = column_configuration.get("FieldType", None)
                if field_type and field_type == "FileInput":
                    current_value = self.data(column)
                    new_value = data.get(column, None)
                    data_change = current_value != new_value
                    if data_change:
                        current_location = self.get_file_path(file_location=current_value, file_column=column)
                        new_location = self.get_file_path(file_location=new_value, file_column=column)
                        print(f"{column} column value changed, old location", str(current_location))
                        print(f"{column} column value changed, new location", str(new_location))
                        self.objectFileLocationChanged.emit(current_location, new_location, column)
        super().update_data(data)

    def save(self):
        if self.task_class != "PackageManager_PackageDefinition":
            super().save()
            return False

        export = self.export_data

        if self.application.current_workdir:
            export_data = json.dumps(export, indent=4, separators=(',',':'))
            print("Export Data" , export_data)
            
            export_file = self.get_file_path()
            print(f"PD: export {self.display} to: ", str(export_file))
            
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(str(export_file), 'w', encoding="utf-8") as doc:
                doc.write(export_data)
            
            for child_item in self._children:
                child_file_path = child_item.get_file_path()
                if child_file_path:
                    if not child_file_path.is_file():
                        print("create empty task definition file", child_file_path)
                        child_file_path.parent.mkdir(parents=True, exist_ok=True)
                        child_file_path.touch()
            super().save()