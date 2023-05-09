from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData
import json

class JSONDataModel(QAbstractItemModel):
    def __init__(self, data, model_item_class, parent=None):
        super().__init__(parent)
        self.modelDataClass = model_item_class
        self.rootItem = self.modelDataClass("RootItem")
        self.setupModelData(data, self.rootItem)
        self._headers = ["Name", "Description"]
    
    def setupModelData(self, data, parent):
        """ Main method used to load all data into the model """
        for task_object in data:
            task_class = task_object.get("objectclass", None)
            task_item = self.modelDataClass(task_class, task_object, parent=parent)
            parent.addChild(task_item)

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
        row = index.row()
        column = index.column()
        column_name = self.headerData(column)
        item = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            return item.data(column_name)
        return None

    def setData(self, index, value, role):
        column = index.column()
        item = index.internalPointer()
        column_name = self.headerData(column)
        item.setData(column_name, value)
        self.dataChanged.emit(index, index)
        # self.exportModelToJson()
        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled \
            | Qt.ItemFlag.ItemIsDropEnabled

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
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        if parentItem:
            return self.createIndex(parentItem.row(), 0, parentItem)

        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    # Drag and Drop
    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def mimeTypes(self):
        return ["application/vnd.jsondataitem"]

    def mimeData(self, indexes):
        mimedata = QMimeData()
        items_data = []
        for index in indexes:
            if index.isValid():
                item = index.internalPointer()
                export = item.task_data
                if export not in items_data:
                    items_data.append(export)
        
        items_data_sorted = sorted(
                            items_data, 
                            key=lambda d: (d['row'])
                            )

        jsondata = json.dumps(items_data_sorted, indent=4)
        encodedJson = jsondata.encode('utf-8')

        mimedata.setData("application/vnd.jsondataitem", encodedJson)
        return mimedata

    def dropMimeData(self, data, action, row, column, parentIndex):
        if not data.hasFormat("application/vnd.jsondataitem"):
            return False

        if action == Qt.DropAction.IgnoreAction:
            return True

        if not parentIndex.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parentIndex.internalPointer()

        encodedData = data.data("application/vnd.jsondataitem")
        
        decodedData = bytes(encodedData)
        jsondata = json.loads(decodedData)
        newItems = []
        dropped_guids = []
        for dropped_item in jsondata:
            item_uid = dropped_item.get('uid', None)
            if item_uid:
                dropped_guids.append(item_uid)

            task_class = dropped_item.get('objectclass', "JSONDataItem")
            newTask = self.modelDataClass(task_class, dropped_item, parentItem)
            newItems.append(newTask)
        
        self.insert_items(parentIndex, newItems, row, column)

        for dropped_guid in dropped_guids:
            item = self.find_item_by_attribute("uid", dropped_guid)
            # print(dropped_guid, item)
            if item:
                self.remove_item(item)
        # self.exportModelToJson()
        return True

    def insert_items(self, parentIndex, list_of_items, row=-1, column=-1):
        parentItem = self.rootItem

        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()

        if row == -1 and column == -1:
            row = parentItem.childCount()
            column = 0
        self.beginInsertRows(parentIndex, row, (row + len(list_of_items)-1) )
        parentItem.insertChildren(row, list_of_items)
        self.endInsertRows()

    def remove_item(self, jsondataitem):
        item_parent = jsondataitem.parent()
        parent_row = item_parent.row()

        if item_parent == self.rootItem or parent_row is None:
            parentIndex = QModelIndex()
        else:
            parentIndex = self.createIndex(parent_row, 0, item_parent)

        self.beginRemoveRows(parentIndex, jsondataitem.row(), jsondataitem.row())
        jsondataitem.removeItem()
        self.endRemoveRows()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/vnd.jsondataitem"):
            event.acceptProposedAction()

    def exportModelToJson(self):
        data = []
        root = self.rootItem
        for i in range(root.childCount()):
            group_item = root.child(i)
            group_data = group_item.task_data
            data.append(group_data)
        jsondata = json.dumps(data, indent=4)
        print(jsondata)

    def find_item_by_attribute(self, column, value, parent=QModelIndex()):
        """
        Finds the first item in the model with a matching attribute value in the given column.
        """
        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            item = index.internalPointer()
            column_value = item.task_data.get(column, None)
            if column_value and (column_value.upper() == value.upper()):
                return item

            if item.childCount() > 0:
                result = self.find_item_by_attribute(column, value, index)
                if result:
                    return result
        return False
