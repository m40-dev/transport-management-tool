import uuid
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal
from copy import deepcopy
from lxml.etree import _Element, _Comment

FILTER_MIN_LEN = 1

class XMLDataItem(QObject):
    data_changed = pyqtSignal()
    locationChanged = pyqtSignal(object) 
    dataDropped = pyqtSignal(dict)
    itemAdded = pyqtSignal(object)
    columnValueChanged = pyqtSignal(str, str, str)

    def __init__(self, application, object_class="XMLDataItem", xml_custom_object=None, parent=None, model_reference=None):
        super().__init__(parent=parent)
        self.application = application
        self.model_reference = model_reference
        self._object_class = object_class
        self._parent = parent
        self._children = []
        self._filtered_children = []
        self._xml_data = xml_custom_object
        self._previous_xml_data = None
        self._uid = str(uuid.uuid4())
        self._is_saved = True
        self._filter_match = True
        self.filter_string = ""
        self._display = ""
        self._description = ""
        
        if xml_custom_object:
            children = xml_custom_object.children()
            if children:
                self.loadChildren(children)
        
        self.dataDropped.connect(self.itemDataDropped)
        self.locationChanged.connect(self.itemLocationChanged)

    def itemDataDropped(self, source_dict):
        # print("foreign model object dropped", source_dict.get("objectclass", None), self.object_class)
        pass

    def itemLocationChanged(self, source_item):
        print("object location changed", self.display)
        #pass over the source files configuration
        self._previous_xml_data = source_item._previous_xml_data
        
    def totalChildCount(self):
        total_childitems = self._children + self._filtered_children
        return len(total_childitems)

    def loadChildren(self, child_tasks):
        if child_tasks:
            for task_object in child_tasks:
                if not isinstance(task_object, _Element) and not isinstance(task_object, _Comment):
                    task_item = self.__class__(
                        application=self.application, 
                        object_class=task_object._xml_object_class, 
                        xml_custom_object=task_object, 
                        parent=self,
                        model_reference=self.model_reference)
                    self.addChild(task_item)

    def flags(self, column):
        return self.flags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    @property
    def object_class(self):
        return self._object_class

    @object_class.setter
    def object_class(self, value):
        self._object_class = value

    @property
    def uid(self):
        if not self._uid:
            self._uid = str(uuid.uuid4())
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    def display(self):
        if self._xml_data:
            return self._xml_data.display
        return ""

    def setDisplay(self, value):
        if self._xml_data:
            self._xml_data.display = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def parent(self):
        return self._parent

    def setParent(self, parent):
        self._parent = parent

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

    def row(self):
        if self.parent() and self in self.parent()._children:
            return self.parent()._children.index(self)
        else:
            if self in self.model_reference.rootItem._children:
                return self.model_reference.rootItem._children.index(self)
        return 0
    
    def setData(self, column, value):
        # print("set data", column, value)
        prev_value = self._xml_data.xml_get_attribute(column, "")
        if prev_value != value:
            # print(f"set item data for column with new value, {column}, previous value {prev_value}, new value {value}")
            self._xml_data.xml_set_attribute(column, value)
            self.data_changed.emit()
            self.columnValueChanged.emit(column, str(prev_value), str(value))
    
    def data(self, column, previous_state=False):
        if previous_state and self._previous_xml_data:
            return self._previous_xml_data.xml_get_attribute(column)

        if self._xml_data:
            return self._xml_data.xml_get_attribute(column)
            
        super().data(column)

    def insertChildren(self, row, child_objects):
        if row == -1:
            row = 0
        
        for element in child_objects:
            # print("add child", element.display)
            self.addChild(element, row)
            row +=1

    def get_children_data(self, object_class=None, export_data=False):
        children = []
        if self.childCount() == 0:
            return children

        for child_item in self._children:
            if export_data:
                child_data = child_item.export_data()
            else:
                child_data = child_item.task_data()
            
            if object_class and child_item.object_class == object_class:
                children.append(child_data)
                continue
            
            if object_class is None:
                children.append(child_data)
        return children

    def task_data(self):
        if self._xml_data is None:
            return self._xml_data

        export_data = deepcopy(self._xml_data)
        # export_data = self._xml_data
        export_data['uid'] = self.uid
        export_data['objectclass'] = self.object_class
        export_data['row'] = self.row()
        export_data['children'] = self.get_children_data()
        return export_data

    @property
    def edit_data(self):
        return self.task_data()

    def update_data(self, dict_data):
        if self._previous_xml_data is None:
            # store the original data in case we want to restore it
            self._previous_xml_data = deepcopy(self.task_data())

        for key, value in dict_data.items():
            self.setData(key, value)


