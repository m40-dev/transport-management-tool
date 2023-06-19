import uuid
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal
from PyQt6.QtGui import QStandardItem

class JSONDataItem(QObject):
    data_changed = pyqtSignal()

    def __init__(self, application, task_class="JSONDataItem", task_data=None, parent=None, model_reference=None):
        super().__init__(parent=parent)
        self.application = application
        self.object_definitions = application.object_definitions
        self.model_reference = model_reference
        self._task_class = task_class
        self._parent = parent
        self._children = []
        self._task_data = task_data
        self._uid = str(uuid.uuid4())
        self._is_saved = True
        self._filter_match = True

        if model_reference:
            model_reference.filterStringChanged.connect(self.handleFilterStringChanged)

        if task_data:
            children = task_data.get("children", None)
            if children:
                self.loadChildren(children)

    @property
    def filter_match(self):
        return self._filter_match

    @filter_match.setter
    def filter_match(self, value):
        self._filter_match = value
        if value and self.parent():
            self.parent().filter_match = value

    def handleFilterStringChanged(self, filter_string):
        filter_match = self.check_filter_conditions(filter_string)
        self.filter_match = filter_match

    def check_filter_conditions(self, filter_string):
        #Initially set filter to true (show all items)
        item_match = True

        if not filter_string or len(filter_string.strip()) == 0:
            return item_match
        
        #General display match condition
        item_match = (filter_string.lower() in self.display.lower())

        #Return final verification state
        return item_match 

    def filter_childCount(self):
        return len(self.filter_childItems())

    def filter_childItems(self):
        filter_rows = []
        for data_item in self.children():
            if data_item.filter_match:
                filter_rows.append(data_item) 
        self._children = filter_rows
        return filter_rows

    def loadChildren(self, child_tasks):
        if child_tasks:
            for task_object in child_tasks:
                task_class = task_object.get("objectclass", None)
                task_item = self.__class__(
                    application=self.application, 
                    task_class=task_class, 
                    task_data=task_object, 
                    parent=self,
                    model_reference=self.model_reference)
                self.addChild(task_item)

    def flags(self, column):
        return self.flags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    @property
    def task_class(self):
        return self._task_class

    @task_class.setter
    def task_class(self, value):
        self._task_class = value

    @property
    def uid(self):
        if not self._task_data.get("uid", None) and not self._uid:
            self._uid = str(uuid.uuid4())
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value
        self._task_data["uid"] = value

    @property
    def display(self):
        configuration = self.object_definitions.get(self.task_class)
        
        if configuration is None:
            return ""
        display_text = []
        for field, field_configuration in configuration.items():
            is_display_column = "DisplayRole" in field_configuration.get("FieldRole", [])
            if not is_display_column:
                continue
            text = str(self._task_data.get(field, ""))
            if len(text.strip()) > 0:
                display_text.append(text.strip())
        if len(display_text) > 0:
            return ", ".join(display_text)
        return ""
    
    @display.setter
    def display(self, value):
        configuration = self.object_definitions.get(self.task_class)
        
        if configuration is None:
            return ""
        
        for field, field_configuration in configuration.items():
            is_display_column = "DisplayRole" in field_configuration.get("FieldRole", [])
            if not is_display_column:
                continue
            self.setData(field, value)
            return True

    @property
    def description(self):
        configuration = self.object_definitions.get(self.task_class)
        
        if configuration is None:
            return ""
        display_text = []
        for field, field_configuration in configuration.items():
            is_display_column = "DescriptionRole" in field_configuration.get("FieldRole", [])
            if not is_display_column:
                continue
            text = str(self._task_data.get(field, ""))
            if len(text.strip()) > 0:
                display_text.append(text.strip())
        if len(display_text) > 0:
            return ", ".join(display_text)
        return ""

    @description.setter
    def description(self, value):
        configuration = self.object_definitions.get(self.task_class)
        
        if configuration is None:
            return ""
        
        for field, field_configuration in configuration.items():
            is_display_column = "DescriptionRole" in field_configuration.get("FieldRole", [])
            if not is_display_column:
                continue
            self.setData(field, value)
            return True

    # def parent(self):
    #     return self._parent

    # def setParent(self, parent):
    #     self._parent = parent

    def addChild(self, child, row=None):
        if row is not None:
            # print('insert at', row)
            self._children.insert(row, child)
        else:
            # print('append to the end')
            self._children.append(child)

    def removeChild(self, row):
        if row >= 0 and row < len(self._children):
            # print(self._children)
            return self._children.pop(row)

    def removeItem(self):
        parent_item = self.parent()
        parent_item.removeChild(self.row())

    def child(self, row):
        if row >= 0 and row < len(self._children):
            return self._children[row]

    def childCount(self):
        return len(self._children)

    def row(self):
        if self._parent is not None and self in self._parent._children:
            return self._parent._children.index(self)
        return 0
    
    def setData(self, column, value):
        # print("set data", column, value)
        prev_value = self._task_data.get(column, None)
        if prev_value != value:
            self._task_data[column] = value
            self.is_saved = False
            self.data_changed.emit()
    
    def data(self, column):
        if self._task_data:
            return self._task_data.get(column,  None)
        super().data(column)

    def insertChildren(self, row, child_objects):
        if row == -1:
            row = 0
        
        for element in child_objects:
            # print("add child", element.name)
            self.addChild(element, row)
            row +=1

    @property
    def is_saved(self):
        return self._is_saved
    
    @is_saved.setter
    def is_saved(self, state):
        self._is_saved = state
        if state is False and self.parent():
            self.parent().is_saved = state
            self.parent().data_changed.emit()

    def save(self):
        self.is_saved = True
        self.data_changed.emit()
        for child_node in self.children():
            child_node.save()

    @property
    def task_data(self):
        if self._task_data is None:
            return self._task_data

        children = []

        for i in range(self.childCount()):
            child_item = self.child(i)
            child_data = child_item.task_data
            children.append(child_data)

        self._task_data['children'] = children
        self._task_data['uid'] = self.uid
        self._task_data['objectclass'] = self.task_class
        self._task_data['row'] = self.row()

        return(self._task_data)

    @property
    def edit_data(self):
        return self._task_data

    def update_data(self, dict_data):
        for key, value in dict_data.items():
            self.setData(key, value)