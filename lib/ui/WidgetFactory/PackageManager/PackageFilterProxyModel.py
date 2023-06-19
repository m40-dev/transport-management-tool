from PyQt6 import QtCore
from PyQt6.QtCore import QModelIndex, Qt, pyqtSignal

class PackageFilterProxyModel(QtCore.QAbstractProxyModel):
    filterStringChanged = pyqtSignal(str)

    def __init__(self, application, source_model, parent_widget):
        super().__init__(parent_widget)
        self.application = application
        self.filterString = ""
        self.treeview = parent_widget
        self.setSourceModel(source_model)
        self.rootItem = self.sourceModel().rootItem
        
    def setFilterString(self, filter_string):
        self.filterString = filter_string
        self.sourceModel().filterStringChanged.emit(filter_string)
        # self.layoutAboutToBeChanged.emit()
        self.filterRowItems(self.rootItem)
        # self.invalidateRowsFilter()
        self.layoutChanged.emit()

    def columnCount(self, index):
        return 1

    def rowCount(self, index=QModelIndex()):
        if index.isValid():
            data_item = index.internalPointer()
            if data_item:
                return data_item.filter_childCount()
        return self.rootItem.filter_childCount()

    def headerData(self, section, orientation=Qt.Orientation.Horizontal, role=Qt.ItemDataRole.DisplayRole):
        return self.sourceModel().headerData(section, orientation, role)

    # def filterAcceptsRow(self, source_row, source_parent):
    #     source_index = self.sourceModel().index(source_row, 0, source_parent)
    #     source_item = source_index.internalPointer()
    #     if source_item:
    #         return source_item.filter_match
    #     return True

    def filterRowItems(self, parent_item):
        row = 0
        proxy_parent_index = self.mapFromSource(self.indexOf(parent_item))
        if parent_item.filter_childCount() > 0:
            for child_item in parent_item.filter_childItems():
                self.filterRowItems(child_item)

    # def data(self, index, role=Qt.ItemDataRole.DisplayRole):
    #     # print("get proxy data", index, index.model())
    #     source_index = self.mapToSource(index)
    #     return self.sourceModel().data(source_index, role)

    # def setData(self, index, value, role):
    #     source_index = self.mapToSource(index)
    #     return self.sourceModel().setData(source_index, value, role)
    
    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            # return QModelIndex()
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            # print("create index for", row, column, childItem, childItem.display)
            return self.createIndex(row, column, childItem)
        return self.createIndex(row, column)
        # return QModelIndex()

    def mapFromSource(self, sourceIndex):
        if sourceIndex.isValid():
            source_item = sourceIndex.internalPointer()
            source_item_parent = source_item.parent()
            if source_item and source_item_parent:
                if source_item in source_item_parent.filter_childItems():
                    filter_index = source_item_parent.filter_childItems().index(source_item)
                    return self.index(filter_index, 0, self.mapFromSource(sourceIndex.parent()))
                else:
                    return QModelIndex() 
            # return self.index(sourceIndex.row(), 0, self.mapFromSource(sourceIndex.parent()))
            return QModelIndex()
        return QModelIndex()

    def mapToSource(self, proxyIndex):
        if proxyIndex.isValid():
            proxy_index = self.index(proxyIndex.row(), 0, proxyIndex.parent())
            proxy_item = proxy_index.internalPointer()
            if proxy_item:
                # print(proxy_item.display, "map TO source", proxy_index.row(), proxy_index.parent())
                return self.sourceModel().indexOf(proxy_item)
        return QModelIndex()
    
    #Program crashing without parent method, possibly should point to proxy index instead of source model?
    def parent(self, child_index):
        model_parent = self.sourceModel().parent(child_index)
        return self.mapFromSource(model_parent)

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