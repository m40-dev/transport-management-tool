import uuid, re
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal
from copy import deepcopy
from lxml.etree import _Element, _Comment
from pyodbc import Row

class ObjectDataItem(QObject):
    data_changed = pyqtSignal()
    locationChanged = pyqtSignal(object) 
    dataDropped = pyqtSignal(dict)
    itemAdded = pyqtSignal(object)
    columnValueChanged = pyqtSignal(str, str, str)

    def __init__(self, parent, application, object_class="TableDataItem", table_data=None, object_data=None, model_reference=None):
        super().__init__(parent=parent)
        self.application = application
        self.model_reference = model_reference
        self._object_class = object_class
        self.object_data = object_data
        self.table_data = table_data
        self._children = []
        self._parent = parent
        self._uid = str(uuid.uuid4())
        if object_class == "TableDataItem" and object_data:
            self.loadChildren(object_data)
    
    def itemDataDropped(self, source_dict):
        # print("foreign model object dropped", source_dict.get("objectclass", None), self.object_class)
        pass

    def itemLocationChanged(self, source_item):
        print("object location changed", self.display)
        #pass over the source files configuration
        # self.object_data = source_item.object_data
        
    def totalChildCount(self):
        total_childitems = self._children + self._filtered_children
        return len(total_childitems)

    def loadChildren(self, child_tasks):
        if child_tasks:
            for data_row in child_tasks:
                if isinstance(data_row, Row):
                    data_item = ObjectDataItem(
                        parent=self, 
                        application=self.application,
                        object_data=data_row, 
                        object_class="ObjectDataItem",
                        model_reference=self.model_reference)
                    self.addChild(data_item)

    def flags(self, column):
        return Qt.ItemFlag.ItemIsEnabled

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
        display = None
        data_row = self.object_data
        if self.object_class == "TableDataItem" and self.table_data:
            data_row = self.table_data

        if isinstance(data_row, str):
            return data_row

        if isinstance(data_row, Row):
            if self.object_class == "TableDataItem" and self.objectkey_table(data_row) == "DialogTable":
                return f"{data_row.TableName} - ({data_row.DisplayName})"

            if self.table_display_pattern is not None and display is None:
                object_display = self.application.db.parse_object_display(
                    data_row,
                    self.table_display_pattern)
                
                display = object_display
                
            if display is None:
                display = f"{self.objectkey_table(data_row)} - ({self.xobjectkey(data_row)})"

            if display is None:
                display = "Object without display name"
        return display

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
        print("set data", column, value)
    
    def data(self, column, previous_state=False):
        print("return column data", column)
            
        super().data(column)

    def insertChildren(self, row, child_objects):
        if row == -1:
            row = 0
        
        for element in child_objects:
            # print("add child", element.display)
            self.addChild(element, row)
            row +=1

    # @property
    # def tooltipText(self):
    #     return f"{str(self.data.tag)}: {str(self.data.attrib)}. {str(self.data.text)}"

    def object_columns(self, row_data):
        return self.application.db.get_object_columns(row_data)

    def xobjectkey(self, row_data):
        XObjectKey = None
        if isinstance(row_data, Row) and "XObjectKey" in self.object_columns(row_data):
            XObjectKey = row_data.XObjectKey
        return XObjectKey

    def objectkey_table(self, row_data):
        table_name = None
        regex = r"<T>(.*?)</T>"
        xobjectkey = self.xobjectkey(row_data)
        if xobjectkey is not None:
            match = re.search(regex, xobjectkey)
            if match:
                table_name = match.group(1)
        return table_name

    @property
    def table_display_pattern(self):
        data_row = self.object_data
        if self.object_class == "TableDataItem" and self.table_data:
            data_row = self.table_data
        table_name = self.objectkey_table(data_row)
        return self.application.db.get_table_display_pattern(table_name)

    def task_data(self):

        export_data = {}
        # export_data['xml_data'] = self._xml_data.string
        # export_data['xml_object_class'] = self._xml_data.xml_object_class
        export_data['uid'] = self.uid
        export_data['objectclass'] = self.object_class
        export_data['row'] = self.row()
        return export_data