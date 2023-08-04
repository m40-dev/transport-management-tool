import uuid, re
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal

class RelationDataItem(QObject):
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
        self._filtered_children = []
        self._filter_match = False
        self._parent = parent
        self._uid = str(uuid.uuid4())

        if object_class == "TableDataItem" and object_data and len(object_data) > 0:
            self.loadChildren(object_data)
        
        if model_reference:
            model_reference.dataFilterChanged.connect(self.handleFilterChanged)
    
    def deselectAllRelations(self):
        if self.object_class == "RelationDataItem":
            self.Relation = 0
        
        if self.childCount() > 0:
            for child_item in self._children:
                child_item.deselectAllRelations()

    @property
    def filter_match(self):
        return self._filter_match

    @filter_match.setter
    def filter_match(self, value):
        self._filter_match = value
        if value and self.parent():
            self.parent().filter_match = True

    def handleFilterChanged(self, filterEnabled=True):
        if self.object_class == "RootItem":
            self.filter_match = True
            return
        
        filter_match = False

        if not filterEnabled:
            filter_match = True 
        else:
            if self.object_class == "RelationDataItem":
                filter_match = (int(self.InitialRelationState) > 0 or int(self.Relation) > 0)

            if self.object_class == "TableDataItem" and self.filter_childCount() > 0:
                filter_match = True

        self.filter_match = filter_match

    def filter_childCount(self):
        return len(self.filter_childItems()[0])

    def totalChildCount(self):
        total_childitems = self._children + self._filtered_children
        return len(total_childitems)

    def filter_childItems(self):
        # Iterate over child items, if any of them is matching the filter criterias
        # add child item to temporary list and reset the children list
        filter_rows = []
        hidden_rows = []
        all_items = self._children + self._filtered_children
        for data_item in all_items:
            if data_item.filter_match:
                filter_rows.append(data_item)
            else:
                hidden_rows.append(data_item)

        #temporary assign filtered rows as item children
        sorted_filter_rows = sorted(filter_rows, key=lambda item: item.display())
        # for item in sorted_filter_rows:
        #     print(f"sorted {item.display}")

        self._children = sorted_filter_rows
        self._filtered_children = hidden_rows

        #return filtered rows
        return sorted_filter_rows, hidden_rows

    def setCheckState(self, column_name, value):
        # print("set check state for column", column_name, value)
        columns = ["SH", "CR", "FK"]
        bitmask = ""
        for column in columns:
            bit = 0
            # calculate for tha desired state for the column
            if column == column_name:
                bit = str(int(value > 0))
            # get current state of the column
            else:
                column_setting = self.checkState(column)
                bit = str(int(column_setting > 0))
            bitmask += bit
        self.Relation = self.binary2int(int(bitmask))
        return True


    def checkState(self, column_name):
        # print("get check state for column", column_name, self.Relation)
        if self.Relation:
            if column_name == "FK" and self.Relation in [1, 3, 5, 7]:
                return 2

            if column_name == "CR" and self.Relation in [2, 3, 7]:
                return 2
            
            if column_name == "SH" and self.Relation > 3:
                return 2
        return 0

    def binary2int(self, binary): 
        int_val, i, n = 0, 0, 0
        while(binary != 0): 
            a = binary % 10
            int_val = int_val + a * pow(2, i) 
            binary = binary // 10
            i += 1
        return int_val

    def itemDataDropped(self, source_dict):
        # print("foreign model object dropped", source_dict.get("objectclass", None), self.object_class)
        pass

    def itemLocationChanged(self, source_item):
        print("object location changed", self.display)
        #pass over the source object configuration
        
    def totalChildCount(self):
        total_childitems = self._children + self._filtered_children
        return len(total_childitems)

    def loadChildren(self, child_tasks=[]):
        for data_row in child_tasks:
            data_item = RelationDataItem(
                parent=self, 
                application=self.application,
                object_data=data_row, 
                object_class="RelationDataItem",
                model_reference=self.model_reference)
            self.addChild(data_item)

    def flags(self, column):
        column_name = self.headers[column]
        print("get flags for column", column, column_name)
        if column_name in ["FK", "CR", "SH"]:
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable

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

    def display(self, column=0):
        if self.object_class == "TableDataItem" and self.table_data:
            return self.table_data

        if self.object_class == "RelationDataItem" and self.object_data and column == 0:
            caption = self.Caption
            table_name = self.ParentTable
            column_reference = self.ChildColumn
            relation = f"{column_reference} --> [{table_name}]"

            if self.RelationType == "ParentRelation":
                table_name = self.ChildTable
                column_reference = self.ChildColumn
                relation = f"{column_reference} <-- [{table_name}]"
                return relation

            return f"{relation} ({caption})"
        
        if isinstance(self.object_data, dict) and column > 0:
            return self.data(column)

        return "Object with no display"

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
        if row >= 0 and row <= len(self._children) and len(self._children) > 0:
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
        if column in ["FK", "CR", "SH"]:
            self.setCheckState(column, value)
        return True
    
    def data(self, column, previous_state=False):
        if isinstance(self.object_data, dict):
            return self.object_data.get(column, "")
        return ""

    def insertChildren(self, row, child_objects):
        if row == -1:
            row = 0
        
        for element in child_objects:
            # print("add child", element.display)
            self.addChild(element, row)
            row +=1

    def task_data(self):
        export_data = {}
        export_data['uid'] = self.uid
        export_data['objectclass'] = self.object_class
        export_data['row'] = self.row()
        return export_data

    @property
    def follow_table(self):
        table_name = self.ParentTable

        if self.RelationType == "ParentRelation":
            table_name = self.ChildTable

        if self.RelationType == "ChildRelation":
            table_name = self.ParentTable

        return table_name
    
    @property
    def follow_column(self):
        return self.ChildColumn

    @property
    def InitialRelationState(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("InitialRelationState", 0)
        return 0

    @property
    def RelationType(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("RelationType", "ChildRelation")
        return "ChildRelation"

    @property
    def Caption(self):
        if isinstance(self.object_data, dict):
            caption = self.object_data.get("Caption", "No Display")
            if caption:
                caption.replace('%Globals.QIM_ProductNameShort%', "OneIM")
            return caption
        return "No Display"

    @property
    def Relation(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("Relation", 0)
        return 0

    @Relation.setter
    def Relation(self, value):
        if isinstance(self.object_data, dict):
            self.object_data["Relation"] = value

    @property
    def ChildTable(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ChildTable", "")

    @property
    def ChildColumn(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ChildColumn", "")

    @property
    def ParentTable(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ParentTable", "")
            
    @property
    def ParentColumn(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ParentColumn", "")
    
    def getAllItems(self):
        return self._children