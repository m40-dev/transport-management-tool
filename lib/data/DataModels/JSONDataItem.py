import uuid
from PyQt6.QtCore import Qt, pyqtSignal, QObject

class JSONDataItem(QObject):
    data_changed = pyqtSignal(object)
    def __init__(self, task_class="JSONDataItem", task_data=None, parent=None):
        super().__init__(parent=parent)
        self._task_class = task_class
        self._parent = parent
        self._children = []
        self._task_data = task_data
        self._uid = None

        if task_data:
            children = task_data.get("children", None)
            if children:
                self.loadChildren(children)

    def loadChildren(self, child_tasks):
        if child_tasks:
            for task_object in child_tasks:
                task_class = task_object.get("objectclass", None)
                task_item = JSONDataItem(task_class, task_object, parent=self)
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
            self.uid = str(uuid.uuid4())
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value
        self._task_data["uid"] = value

    def parent(self):
        return self._parent

    def setParent(self, parent):
        self._parent = parent

    def addChild(self, child, row=None):
        if row is not None:
            # print('insert at', row)
            self._children.insert(row, child)
        else:
            # print('append to the end')
            self._children.append(child)

    def removeChild(self, row):
        if row >= 0 and row < len(self._children):
            print(self._children)
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
        if self._parent is not None:
            return self._parent._children.index(self)
    
    def setData(self, column, value):
        # print("set Item data", column, value)
        prev_value = self._task_data.get(column, None)
        self._task_data[column] = value
        if prev_value != value:
            self.data_changed.emit(self)
    
    def data(self, column):
        # print("get Item data", column)
        return self._task_data.get(column,  None)

    def insertChildren(self, row, child_objects):
        # print(self.name, "insert children here", row, child_objects)
        if row == -1:
            row = 0
        
        for element in child_objects:
            # print("add child", element.name)
            self.addChild(element, row)
            row +=1

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