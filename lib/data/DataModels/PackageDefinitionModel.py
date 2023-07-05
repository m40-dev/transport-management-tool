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
        
        if task_data:
            self.source_files = self.get_file_data(reload_data=True)
            self.source_files_text = self.get_file_strings(reload_data=True)
            # children object handling
            child_tasks = task_data.get("children", None)
            children_columns_configuration = self.object_configuration.get_columns_configuration_by_type(self.task_class, "ChildObjectReference")
            if not child_tasks and children_columns_configuration:
                for column in children_columns_configuration.keys():
                    child_tasks = task_data.get(column, None)
                    if child_tasks:
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
        