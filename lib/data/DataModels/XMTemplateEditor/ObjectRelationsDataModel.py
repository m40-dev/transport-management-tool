from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData, pyqtSignal

import json
from .RelationDataItem import RelationDataItem

class ObjectRelationsDataModel(QAbstractItemModel):
    dataFilterChanged = pyqtSignal(bool) 

    def __init__(self, application, object_data={}, parent_widget=None):
        super().__init__(parent_widget)
        self.application = application
        self.treeview = parent_widget

        self._headers = ["Database Relation", "FK", "CR", "SH"]
        self.rootItem = RelationDataItem(
            application=application, 
            object_class="RootItem",
            model_reference=self)

        if len(object_data) > 0:
            self.setupModelData(object_data, self.rootItem)

    def setFilter(self, filterEnabled=True):
        #emit the signal for all model data items to trigger filter comparison
        self.dataFilterChanged.emit(filterEnabled)
        
        #run over the tree objects (starting at top level root item) and filter elements
        self.treeview.selectionModel().clear()
        self.filterRowItems(self.rootItem)

        #expand all treeview nodes to show the results
        # self.treeview.expandAll()
        
        if not filterEnabled:
            self.treeview.expandAll()

    def filterRowItems(self, parent_item):

        if parent_item.filter_childCount() > 0:
            parent_index = self.indexOf(parent_item)
            filter_items, hide_items = parent_item.filter_childItems()

            self.beginRemoveRows(parent_index, 0, parent_item.totalChildCount())
            parent_item._children = filter_items
            self.endRemoveRows()

            for child_item in filter_items:
                self.filterRowItems(child_item)

    def setupModelData(self, object_data, parentItem):
        """ Main method used to load all data into the model """
        if not isinstance(object_data, dict):
            return False 

        for table_name, table_records in object_data.items():
            data_item = RelationDataItem(
                parent=parentItem,
                application=self.application, 
                object_class="TableDataItem",
                table_data=table_name,
                object_data=table_records,
                model_reference=self)

            # print("table record added", table_name, data_item, data_item.display(), "child records", len(table_records))
            parentItem.addChild(data_item)
        self.layoutChanged.emit()

    def reloadModelData(self, object_data, filter_state=True):
        self.beginResetModel()
        self.rootItem._children = []
        self.rootItem._filtered_children = []
        if object_data and len(object_data)>0:
            self.setupModelData(object_data, self.rootItem)
        self.endResetModel()
        self.setFilter(filter_state)

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers_list):
        self._headers = headers_list

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        # print("read model data")
        if not index.isValid():
            return None

        item = index.internalPointer()
        column = index.column()
        column_name = self.headers[column]

        if (item.object_class == "RelationDataItem" 
            and role == Qt.ItemDataRole.CheckStateRole and column_name in ["FK", "CR", "SH"]):
                return item.checkState(column_name)

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return item.display()

            if column > 0:
                return item.data(column_name)
                
        return None

    def setData(self, index, value, role):
        # print("set model data")
        column = index.column()
        column_name = self.headerData(column)
        item = index.internalPointer()
        item.setData(column_name, value)
        self.dataChanged.emit(index, index)

        # handle multi-selection events
        selected_indexes = self.treeview.selectedIndexes()
        if self.treeview.hasFocus() and len(selected_indexes) > 0:
            # print("multiselect data change")
            for selected_index in selected_indexes:
                if selected_index != index:
                    item = selected_index.internalPointer()
                    item.setData(column_name, value)
                    self.dataChanged.emit(selected_index, selected_index)
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags =  Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        column_name = self.headers[index.column()]
        if column_name in ["FK", "CR", "SH"]:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
            
        return flags

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
        newTask = [RelationDataItem(
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
   
    def extendTableRelations(self, source_index, table_relations):
        parentIndex = source_index
        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()  
            self.setupModelData(table_relations, parentItem)

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

    def remove_item(self, source_index):
        if not source_index.isValid():
            return False
        
        relationItem = source_index.internalPointer()
        item_parent = relationItem.parent()
        parent_row = item_parent.row()

        if item_parent == self.rootItem:
            parentIndex = QModelIndex()
        else:
            parentIndex = self.createIndex(parent_row, 0, item_parent)

        self.beginRemoveRows(parentIndex, relationItem.row(), relationItem.row())
        relationItem.removeItem()
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

    def getCurrentModelData(self, table_name=None, parent=None):
        if not parent:
            parent = self.rootItem
        child_items = parent.getAllItems()
        model_data = {}
        relation_data = []
        for data_item in child_items:
            if data_item.object_class == "TableDataItem":
                table_name = data_item.table_data
                model_data.update(self.getCurrentModelData(table_name, data_item))
            
            if data_item.object_class == "RelationDataItem" and table_name:
                if data_item.object_data not in relation_data:
                    relation_data.append(data_item.object_data)
                model_data = {table_name: relation_data}
            if data_item.childCount() > 0:
                model_data.update(self.getCurrentModelData(parent=data_item))
        return model_data            

