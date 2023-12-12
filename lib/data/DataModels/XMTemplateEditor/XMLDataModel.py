from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt, QMimeData, pyqtSignal
from .xml_object_definitions import transport_template

import json
from .ObjectDataItem import ObjectDataItem
from .XMLDataItem import XMLDataItem
from lib.ui.WidgetFactory.DialogScreens.MessageBox import MsgBox

class XMLDataModel(QAbstractItemModel):
    databaseObjectsLoaded = pyqtSignal(object, dict)
    xmlDataStructureChanged = pyqtSignal()
    modelItemChecked = pyqtSignal(object, str, int)

    def __init__(self, application, data_source, parent_widget=None, transport_template=None):
        super().__init__(parent_widget)
        self.application = application
        if transport_template is None:
            self.transport_template = transport_template(self)
        else:
            self.transport_template = transport_template
            
        self._headers = ["XML Transport Structure", "Options"]
        self.treeview = parent_widget
        self.export_file_path = data_source
        self.treeview.setWordWrap(True)

        self.rootItem = XMLDataItem(
            application=self.application, 
            object_class="RootItem", 
            xml_custom_object=self.transport_template, 
            model_reference=self)

        if data_source:
            parsing_status, status_message = self.transport_template.parse_xml_file(data_source)
            if parsing_status is False:
                if "document is empty" not in status_message.lower():
                    print("template parsing failed", status_message)
                    MsgBox(self.application, "XML Template Parsing Failed!", f"<b>File path:</b> {data_source}\n<b>Error Message:</b> {status_message}")

        data = self.transport_template.children()
        if data:
            self.setupModelData(data, self.rootItem)

        # connect model data signals 
        self.databaseObjectsLoaded.connect(self.onDatabaseObjectsLoaded)

        # save initial transport state
        self.fileSaved()

    def setupModelData(self, data, parent):
        """ Main method used to load all data into the model """
        for task_object in data:
            task_item = XMLDataItem(
                application=self.application, 
                xml_custom_object=task_object, 
                parent=parent,
                model_reference=self)
            parent.addChild(task_item)

    def reload_model_data(self):
        # print("reload model data")
        if self.export_file_path:
            self.beginResetModel()
            self.rootItem._children = []
            self.transport_template.parse_xml_file(self.export_file_path)
            data = self.transport_template.children()
            if data:
                self.setupModelData(data, self.rootItem)
            self.endResetModel()
        self.xmlDataStructureChanged.emit()

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
        column = index.column()
        column_name = self.headers[column]

        if role == Qt.ItemDataRole.DisplayRole:
            if isinstance(item, XMLDataItem):
                return item.display(column_name)

            if column_name == "XML Transport Structure":
                return item.display()
        if role == Qt.ItemDataRole.DecorationRole and column_name == "XML Transport Structure":
            return item.icon()
        if (isinstance(item, XMLDataItem) and item.isCheckable(column_name) 
            and role == Qt.ItemDataRole.CheckStateRole and column_name in ["Options"]):
                return item.checkState(column_name)

        if role == Qt.ItemDataRole.EditRole and column_name == "XML Transport Structure":
            return item.display(column_name)
        
        return None

    def setData(self, index, value, role):
        column = index.column()
        item = index.internalPointer()
        column_name = self.headerData(column)

        if column_name in ["Options"]:
            # option columns makes only the checkbox data changes
            item.setCheckState(column_name, value)
            self.modelItemChecked.emit(item, column_name, value)
        else:
            # otherwise set data directly
            if column_name == "XML Transport Structure":
                item.setDisplay(value)
            else:
                item.setData(column_name, value)

        self.dataChanged.emit(index, index)
        self.xmlDataStructureChanged.emit()
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled \
            | Qt.ItemFlag.ItemIsDropEnabled
        
        column_name = self.headers[index.column()]
        if column_name == "Options":
            option_display = self.data(index)
            if option_display and len(option_display.strip()) > 0:
                flags |= Qt.ItemFlag.ItemIsUserCheckable

        if column_name == "XML Transport Structure":
            option_display = self.data(index)
            if option_display and len(option_display.strip()) > 0:
                flags |= Qt.ItemFlag.ItemIsEditable

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
        return ["application/vnd.xmldataitem", "application/vnd.objectdataitem"]

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

        mimedata.setData("application/vnd.xmldataitem", encodedData)
        return mimedata

    def dropMimeData(self, data, action, row, column, parentIndex):
        if action == Qt.DropAction.IgnoreAction:
            return False

        # start = time.time()
        encodedData = data.data("application/vnd.xmldataitem")

        if len(encodedData) == 0:
            # if no xmldata is being dropped, it should be database object data drop
            encodedData = data.data("application/vnd.objectdataitem")

        if len(encodedData) == 0:
            # if not supported data type, break here
            return False

        decodedData = bytes(encodedData)
        jsondata = json.loads(decodedData)
        newItems = []
        source_items = []

        # print("Data dropped:", jsondata)

        if not parentIndex.isValid():
            # dropped at top level item
            parentItem = self.rootItem
            if data.hasFormat("application/vnd.objectdataitem"):
                parentItem = self.addTransportTask("VI.Transport.ObjectTransport, VI.Transport")
                parentIndex = self.indexOf(parentItem)
        else:
            parentItem = parentIndex.internalPointer()

        for dropped_item in jsondata:

            source_item_uid = dropped_item.get('uid', None)
            source_item = None
            if source_item_uid:
                # find the source Item and save it
                source_item = self.find_item_by_attribute("uid", source_item_uid)
                if source_item:
                    source_items.append(source_item)
                    
            if dropped_item.get("objectclass", None) == "TableDataItem":
                # do not include table data items
                continue
            # print("dropped item:", dropped_item)
            # create new object from the source item data and add it to the list, all dropped items will be inserted at once
            new_item = XMLDataItem(
                application=self.application,
                parent=parentItem,
                model_reference=self)
            newItems.append(new_item)
            
            #emit relocation signal for the new item and tell it about its source item from the same model
            # print(source_item.model_reference)
            if source_item and source_item.model_reference == self:
                new_item.locationChanged.emit(source_item)
            else:
                #emit new item from source signal to tell new item about source item data
                new_item.dataDropped.emit(dropped_item)
        
        #insert dropped items at new location
        self.insert_items(parentIndex, newItems, row, column)
        
        # for new_item in newItems:
        #     new_item.updateSortOrder()

        #remove source objects at once
        for source_item in source_items:
            self.remove_item(source_item)
        # end = time.time()

        for new_item in newItems:
            new_item.refreshModelStructure()

        self.xmlDataStructureChanged.emit()

        return True
    
    def insert_item(self, object_class, object_data, parentIndex=QModelIndex()):
        parentItem = self.rootItem
        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()  
        row = parentItem.childCount()
        newTask = [XMLDataItem(
            application=self.application, 
            object_class=object_class, 
            object_data=object_data,
            parent=parentItem,
            model_reference=self)]
        newTask[0].is_saved = False
        self.insert_items(parentIndex, newTask, row)

    def addTransportTask(self, task_type):
        transport_task_xml_object = self.transport_template.add_transport_task(task_type)
        task_item = self.add_xml_item(transport_task_xml_object)
        return task_item

    def addSQLScript(self, source_index, script_type):
        parentItem = None
        if source_index.isValid():
            parentItem = source_index.internalPointer() 
        
        if not parentItem and not parentItem._xml_data:
            return False

        script_xml_object = parentItem._xml_data.add_sql_script(script_type)
        self.add_xml_item(xml_object=script_xml_object, parentIndex=source_index)

    def add_xml_item(self, xml_object, parentIndex=QModelIndex()):
        parentItem = self.rootItem
        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()  
        row = parentItem.childCount()
        model_item = XMLDataItem(
            application=self.application,
            xml_custom_object=xml_object,
            parent=parentItem,
            model_reference=self)
        self.beginInsertRows(parentIndex, row, row + 1)
        parentItem.addChild(model_item, row)
        self.endInsertRows()
        self.layoutChanged.emit()
        self.xmlDataStructureChanged.emit()
        return model_item
    
    def insert_items(self, parentIndex, list_of_items, row=-1, column=-1, sort_children=False):
        parentItem = self.rootItem

        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()

        if row == -1 and column == -1:
            row = parentItem.childCount()
            column = 0
        # print("insert items at location", row, (row + len(list_of_items)-1))
        self.beginInsertRows(parentIndex, row, (row + len(list_of_items)-1) )
        parentItem.insertChildren(row, list_of_items)
        if sort_children:
            parentItem.sortChildren()
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
        if event.mimeData().hasFormat("application/vnd.xmldataitem"):
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

    def exportModelToJson(self):
        data = []
        root = self.rootItem
        for i in range(root.childCount()):
            group_item = root.child(i)
            group_data = group_item.task_data()
            data.append(group_data)
        jsondata = json.dumps(data, indent=4)
        return jsondata

    def exportXMLData(self):
        # This section is required to 'fix' the xml structures before the entire structure can be exported
        # In cases where the model data representation does not exactly match the target XML structures, 
        # the nodes which are not part of the model are being deleted from the transport template (broken parent chain most likely?). 
        # This mechanism allows for the existing, but detached elements to be restored in the xml structure
        
        for childItem in self.rootItem._children:
            # custom xml object classes are accessed through XMLDataItem objects
            # in this case the call is only executed for the top level items (transport tasks) 
            childItem.prepareExportData()

        # return entire transport template xml structure once all preparation tasks are completed
        return self.transport_template.string

    def isDifferent(self):
        return self.transport_template.string != self.transport_template_initial

    def fileSaved(self):
        self.transport_template_initial = self.transport_template.string

    def onDatabaseObjectsLoaded(self, source_object, object_data):
        data_items = []
        # print("database objects loaded", len(data_items))
        for table_name, results in object_data.items():
            table_display_name = table_name
            if self.application.db:
                table_display_name = self.application.db.table_info.get(table_name, table_name)
            # print(f"{table_name} table data loaded - ({len(results)})")
            table_data_item = ObjectDataItem(parent=source_object, application=self.application, table_data=table_display_name, object_data=results, model_reference=self)
            data_items.append(table_data_item)
        parentIndex = self.indexOf(source_object)
        self.treeview.setExpanded(parentIndex, True)
        self.insert_items(parentIndex=parentIndex, list_of_items=data_items, sort_children=True)
        

    

