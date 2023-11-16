import uuid
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal
from copy import deepcopy
import re, os
from pathlib import Path

FILTER_MIN_LEN = 1

class ObjectConfigurationItem(QObject):
    data_changed = pyqtSignal()
    locationChanged = pyqtSignal(object) 
    dataDropped = pyqtSignal(dict)
    itemAdded = pyqtSignal(object)
    columnValueChanged = pyqtSignal(str, str, str)

    def __init__(self, parent, application, object_data=None, model_reference=None):
        super().__init__()
        self.application = application
        self.ProgramConfiguration = application.ProgramConfiguration
        self.model_reference = model_reference
        self._previous_object_data = object_data
        self._uid = str(uuid.uuid4())
        self._children = []
        if object_data and isinstance(object_data, dict):
            self._configuration_key = list(object_data.keys())[0]
            self._object_data = list(object_data.values())[0]

        # self.source_files = self.get_file_data(reload_data=True)
        self.dataDropped.connect(self.itemDataDropped)
        self.locationChanged.connect(self.itemLocationChanged)

    def itemDataDropped(self, source_dict):
        pass

    def itemLocationChanged(self, source_item):
        pass
    
    def flags(self, column):
        return self.flags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable
    
    def insertChildren(self, row, child_objects):
        if row == -1:
            row = 0
        
        for element in child_objects:
            # print("add child", element.display)
            self.addChild(element, row)
            row +=1

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
        parent_item.removeChild(self.row())

    def row(self):
        if self.parent() and self in self.parent()._children:
            return self.parent()._children.index(self)
        else:
            if self in self.model_reference.rootItem._children:
                return self.model_reference.rootItem._children.index(self)
        return 0
    
    def setData(self, column, value):
        # print("set data", column, value)
        if not self._object_data:
            return False
        
        if column == "configuration_key":
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

        return export_data

    def export_data(self):
        self._object_data["RowId"] = self.row()
        for key, value in self._object_data.items():
            if isinstance(value, bool):
                value = str(value)
                self._object_data[key] = value
        return {self._configuration_key: self._object_data}
    
    @property
    def display(self):
        return str({self._configuration_key: self._object_data})

    @property
    def configuration_key(self):
        return self._configuration_key

    @configuration_key.setter
    def configuration_key(self, value):
        self._configuration_key = value


