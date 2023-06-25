from . import JSONDataItem, JSONDataModel, pyqtSignal
from copy import deepcopy
from pathlib import Path
import json
import os
import re

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
    objectDataChanged = pyqtSignal(dict)
    

    def __init__(self, application, task_class="PackageManager_PackageDefinition", task_data=None, parent=None, model_reference=None):
        super().__init__(
            application=application,
            parent=parent, 
            task_class=task_class, 
            task_data=task_data,
            model_reference=model_reference)

        if task_class is None:
            self.task_class = "PackageManager_PackageDefinition"

        self.object_configuration = application.object_configuration
        self.objectFileLocationChanged.connect(self.fileLocationChangeHandler)
        self.objectDataChanged.connect(self.dataChangeHandler)

        # object_configuration = self.object_configuration.get(self.task_class)
        # if self.parent():
        #     self.parent().objectDataChanged.connect(self.parentDefinitionChanged)

        if task_data:
            # children object handling
            child_tasks = task_data.get("children", None)
            if not child_tasks:
                #TODO: get child task column from the object configuration
                child_tasks = task_data.get("Tasks", None)
                if child_tasks:
                    # self._task_class = "PackageManager_PackageDefinition"
                    self.loadChildren(child_tasks)
    
    def itemLocationChanged(self, source_item):
        print("object location changed", source_item.parent().display, self.parent().display)
        object_configuration = self.object_configuration.get(self.task_class)
        if object_configuration and self.parent():
            for column, column_configuration in object_configuration.items():
                if (column_configuration.get("FieldType", None) == "FileInput"): 
                    source_file = source_item.get_file_path(file_column=column, previous_state=True)
                    target_file = self.get_file_path(file_column=column, previous_state=True)
                    if source_file != target_file:
                        self.moveFile(source_file, target_file)

    def dataChangeHandler(self, previous_data):
        print("data change handler")
        for column, previous_value in previous_data.items():
            # current_value = self.task_data.get(column, None)
            # if previous_value != current_value:
                #check column configuration
                # print("data change handler", column, previous_value, current_value)
            column_config = self.object_configuration.get_column_configuration(self.task_class, column)
            # print("column configuration", column, column_config)
            if column_config:
                if (column_config.get("FieldType", None) == "FileInput"):
                    # current_location = self.get_file_path(file_location=previous_value, file_column=column, previous_state=True)
                    # new_location = self.get_file_path(file_location=current_value, file_column=column)
                    current_location = self.get_file_path(file_column=column, previous_state=True)
                    new_location = self.get_file_path(file_column=column)
                    
                    # print(f"{column} column value changed, old location", str(current_location))
                    # print(f"{column} column value changed, new location", str(new_location))
                    if current_location != new_location:
                        self.objectFileLocationChanged.emit(current_location, new_location, column)

    def fileLocationChangeHandler(self, source_path, target_path, file_column):
        print("fileLocationChangeHandler", source_path, target_path)
        if source_path.is_file():
            self.moveFile(source_path, target_path)

    def parentDefinitionChanged(self, previous_parent_data):
        print(self.display, "parent definition changed", self.parent().display)
        if self.application.current_workdir:
            object_configuration = self.item_class_configuration
            if object_configuration and self.parent():
                for column, column_configuration in object_configuration.items():
                    if (column_configuration.get("FieldType", None) == "FileInput"):
                        file_name = self.data(column, previous_state=True)
                        if len(file_name.strip()) > 0:
                            self.moveChildFile(file_column=column)
                        # pass
    
    def moveChildFile(self, file_column="DefinitionFile"):
        file_name = self.data(file_column, previous_state=True)
        if not file_name:
            #file name not in data, there is nothing to do
            return False

        print(self.display, "checking for child object files to be moved:", file_name, "column", file_column)
        column_configuration = self.object_configuration.get_column_configuration(self.task_class, file_column)
        if column_configuration:
            source_file = self.get_file_path(file_column=file_column, previous_state=True)
            target_file = self.get_file_path(file_column=file_column)
            # print(f"{file_column} changed? {source_file != target_file} - source file: {source_file}, target file: {target_file}")
            if source_file != target_file and source_file.is_file():
                #move files only if needed
                self.moveFile(source_file, target_file)

    def get_file_path(self, file_location=None, file_column="DefinitionFile", previous_state=False):
        if not file_location:
            file_location = self.data(file_column, previous_state)
        
        if not file_location:
            return file_location

        object_configuration = self.item_class_configuration
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
                    parent_directory_path = self.application.current_workdir
                    file_path = Path(os.sep.join([parent_directory_path, file_location]))
                    
                    redirection_relative_to = definition_file_configuration.get("RedirectDirectoryRelativeTo", None)
                    if redirection_relative_to and redirection_relative_to.lower() == "parent" and self.parent():
                        # target directory should be relative to parent object, not to workdir
                        parent_location = self.parent().data(file_column, previous_state)
                        if previous_state and self.parent()._previous_task_data:
                            #previous data state is required, but parent location is determined by the DefinitionFile path
                            parent_location = self.parent()._previous_task_data.get("DefinitionFile")

                        parent_directory_path = self.parent().get_file_path(parent_location, previous_state=previous_state).parent
                        # print(f"get file path in previous state {previous_state}, parent location {parent_location}")

                    static_redirect = definition_file_configuration.get("RedirectDirectoryStatic", None)
                    if static_redirect:
                        # Redirect File To different Directory
                        file_path = Path(os.sep.join([str(parent_directory_path), str(static_redirect), file_location]))
                        return file_path
                    
                    dynamic_redirect = definition_file_configuration.get("RedirectDirectoryDynamic", None)
                    if dynamic_redirect:
                        # Redirect File To different Directory based on the object parameters
                        dynamic_redirect = self.parse_text_pattern(dynamic_redirect, previous_state)
                        file_path = Path(os.sep.join([str(parent_directory_path), str(dynamic_redirect), file_location]))
                        # print("dynamic file location", file_path)
                        return file_path
                    return file_path
        return file_location

    def get_replacement_values(self, replacement_columns, previous_state=False):
        replacement_dict = {}
        for column in replacement_columns:
            column_value = self.task_data.get(column, "")
            if previous_state and self._previous_task_data:
                column_value = self._previous_task_data.get(column, "")

            if "parent." in column.lower() and self.parent():
                # parent object reference
                parent_column = column.split(".")[1]
                column_value = self.parent().task_data.get(parent_column, "")
                if previous_state and self.parent()._previous_task_data:
                    column_value = self.parent()._previous_task_data.get(parent_column, "")
            replacement_dict[column] = column_value
        return replacement_dict

    def parse_text_pattern(self, string_pattern, previous_state=False):

        regex_pattern = r'%([^%]+)%'

        matches = re.findall(regex_pattern, string_pattern)

        # print("pattern matches", matches)

        replacement_dict = self.get_replacement_values(matches, previous_state)

        # print("replacement dict", replacement_dict)

        parsed_string = re.sub(regex_pattern, lambda match: replacement_dict.get(match.group(1), match.group(0)), string_pattern)

        # print(f"string pattern: {string_pattern}, parsed string {parsed_string}")

        return parsed_string

    def moveFile(self, source_path, destination_path):
        print(f"moving {source_path} to {destination_path}")
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

    def save(self):
        # print(f"start save {self._previous_task_data is not None}, task class {self.task_class}")
        if self._previous_task_data is not None:
            self.objectDataChanged.emit(self._previous_task_data)

        # if export_file and not export_file.is_file():
        #     print("create empty object definition file", export_file)
        #     export_file.parent.mkdir(parents=True, exist_ok=True)
        #     export_file.touch()

        if self.task_class == "PackageManager_PackageDefinition":
            if self.application.current_workdir:
                export_file = self.get_file_path()
                export = self.export_data
                export_data = json.dumps(export, indent=4, separators=(',',':'))
                # print("Export Data" , export_data)
                
                print(f"PD: Exported {self.display} to: ", str(export_file))
                
                export_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(str(export_file), 'w', encoding="utf-8") as doc:
                    doc.write(export_data)
            
                # save child objects
                for child_item in self._children:
                    if self._previous_task_data:
                        #update child item with latest parent data
                        child_item.parentDefinitionChanged(self._previous_task_data)
                    child_item.save()
        super().save()
        