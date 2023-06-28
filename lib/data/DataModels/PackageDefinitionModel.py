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
        self.objectDataChanged.connect(self.dataChangeHandler)

        
        if task_data:
            self.source_files = self.get_file_data(reload_data=True)
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
        self.source_files = source_item.get_file_data()

    def update_file_locations(self):  
        print("update file locations", self.display, self.source_files)    
        column_configurations = self.object_configuration.get_columns_configuration_by_type(self.task_class, "FileInput")
        if column_configurations and self.source_files:
            for column in column_configurations.keys():
                source_file = self.source_files.get(column, None)
                target_file = self.get_file_path(file_column=column)
                if source_file and target_file and source_file != target_file:
                    self.moveFile(source_file, target_file)
        self.source_files = self.get_file_data(reload_data=True)

    def dataChangeHandler(self, previous_data):
        # self.source_files = self.get_file_data()
        pass

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
            column_value = self.task_data().get(column, "")
            if previous_state and self._previous_task_data:
                column_value = self._previous_task_data.get(column, "")

            if "parent." in column.lower() and self.parent():
                # parent object reference
                parent_column = column.split(".")[1]
                column_value = self.parent().task_data().get(parent_column, "")
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
        self.application.delete_empty_directory(source_path.parent)

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
        self.update_file_locations()
        if self.task_class == "PackageManager_PackageDefinition":
            if self.application.current_workdir:
                export_file = self.get_file_path()
                export = self.export_data()
                export_data = json.dumps(export, indent=4, separators=(',',':'))
                # print("Export Data" , export_data)
                
                print(f"PD: Exported {self.display} to: ", str(export_file))
                
                export_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(str(export_file), 'w', encoding="utf-8") as doc:
                    doc.write(export_data)
            
                # save child objects
                for child_item in self._children:
                    child_item.save()
        super().save()
        