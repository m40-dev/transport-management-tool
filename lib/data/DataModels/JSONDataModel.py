from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData, pyqtSignal
from PyQt6.QtGui import QStandardItemModel
import json
import time

class JSONDataModel(QAbstractItemModel):
    filterStringChanged = pyqtSignal(str) 

    def __init__(self, application, data, model_item_class, parent_widget=None):
        super().__init__(parent_widget)
        self.modelDataClass = model_item_class
        self.application = application
        self.object_configuration = application.object_configuration
        self.rootItem = self.modelDataClass(application=self.application, task_class="RootItem", model_reference=self)
        self._headers = ["Actions"]
        self.treeview = parent_widget
        if data:
            self.setupModelData(data, self.rootItem)

    def setFilterString(self, filter_string):
        #emit the signal for all model data items to trigger filter comparison
        self.filterStringChanged.emit(filter_string)
        # self.treeview.collapseAll()
        
        #run over the tree objects (starting at top level root item) and filter elements
        self.treeview.selectionModel().clear()
        # self.layoutAboutToBeChanged.emit()
        self.filterRowItems(self.rootItem)
        # self.layoutChanged.emit()

        #expand all treeview nodes to show the results
        self.treeview.expandAll()
        
        if len(filter_string) == 0:
            self.treeview.collapseAll()

    def filterRowItems(self, parent_item):

        if parent_item.filter_childCount() > 0:
            parent_index = self.indexOf(parent_item)
            filter_items, hide_items = parent_item.filter_childItems()

            self.beginRemoveRows(parent_index, 0, parent_item.totalChildCount())
            parent_item._children = filter_items
            self.endRemoveRows()

            for child_item in filter_items:
                self.filterRowItems(child_item)

    def setupModelData(self, data, parent):
        """ Main method used to load all data into the model """
        for task_object in data:
            task_class = task_object.get("objectclass", None)
            task_item = self.modelDataClass(
                application=self.application,
                task_class=task_class, 
                task_data=task_object, 
                parent=parent,
                model_reference=self)
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
        # row = index.row()
        # column = index.column()
        # column_name = self.headerData(column)
        item = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            return item.display
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
        return ["application/vnd.jsondataitem"]

    def mimeData(self, indexes):
        mimedata = QMimeData()
        items_data = []
        for index in indexes:
            if index.isValid():
                item = index.internalPointer()
                task_data = item.task_data()
                task_data["parent"] = item.get_parent_data()
                if task_data not in items_data:
                    items_data.append(task_data)
        
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
        # start = time.time()
        encodedData = data.data("application/vnd.jsondataitem")
        
        decodedData = bytes(encodedData)
        jsondata = json.loads(decodedData)
        newItems = []
        source_items = []
        
        for dropped_item in jsondata:
            source_item_uid = dropped_item.get('uid', None)
            source_item = None
            if source_item_uid:
                # find the source Item and save it
                source_item = self.find_item_by_attribute("uid", source_item_uid)
                if source_item:
                    source_items.append(source_item)

            task_class = dropped_item.get('objectclass', "JSONDataItem")
            
            # print("dropped item:", dropped_item)
            # create new object from the source item data and add it to the list, all dropped items will be inserted at once
            new_item = self.modelDataClass(
                application=self.application, 
                task_class=task_class, 
                task_data=dropped_item, 
                parent=parentItem,
                model_reference=self)
            newItems.append(new_item)
            new_item.is_saved = False
            
            
            #emit relocation signal for the new item and tell it about its source item from the same model
            if source_item:
                new_item._previous_task_data = source_item._previous_task_data
                new_item.locationChanged.emit(source_item)
            else:
                #emit new item from source signal to tell new item about source item data
                new_item.dataDropped.emit(dropped_item)
        
        #insert dropped items at new location
        self.insert_items(parentIndex, newItems, row, column)
        
        for new_item in newItems:
            new_item.updateSortOrder()

        #remove source objects at once
        for source_item in source_items:
            self.remove_item(source_item)
        # end = time.time()
        # print("drop event handling", end - start, len(decodedData))
        print("drop event handling", len(decodedData))

        return True
    
    def insert_item(self, task_class, dict_data, parentIndex):
        parentItem = self.rootItem
        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()  
        row = parentItem.childCount()
        newTask = [self.modelDataClass(
            application=self.application, 
            task_class=task_class, 
            task_data=dict_data, 
            parent=parentItem,
            model_reference=self)]
        newTask[0].is_saved = False
        self.insert_items(parentIndex, newTask, row)
    
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

    def remove_item(self, jsondataitem):
        item_parent = jsondataitem.parent()
        parent_row = item_parent.row()

        if item_parent == self.rootItem:
            parentIndex = QModelIndex()
        else:
            parentIndex = self.createIndex(parent_row, 0, item_parent)

        self.beginRemoveRows(parentIndex, jsondataitem.row(), jsondataitem.row())
        jsondataitem.is_saved = False
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
            group_data = group_item.task_data()
            data.append(group_data)
        jsondata = json.dumps(data, indent=4)
        print(jsondata)

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

    def find_index_by_attribute(self, column, value, parent=QModelIndex()):
        """
        Finds the first item in the model with a matching attribute value in the given column.
        """
        if not value:
            return False

        for row in range(self.rowCount(parent)):
            index = self.index(row, 0, parent)
            if index.isValid():
                item_data = index.internalPointer()
                if item_data:
                    column_value = item_data.data(column)
                    if column_value and (column_value.upper() == value.upper()):
                        return index

                    if item_data.childCount() > 0:
                        result = self.find_index_by_attribute(column, value, index)
                        if result:
                            return result
        return QModelIndex()