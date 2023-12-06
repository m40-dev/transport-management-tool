from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData, pyqtSignal

import json
from .ObjectDataItem import ObjectDataItem

class ObjectDataListModel(QAbstractItemModel):
    xmlDataStructureChanged = pyqtSignal()

    def __init__(self, application, object_data=[], parent_widget=None):
        super().__init__(parent_widget)
        self.application = application
        self._headers = ["Database Object"]
        self.treeview = parent_widget
        self.tableNameInDisplay = False
        self.rootItem = ObjectDataItem(
            application=application, 
            object_class="RootItem",
            model_reference=self)

        if len(object_data) > 0:
            self.setupModelData(object_data)

    def setupModelData(self, data):
        """ Main method used to load all data into the model """

        for task_object in data:
            task_item = ObjectDataItem(
                application=self.application, 
                object_class="ObjectDataItem",
                object_data=task_object,
                model_reference=self,
                parent=self.rootItem)
            task_item.tableNameInDisplay = self.tableNameInDisplay
            self.rootItem.addChild(task_item)

    def reloadModelData(self, object_data):
        self.beginResetModel()
        self.rootItem._children = []
        if object_data and len(object_data)>0:
            self.setupModelData(object_data)
        self.endResetModel()

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers_list):
        self._headers = headers_list

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return item.display()
        return None

    def setData(self, index, value, role):
        column = index.column()
        item = index.internalPointer()
        column_name = self.headerData(column)
        item.setData(column_name, value)
        self.dataChanged.emit(index, index)
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled

    def headerData(self, section, orientation=Qt.Orientation.Horizontal, role=Qt.ItemDataRole.DisplayRole):
        if orientation==Qt.Orientation.Horizontal and role==Qt.ItemDataRole.DisplayRole:
            if section < len(self.headers):
                return self.headers[section]
        return None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return self.createIndex(row, column)

    def indexOf(self, data_item):
        if data_item == self.rootItem or data_item is None:
            return QModelIndex()

        if data_item is not None:
            parentItem = data_item.parent()
            parentIndex = self.indexOf(parentItem)
            if not parentIndex.isValid():
                parentIndex = QModelIndex()
            return self.index(data_item.row(), 0, parentIndex)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem or parentItem is None:
            return QModelIndex()

        if parentItem:
            return self.createIndex(parentItem.row(), 0, parentItem)

        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0
        parentItem = self.rootItem

        if parent.isValid():
            parentItem = parent.internalPointer()

        if parentItem:
            return parentItem.childCount()
        return 0

    # Drag and Drop
    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def mimeTypes(self):
        return ["application/vnd.objectdataitem"]

    def mimeData(self, indexes):
        mimedata = QMimeData()
        items_data = []
        for index in indexes:
            if index.isValid():
                item = index.internalPointer()

                task_data = item.task_data()
                if task_data not in items_data:
                    items_data.append(task_data)
        
        items_data_sorted = sorted(
                            items_data, 
                            key=lambda d: (d.get('row', ''))
                            )

        jsondata = json.dumps(items_data_sorted, indent=4)
        encodedData = jsondata.encode('utf-8')

        mimedata.setData("application/vnd.objectdataitem", encodedData)
        return mimedata
    
    def insert_item(self, object_class, object_data, parentIndex=QModelIndex()):
        parentItem = self.rootItem
        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()  
        row = parentItem.childCount()
        newTask = [ObjectDataItem(
            application=self.application, 
            object_class=object_class, 
            object_data=object_data,
            parent=parentItem,
            model_reference=self)]
        newTask[0].is_saved = False
        self.insert_items(parentIndex, newTask, row)

    def addTransportTask(self, task_type):
        transport_task_xml_object = self.transport_template.add_transport_task(task_type)
        self.add_xml_item(transport_task_xml_object)
   
    def insert_items(self, parentIndex, list_of_items, row=-1, column=-1):
        parentItem = self.rootItem

        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()

        if row == -1 and column == -1:
            row = parentItem.childCount()
            column = 0
        # print("insert items at location", row, (row + len(list_of_items)-1))
        self.beginInsertRows(parentIndex, row, (row + len(list_of_items)-1) )
        parentItem.insertChildren(row, list_of_items)
        self.endInsertRows()

    def remove_item(self, xmldataitem):
        item_parent = xmldataitem.parent()
        parent_row = item_parent.row()

        if item_parent == self.rootItem:
            parentIndex = QModelIndex()
        else:
            parentIndex = self.createIndex(parent_row, 0, item_parent)

        self.beginRemoveRows(parentIndex, xmldataitem.row(), xmldataitem.row())
        xmldataitem.is_saved = False
        xmldataitem.removeItem()
        self.endRemoveRows()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/vnd.objectdataitem"):
            event.acceptProposedAction()

    def find_item_by_attribute(self, column, value, parent=QModelIndex()):
        """
        Finds the first item in the model with a matching attribute value in the given column.
        """
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            if index.isValid():
                item = index.internalPointer()
                if item.task_data():
                    column_value = item.task_data().get(column, None)
                    if column_value and (column_value.upper() == value.upper()):
                        return item

                    if item.childCount() > 0:
                        result = self.find_item_by_attribute(column, value, index)
                        if result:
                            return result
        return False