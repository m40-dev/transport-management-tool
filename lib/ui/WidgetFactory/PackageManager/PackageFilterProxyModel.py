from PyQt6 import QtCore
from PyQt6.QtCore import QModelIndex

class PackageFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, application, source_model, parent):
        super().__init__(parent=parent)
        self.application = application
        self.filterString = ""
        self.setRecursiveFilteringEnabled(True)
        self.rootItem = source_model.modelDataClass(application=application, task_class="RootItem")
        self.setSourceModel(source_model)

    def setFilterString(self, string):
        self.filterString = string
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if len(self.filterString) <= 3:
            return True
        
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        # index = self.index(source_row, 0, source_parent)
        if index.isValid():
            item = index.internalPointer()
            return self.check_conditions(item)
        return False

    def check_conditions(self, item):
        item_match = self.filterString.lower() in item.display.lower()

        print("checking:", item.display, "filter:", self.filterString, "match:", item_match)

        if item_match:
            return True
        return False

    #Example from stackoverflow
    # def index(self, row, column, parent=QtCore.QModelIndex()):
    #     return self.createIndex(row, column)

    # def mapFromSource(self, sourceIndex):
    #     if sourceIndex.isValid()  and 0 <= sourceIndex.row() < self.rowCount():
    #         ix = self.sourceModel().index(sourceIndex.row(), 0)
    #         return self.index(int(ix.data()), sourceIndex.column())
    #     return QtCore.QModelIndex()

    # def mapToSource(self, proxyIndex):
    #     res = self.sourceModel().match(self.sourceModel().index(0, 0), QtCore.Qt.ItemDataRole.DisplayRole, proxyIndex.row(), flags=QtCore.Qt.MatchFlag.MatchExactly)
    #     if res:
    #         return res[0].sibling(res[0].row(), proxyIndex.column())
    #     return QtCore.QModelIndex()

    
    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            # return QModelIndex()
            parentItem = self.sourceModel().rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, 0, childItem)

        return QModelIndex()

    def mapFromSource(self, sourceIndex):
        if sourceIndex.isValid():
            # return sourceIndex
            source_item = sourceIndex.internalPointer()
            proxy_item = self.sourceModel().find_item_by_attribute("uid", source_item.uid)
            if proxy_item:
                proxy_index = self.sourceModel().indexOf(proxy_item)
                return proxy_index
            return sourceIndex
        return QModelIndex()
        

    def mapToSource(self, proxyIndex):
        if proxyIndex.isValid():
            proxy_item = proxyIndex.internalPointer()
            if proxy_item:
                # print("map to source: ", proxy_item.display, proxy_item.uid, proxy_item, proxyIndex)
                source_item = self.sourceModel().find_item_by_attribute("uid", proxy_item.uid)
                if source_item:
                    source_index = self.sourceModel().indexOf(source_item)
                    # print("source item found:", source_item, "index: ", source_index)
                    if source_index.isValid():
                        return source_index
                # return proxyIndex
        return QModelIndex()
    
    #Program crashing without parent method, possibly should point to proxy index instead of source model?
    def parent(self, index):
        return self.sourceModel().parent(index)

