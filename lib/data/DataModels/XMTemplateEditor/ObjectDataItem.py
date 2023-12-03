import uuid, re
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal
from pyodbc import Row

class ObjectDataItem(QObject):
    data_changed = pyqtSignal()
    locationChanged = pyqtSignal(object) 
    dataDropped = pyqtSignal(dict)
    itemAdded = pyqtSignal(object)
    columnValueChanged = pyqtSignal(str, str, str)

    def __init__(self, application, object_class="TableDataItem", table_data=None, object_data=None, parent=None, model_reference=None):
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
    
    @property
    def table_name(self):
        return self.objectkey_table(self.object_data)

    def itemDataDropped(self, source_dict):
        # print("foreign model object dropped", source_dict.get("objectclass", None), self.object_class)
        pass

    def itemLocationChanged(self, source_item):
        # print("object location changed", self.display)
        pass
        
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
            self.sortChildren()

    def sortChildren(self):
        if len(self._children) > 0:
            children_sorted = sorted(self._children, key=lambda item: item.display())
            self._children = children_sorted
            
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
                display = f"{data_row.TableName} - ({data_row.DisplayName}) - [{self.childCount()}]"
                return display.replace('%Globals.QIM_ProductNameShort%', "OneIM")

            if self.table_display_pattern is not None and display is None:
                
                object_display = self.application.db.parse_object_display(
                    data_row,
                    self.table_display_pattern)
                display = object_display
                
            if display is None:
                display = f"{self.objectkey_table(data_row)} - ({self.xobjectkey(data_row)})"

            if display is None:
                display = "Object without display name"

        if display:
            display.replace('%Globals.QIM_ProductNameShort%', "OneIM")

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
        # print("set object data", column, value)
        pass
    
    def data(self, column, previous_state=False):
        # print("return column data", column)
        super().data(column)


    def insertChildren(self, row, child_objects):
        if row == -1:
            row = 0
        
        for element in child_objects:
            # print("add child", element.display)
            self.addChild(element, row)
            row +=1

    def object_columns(self, row_data):
        return self.application.db.get_object_columns(row_data)

    def xobjectkey(self, row_data):
        XObjectKey = None
        db_columns = self.object_columns(row_data)
        if isinstance(row_data, Row) and db_columns:
            for column_name in db_columns:
                if column_name.upper() == "XOBJECTKEY":
                    XObjectKey = row_data.__getattribute__(column_name)
                    break
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
        pattern = self.application.db.get_table_display_pattern(table_name)
        # print(data_row, table_name, "table display pattern", pattern)
        return pattern

    def task_data(self):
        export_data = {}
        export_data['uid'] = self.uid
        export_data['objectclass'] = self.object_class
        export_data['row'] = self.row()

        data_row = self.object_data
        
        if self.object_class == "TableDataItem" and self.table_data:
            data_row = self.table_data
        row_data = {}

        for column_name in self.object_columns(data_row):
            row_data[column_name] = str(data_row.__getattribute__(column_name))

        export_data['object_info'] = self.object_info()
        export_data['object_data'] = row_data
        
        return export_data

    def object_info(self):
        data_row = self.object_data
        if self.object_class == "TableDataItem" and self.table_data:
            data_row = self.table_data
        table_name = self.objectkey_table(data_row)
        table_info = self.application.db.table_info.get(table_name, None)
        object_info_dict = {}
        pk_columns_dict = {}
        if table_info is not None:
            pk_columns = [table_info.PKName1, table_info.PKName2]
            for pk_column in pk_columns:
                if pk_column is not None and len(str(pk_column)) > 0 and pk_column not in pk_columns_dict.keys():
                    pk_columns_dict[pk_column] = str(data_row.__getattribute__(pk_column))
        display_name = self.display()
        object_info_dict["table_name"] = table_name
        object_info_dict["object_display"] = f"{table_name} - ({display_name})"
        object_info_dict["pk_columns"] = pk_columns_dict
        return object_info_dict

    