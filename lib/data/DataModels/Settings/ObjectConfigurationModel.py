from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData, pyqtSignal
import json
from .ObjectConfigurationItem import ObjectConfigurationItem

class ObjectConfigurationModel(QAbstractItemModel):
    filterStringChanged = pyqtSignal(str) 

    def __init__(self, application, configuration_data, parent_widget=None):
        super().__init__(parent_widget)
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self._headers = ["Form Elements"]
        self.listview = parent_widget
        self.rootItem = ObjectConfigurationItem(parent=parent_widget, application=application, object_data=None, model_reference=self)

        if configuration_data:
            self.setupModelData(configuration_data)

    def setupModelData(self, configuration_data):
        """ Main method used to load all data into the model """
        configuration_data = self.ProgramConfiguration.sortSectionItems(configuration_data.ConfigurationParameters)
        for configuration_key, configuration_entry in configuration_data.items():
            configuration_item = ObjectConfigurationItem(
                parent=self.rootItem,
                application=self.application,
                object_data={configuration_key: configuration_entry}, 
                model_reference=self)
            self.rootItem.addChild(configuration_item)

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
            return item.display
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
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return self.rootItem.childCount()

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
                object_data = item.object_data()
                if object_data not in items_data:
                    items_data.append(object_data)
        
        jsondata = json.dumps(items_data, indent=4)
        encodedJson = jsondata.encode('utf-8')

        mimedata.setData("application/vnd.jsondataitem", encodedJson)
        return mimedata

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/vnd.jsondataitem"):
            event.acceptProposedAction()

    def dropMimeData(self, data, action, row, column, parentIndex=QModelIndex()):
        if not data.hasFormat("application/vnd.jsondataitem"):
            return False

        if action == Qt.DropAction.IgnoreAction:
            return True

        parentItem = self.rootItem
        if row != -1:
            row = row
        elif parentIndex.isValid():
            row = parentIndex.row()
        else:
            row = self.rowCount(QModelIndex())

        # print("drop item at location", row, column, data, action)

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
                source_item = self.findItemByUID("uid", source_item_uid)
                if source_item:
                    source_items.append(source_item)

            # create new object from the source item data and add it to the list, all dropped items will be inserted at once
            new_item = ObjectConfigurationItem(
                parent=parentItem,
                application=self.application, 
                object_data=dropped_item.get("object_data", None),
                model_reference=self)

            newItems.append(new_item)
            
            #emit relocation signal for the new item and tell it about its source item from the same model
            if source_item:
                new_item.locationChanged.emit(source_item)
            else:
                #emit new item from source signal to tell new item about source item data
                new_item.dataDropped.emit(dropped_item)
        
        #insert dropped items at new location
        self.insertItems(newItems, row)

        #remove source objects at once
        self.removeItems(source_items)

        #emit data change signal
        self.dataChanged.emit(parentIndex, parentIndex)
        return True

    def insertItems(self, list_of_items, row=-1):
        parentItem = self.rootItem

        if row == -1:
            row = parentItem.childCount()

        # print("insert items at location", row, (row + len(list_of_items)-1))
        self.beginInsertRows(QModelIndex(), row, (row + len(list_of_items)-1) )
        parentItem.insertChildren(row, list_of_items)
        self.endInsertRows()

    def removeItems(self, source_items):
        for source_item in source_items:
            self.beginRemoveRows(QModelIndex(), source_item.row(), source_item.row())
            self.rootItem.removeChildItem(source_item)
            self.endRemoveRows()

    def exportModelToJson(self):
        data = []
        root = self.rootItem
        for i in range(root.childCount()):
            group_item = root.child(i)
            group_data = group_item.export_data()
            data.append(group_data)
        jsondata = json.dumps(data, indent=4)
        # print(jsondata)
        return jsondata

    def exportModelData(self):
        data = []
        root = self.rootItem
        export_data = {}
        for i in range(root.childCount()):
            group_item = root.child(i)
            object_data = group_item.export_data()
            export_data.update(object_data)
        return export_data

    def findItemByUID(self, column, uid_query):
        """
        Finds the first item in the model with a matching attribute value in the given column.
        """
        for row in range(self.rowCount()):
            index = self.index(row, 0)
            if index.isValid():
                item = index.internalPointer()
                if item.uid == uid_query:
                    return item
        return False