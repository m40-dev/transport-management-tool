import uuid
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal, QSize, pyqtProperty

from PyQt6 import QtCore
from copy import deepcopy
import re, os
from pathlib import Path

FILTER_MIN_LEN = 1

class ObjectConfigurationItem(QObject):
    data_changed = pyqtSignal()
    locationChanged = pyqtSignal(object) 
    dataDropped = pyqtSignal(dict)
    itemAdded = pyqtSignal(object)
    itemRemoved = pyqtSignal(object)
    columnValueChanged = pyqtSignal(str, str, str)

    def __init__(self, parent, application, object_data=None, model_reference=None):
        super().__init__()
        self.application = application
        self.ProgramConfiguration = application.ProgramConfiguration
        
        self.ObjectModelConfiguration = self.ProgramConfiguration.getConfigurationParameters("ObjectModelConfiguration")
        self.ExportConfiguration = self.ObjectModelConfiguration.get("FieldTypeExportMapping", {})

        self.model_reference = model_reference
        self._previous_object_data = object_data
        self._uid = str(uuid.uuid4())
        self._children = []
        self._object_data = object_data

            
        if object_data and isinstance(object_data, dict):
            self._configuration_key = list(object_data.keys())[0]
            self._object_data = list(object_data.values())[0]
            self._object_data["ConfigurationSectionId"] = self.model_reference._object_class

        # self.source_files = self.get_file_data(reload_data=True)
        self.dataDropped.connect(self.itemDataDropped)
        self.locationChanged.connect(self.itemLocationChanged)
        self._isActive = False

    def itemDataDropped(self, source_dict):
        pass

    def itemLocationChanged(self, source_item):
        pass
    
    def flags(self, column):
        return self.flags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    
    def insertChildren(self, row, child_objects):
        if row == -1:
            row = self.childCount()
        
        for element in child_objects:
            # print("add child", element.display)
            self.addChild(element, row)
            row +=1
    
    def parent(self):
        return self.model_reference.rootItem

    def addChild(self, child, row=None):
        if row is not None and row <= self.childCount():
            # print('insert at', row)
            self._children.insert(row, child)
        else:
            # print('append to the end')
            self._children.append(child)
        self.itemAdded.emit(child)

    def removeChild(self, row):
        if row >= 0 and row <= len(self._children):
            return self._children.pop(row)

    def removeChildItem(self, childItem):
        if childItem in self._children:
            child_index = self._children.index(childItem)
            return self._children.pop(child_index)

    def removeItem(self):
        parent_item = self.parent()
        parent_item.removeChild(self.row())

    def child(self, row):
        if row >= 0 and row < len(self._children):
            return self._children[row]

    def childCount(self):
        return len(self._children)

    def removeItem(self):
        parent_item = self.parent()
        if self.parent():
            parent_item.removeChild(self.row())
        self.itemRemoved.emit()

    def row(self):
        if self.parent() and self in self.parent()._children:
            return self.parent()._children.index(self)
        print("item not found in the child list")
        return 0
    
    def setData(self, column, value):
        # print("set data", column, value)
        if not self._object_data:
            return False
        
        if column == "FieldId":
            self._configuration_key = value
            self.data_changed.emit()
            return True
            
        prev_value = self._object_data.get(column, "")
        if prev_value != value:
            # print(f"set item data for column with new value, {column}, previous value {prev_value}, new value {value}")
            self._object_data[column] = value
            self.data_changed.emit()
            self.columnValueChanged.emit(column, str(prev_value), str(value))
    
    def data(self, column, previous_state=False):
        if self._object_data:
            if column=="FieldId":
                return self.configuration_key

            return self._object_data.get(column,  None)
        return None

    @property
    def uid(self):
        if not self._object_data.get("uid", None) and not self._uid:
            self._uid = str(uuid.uuid4())
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value
        self._object_data["uid"] = value

    def object_data(self):
        if self._object_data is None:
            return self._object_data
        export_data = {}
        export_data["object_data"] = {self._configuration_key: self._object_data}
        export_data["uid"] = self.uid
        export_data["RowId"] = self.row()

        return export_data

    def export_data(self):
        self._object_data["RowId"] = self.row()
        export_data = {}
        
        for reference_key, export_configuration in self.ExportConfiguration.items():
            #Common attributes export
            if reference_key=="Common" and isinstance(export_configuration, list):
                for export_column in export_configuration:
                    export_data[export_column] = self.getFieldConfigurationValue(export_column)
            
            #referenced columns export
            if isinstance(export_configuration, dict):
                reference_field_configuration = self._object_data.get(reference_key, "")
                if reference_key in export_data.keys():
                    reference_field_configuration = export_data[reference_key]
                
                if len(str(reference_field_configuration)) > 0 and reference_field_configuration in export_configuration.keys():
                    export_columns = export_configuration.get(reference_field_configuration, [])
                    for export_column in export_columns:
                        export_data[export_column] = self.getFieldConfigurationValue(export_column)
                
                if reference_key == self.model_reference._object_class and self.configuration_key in export_configuration.keys():
                    # print("add class specific field configurations for section", reference_key, self.configuration_key)
                    export_columns = export_configuration.get(self.configuration_key, [])
                    for export_column in export_columns:
                        export_data[export_column] = self.getFieldConfigurationValue(export_column)


        export_dict = {self._configuration_key: export_data}
        # print(export_dict)
        return export_dict
    
    def getFieldConfigurationValue(self, export_column):
        export_value = self._object_data.get(export_column, None)
        if export_value is None:
            if export_column in self.ObjectModelConfiguration.keys():
                export_value = self.ObjectModelConfiguration[export_column].get("DefaultValue", "")
        
        if isinstance(export_value, str) and export_value.isnumeric():
            export_value = int(export_value)

        if not isinstance(export_value, bool) and str(export_value).upper() in ["TRUE", "FALSE"]:
            export_value = export_value.upper() == "TRUE"
        # print(f"export value  for {export_column} could not be found, using default field configuration.. -> {export_value}")
        return export_value


    @property
    def display(self):
        return self._object_data.get("Display", "")

    @property
    def description(self):
        return self._object_data.get("Description", "")


    @property
    def configuration_key(self):
        return self._configuration_key

    @configuration_key.setter
    def configuration_key(self, value):
        self._configuration_key = value

    @property
    def isActive(self):
        return self._isActive

    @isActive.setter
    def isActive(self, isActive):
        self._isActive = isActive

