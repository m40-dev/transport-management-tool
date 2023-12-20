# Standard modules
from pathlib import Path
from copy import deepcopy
import json

#""" Required QT Libraries """
from PyQt6.QtCore import pyqtSignal, QTimer, Qt, QMimeData, QSize
from PyQt6 import QtWidgets

# XML Management
from ..CodeEditors.XMLEditor import xml_editor
from .ContextMenu import XMLObjectContextMenu, ObjectDataItemContextMenu
from ..DialogScreens import ScriptEditorDialog

# Data Models
from lib.data.DataModels import XMLDataItem, XMLDataModel, ObjectDataItem, TASKS
from lib.data.DataModels.XMTemplateEditor.xml_object_definitions import transport_template
# Custom Widgets
from lib.ui.WidgetFactory import FormEditorDialog


XML_PREVIEW_TIMER = 100

class XMLTemplateEditorWidget(QtWidgets.QWidget):
    xmlStructureChanged = pyqtSignal()

    def __init__(self, parent, application, file_path):
        super().__init__()
        self.parent = parent
        self.application = application
        self.current_file = file_path
        self.setupUi()
        self.transport_template = transport_template(self)

        # Initial refresh

        self.loadXMLStructureView()
        self.onXMLPreviewRefresh()
        
        self.xmlStructureChanged.connect(self.onXMLPreviewRefresh)
        self.XMLStructureTreeView.mousePressEvent = self.XMLStructureTreeViewMousePressEvent
        self.XMLStructureTreeView.setWordWrap(True)
        self.parent.refreshUi.connect(self.refresh_ui)
        self.setStyleSheet(self.application.styleSheet())


    def XMLStructureTreeViewMousePressEvent(self, event):
        QtWidgets.QTreeView.mousePressEvent(self.XMLStructureTreeView, event)

        target_index = self.XMLStructureTreeView.indexAt(event.position().toPoint())
        if target_index.isValid():
            self.onCurrentIndexChanged(target_index)
        else:
            self.onCurrentIndexChanged(None)
        
    @property
    def display(self):
        display_name = "New Template"
        if self.current_file:
            display_name = Path(self.current_file).name
        return display_name
    


    def reloadXMLFile(self):
        self.XMLStructureTreeView.model().reload_model_data()

    def loadXMLStructureView(self):
        data_model =  XMLDataModel(
            application=self.application,
            parent_widget=self.XMLStructureTreeView,
            data_source=self.current_file,
            transport_template=self.transport_template)
        
        self.XMLStructureTreeView.setModel(data_model)
        data_model.xmlDataStructureChanged.connect(self.xmlStructureChanged)
        data_model.modelItemChecked.connect(self.onItemCheckStateChange)
        self.setCurrentXMLTemplate()

        self.XMLStructureTreeView.header().resizeSection(0, round(self.application.width() * 0.25))
        self.XMLStructureTreeView.header().resizeSection(1, round(self.application.width() * 0.18))

    def onXMLPreviewRefresh(self):
        self.xml_preview_timer.start(XML_PREVIEW_TIMER)

    def refreshXMLPreview(self):
        self.XMLPreviewBrowser.setText(self.XMLStructureTreeView.model().exportXMLData())
    
    def refresh_ui(self):
        self.XMLPreviewBrowser.setText(self.XMLStructureTreeView.model().exportXMLData())
        self.XMLPreviewBrowser.reconfigure_editor()
        self.setCurrentXMLTemplate()
        self.setStyleSheet(self.application.styleSheet())
        # self.XMLStructureTreeView.setStyleSheet(self.styleSheet())

    def saveXMLTemplate(self):
        if self.current_file:
            # print(Path(self.current_file), Path(self.current_file).is_file())
            if Path(self.current_file).is_file():
                Path(self.current_file).parent.mkdir(parents=True, exist_ok=True)
                with open(self.current_file, 'w') as doc:
                    doc.write(self.XMLStructureTreeView.model().exportXMLData())
                    # doc.write(self.transport_template.string)
                self.XMLStructureTreeView.model().fileSaved()
                return self.current_file
            return self.saveXMLTemplateAs(self.current_file)
        return self.saveXMLTemplateAs(self.application.current_workdir)

    def saveXMLTemplateAs(self, initial_directory=None):
        dialog = QtWidgets.QFileDialog(self, "Save As")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile) 

        file_path = dialog.getSaveFileName(
            filter="*.xml", 
            directory=str(initial_directory))

        if file_path[0] != "":
            with open(file_path[0], 'w') as doc:
                doc.write(self.XMLStructureTreeView.model().exportXMLData())
                # doc.write(self.transport_template.string)
            self.current_file = file_path[0]
            self.parent.tabNameChanged.emit(self)
            self.setCurrentXMLTemplate()
            self.XMLStructureTreeView.model().fileSaved()
            return file_path[0]
        return False

    def setCurrentXMLTemplate(self, file_path=None):
        if self.current_file:
            self.current_file_label.setText(str(self.current_file))

    def xmlContextMenuRequested(self, menuPosition):
        clickedIndex = self.XMLStructureTreeView.indexAt(menuPosition)
        clickedItem = clickedIndex.internalPointer()
        if isinstance(clickedItem, ObjectDataItem):
            contextMenu = ObjectDataItemContextMenu(
                parent=self.application, 
                source_index=clickedIndex)

            contextMenu.onQueryTableData.connect(self.queryTaskData)
            if len(contextMenu.menu_items) > 0:
                menu_target = self.XMLStructureTreeView.mapToGlobal(menuPosition)
                contextMenu.popup(menu_target)
            
            return

        contextMenu = XMLObjectContextMenu(
            parent=self.application, 
            source_index=clickedIndex)
        
        contextMenu.onListRelatedObjectData.connect(lambda: self.listObjectDataRequested(
            source_index = clickedIndex, 
            override = True))

        contextMenu.onLoadDatabaseObject.connect(self.loadDatabaseObject)
        contextMenu.onSaveRelationPreset.connect(self.saveRelationPreset)
        contextMenu.onAddTransportTask.connect(self.addTransportTask)
        contextMenu.onAddSQLScript.connect(self.addSQLScript)
        contextMenu.onEditSQLScript.connect(self.editSQLScript)
        contextMenu.onCopySelectedNodes.connect(self.copyXMLNodes)
        contextMenu.onPasteSelectedNodes.connect(self.pasteSelectedNodes)
        contextMenu.onQueryTableData.connect(self.queryTaskData)

        if len(contextMenu.menu_items) > 0:
            menu_target = self.XMLStructureTreeView.mapToGlobal(menuPosition)
            contextMenu.popup(menu_target)

    """ Context Menu handling functions  """
    def queryTaskData(self, source_index):
        if source_index.isValid():
            source_item = source_index.internalPointer()
            if isinstance(source_item, (XMLDataItem, ObjectDataItem)):
                self.parent.tableSelectionRequested.emit(source_item.table_name)
                
    def pasteSelectedNodes(self, target_index):
        mimeData = self.application.clipboard.mimeData()
        xml_model = self.XMLStructureTreeView.model()

        encodedData = mimeData.data("application/vnd.xmldataitem")

        if len(encodedData) == 0:
            # if no xmldata is being dropped, it should be database object data drop
            encodedData = mimeData.data("application/vnd.objectdataitem")

        if len(encodedData) == 0:
            # if not supported data type, break here
            return False

        if not target_index.isValid():
            # dropped at top level item
            parentItem = xml_model.rootItem
            # if mimeData.hasFormat("application/vnd.objectdataitem"):
            #     parentItem = xml_model.addTransportTask("VI.Transport.ObjectTransport, VI.Transport")
            #     target_index = xml_model.indexOf(parentItem)
        else:
            parentItem = target_index.internalPointer()

        decodedData = bytes(encodedData)
        jsondata = json.loads(decodedData)
        # print("pasted data",jsondata)
        newItems = []
        for source_object in jsondata:
            new_item = XMLDataItem(
                application=self.application,
                parent=parentItem,
                model_reference=xml_model,
                )
            newItems.append(new_item)
            new_item.fromString(source_object["xml_data"], source_object["xml_object_class"])
            object_relations = source_object.get("object_relations", None)
            if object_relations:
                new_item.object_relations = object_relations
        
        #insert dropped items at new location
        xml_model.insert_items(target_index, newItems)

        for new_item in newItems:
            new_item.refreshModelStructure()

        xml_model.xmlDataStructureChanged.emit()

    def copyXMLNodes(self):
        selected_xml_items = self.selectedItems(object_class=XMLDataItem)

        mimedata = QMimeData()
        items_data = []

        for source_item in selected_xml_items:
            task_data = source_item.task_data()
            
            if task_data not in items_data:
                items_data.append(task_data)

        items_data_sorted = sorted(
                            items_data, 
                            key=lambda d: (d.get("row", ""))
                            )
        
        jsondata = json.dumps(items_data_sorted, indent=4)
        encodedData = jsondata.encode('utf-8')

        mimedata.setData("application/vnd.xmldataitem", encodedData)
        self.application.clipboard.setMimeData(mimedata)

    def loadDatabaseObject(self, source_index):
        selected_xml_items = self.selectedItems(object_class=XMLDataItem)
        for source_item in selected_xml_items:
            if source_item.xml_object_class == "Transport_Object":
                source_item.loadDatabaseObject()

        if len(selected_xml_items) == 0 and source_index.isValid():
            source_item = source_index.internalPointer()
            if isinstance(source_item, XMLDataItem) and source_item.xml_object_class == "Transport_Object":
                source_item.loadDatabaseObject()
        self.parent.reloadDatabaseRelations(source_index)

    def listObjectDataRequested(self, source_index, override=False):
        for source_item in self.selectedItems(object_class=XMLDataItem):
            source_item.listObjectData(override)

            # if source_item.xml_object_class == "Transport_Object":
            #     source_item.listRelatedObjectData(override)
        
        if len(self.XMLStructureTreeView.selectedIndexes()) == 0 and source_index.isValid():
            source_item = source_index.internalPointer()
            source_item.listObjectData(override)

            # if source_item.xml_object_class == "Transport_Object":
            #     source_item.listRelatedObjectData(override)
 
    def saveRelationPreset(self, source_index):
        if not source_index.isValid():
            return False

        source_item = source_index.internalPointer()
        if source_item and source_item.xml_object_class != "Transport_Object":
            return False

        dialog = FormEditorDialog(self.application, "XMLTemplateEditor_RelationPreset")
        if dialog.exec():
            preset_data = dialog.form_data
            preset_data["table_relations"] = deepcopy(source_item.object_relations)
            
            self.application.relationPresetAdded(
                source_item.table_name, 
                preset_data["name"], 
                preset_data)

    def addTransportTask(self, task_type):
        self.XMLStructureTreeView.model().addTransportTask(task_type)

    def addSQLScript(self, source_index, script_type):
        self.XMLStructureTreeView.model().addSQLScript(source_index, script_type)

    def editSQLScript(self, source_index):
        if not source_index.isValid():
            return False

        source_item = source_index.internalPointer()
        if source_item and source_item.xml_object_class != "Transport_SQL_Object":
            return False

        dialog = ScriptEditorDialog(self.application, source_item.script)
        if dialog.exec():
            source_item.script = dialog.script
            self.xmlStructureChanged.emit()

    def XMLStructureDragMoveEvent(self, event):
        move_accept = False
        source_index = event.source().currentIndex()
        source_item = source_index.internalPointer()

        QtWidgets.QTreeView.dragMoveEvent(self.XMLStructureTreeView, event)
        
        drop_index = self.XMLStructureTreeView.indexAt(event.position().toPoint())
        drop_item = drop_index.internalPointer()

        dropIndicator = self.XMLStructureTreeView.dropIndicatorPosition()
        
        # Internal Move between XML Data structure nodes
        if isinstance(source_item, XMLDataItem) and isinstance(drop_item, XMLDataItem):
            if dropIndicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.OnItem:
                # print(drop_item.xml_object_class)
                if (
                    # Check target accepted classes
                    (source_item.xml_object_class in drop_item.accepted_classes or len(drop_item.accepted_classes) == 0)
                    # Check target accepted tables
                    and (source_item.table_name in drop_item.accepted_tables or len(drop_item.accepted_tables) == 0)
                    # Drop Allowed ON task objects only
                    and (drop_item.xml_object_class in TASKS.keys())
                    
                ):
                    move_accept = True

            if dropIndicator in [QtWidgets.QAbstractItemView.DropIndicatorPosition.BelowItem, QtWidgets.QAbstractItemView.DropIndicatorPosition.AboveItem]:
                if (
                    (source_item.xml_object_class in drop_item.accepted_classes or len(drop_item.accepted_classes) == 0)
                    and (source_item.table_name in drop_item.accepted_tables or len(drop_item.accepted_tables) == 0)
                    and (drop_item.xml_object_class not in TASKS.keys())
                ):
                    move_accept = True
                # alternatively check if we are moving top level items, making reorganization allowed
                if (
                    (source_item.xml_object_class in TASKS.keys())
                    and (drop_item.xml_object_class in TASKS.keys())
                ):
                    move_accept = True
        
        # Adding new elements from the database records list
        if (isinstance(source_item, ObjectDataItem) and isinstance(drop_item, XMLDataItem)): # and source_item.model_reference != drop_item.model_reference:
            # print(source_item.object_class, source_item.table_name, drop_item.accepted_tables, drop_item.xml_object_class)
            if dropIndicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.OnItem:
                if (
                    (source_item.table_name in drop_item.accepted_tables or len(drop_item.accepted_tables) == 0)
                    # check if source object class is accepted
                    and (source_item.object_class in drop_item.accepted_classes or len(drop_item.accepted_classes) == 0)
                    # Drop Allowed ON task objects only
                    and (drop_item.xml_object_class in TASKS.keys())
                ):
                    move_accept = True
            
            if dropIndicator in [QtWidgets.QAbstractItemView.DropIndicatorPosition.BelowItem, QtWidgets.QAbstractItemView.DropIndicatorPosition.AboveItem]:
                if (
                    (source_item.table_name in drop_item.accepted_tables or len(drop_item.accepted_tables) == 0)
                    # check if source object class is accepted
                    and (source_item.object_class in drop_item.accepted_classes or len(drop_item.accepted_classes) == 0)
                ):
                    move_accept = True

        # no target item - internal move to the top level, only task items can be rearranged to top level
        if drop_item is None and isinstance(source_item, XMLDataItem):
            if source_item.xml_object_class in TASKS.keys():
                move_accept = True
        
        # no target item - drop new item at top level
        if drop_item is None and isinstance(source_item, ObjectDataItem) and source_item.model_reference != self.XMLStructureTreeView.model():
            move_accept = True

        if (event.mimeData().hasFormat("application/vnd.xmldataitem") or event.mimeData().hasFormat("application/vnd.objectdataitem")) and move_accept:
            event.acceptProposedAction()
        else:
            event.ignore()

    def onCurrentIndexChanged(self, current_index=None):
        if current_index:
            itemClicked = current_index.internalPointer()
        else:
            return self.parent.reloadDatabaseRelations(None)

        if itemClicked and isinstance(itemClicked, XMLDataItem) and itemClicked.xml_object_class == "Transport_Object":
            self.parent.reloadDatabaseRelations(current_index)
        else:
            self.parent.reloadDatabaseRelations(None)

        if isinstance(itemClicked, XMLDataItem):
            display_text = itemClicked.display("XML Transport Structure")
            self.XMLPreviewBrowser.find_text(display_text)

    def onItemCheckStateChange(self, source_item, column_name, check_state):
        if column_name != "Options":
            return False

        for selected_item in self.selectedItems():
            if type(selected_item) == type(source_item) and selected_item != source_item and selected_item.xml_object_class == source_item.xml_object_class:
                selected_item.setCheckState(column_name, check_state)
        self.XMLStructureTreeView.model().layoutChanged.emit()

    def selectedItems(self, object_class=None):
        selected_items = []
        selected_indexes = self.XMLStructureTreeView.selectionModel().selectedRows()
        if len(selected_indexes) > 0:
            for index in selected_indexes:
                if not index.isValid():
                    continue
                item = index.internalPointer()
                if object_class:
                    if not isinstance(item, object_class):
                        continue

                if item and item not in selected_items:
                    selected_items.append(item)
        return selected_items

    def deleteSelectedItems(self):
        if not self.XMLStructureTreeView.hasFocus():
            return False

        selected_items = self.selectedItems()
        for item in selected_items:
            item.removeItem()

        self.xmlStructureChanged.emit()
        self.XMLStructureTreeView.model().layoutChanged.emit()

    def setupUi(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.mainSplitter = QtWidgets.QSplitter(self)
        
        self.layout.addWidget(self.mainSplitter, 0, 0, 1, 1)
        
        self.mainSplitter.setOrientation(Qt.Orientation.Horizontal)
        self.mainSplitter.setObjectName("XMLTemplateEditorWidgetSplitter")

        self.XMLStructureTreeView = QtWidgets.QTreeView(self.mainSplitter)
        self.XMLStructureTreeView.setObjectName("XMLStructureTreeView")
        self.XMLStructureTreeView.setProperty("Widget", "XMLTemplateEditorWidget")
        self.XMLStructureTreeView.header().setProperty("Widget", "XMLTemplateEditorWidget")
        self.XMLStructureTreeView.setSortingEnabled(False)
        self.XMLStructureTreeView.setWordWrap(True)
        self.XMLStructureTreeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.XMLStructureTreeView.customContextMenuRequested.connect(self.xmlContextMenuRequested)
        self.XMLStructureTreeView.dragMoveEvent = self.XMLStructureDragMoveEvent
        self.XMLStructureTreeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        # self.XMLStructureTreeView.setHeaderHidden(True)
        self.XMLStructureTreeView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.XMLStructureTreeView.setDragEnabled(True)
        self.XMLStructureTreeView.setAcceptDrops(True)
        self.XMLStructureTreeView.setUniformRowHeights(False)
        self.XMLStructureTreeView.setDropIndicatorShown(True)
        self.XMLStructureTreeView.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragDrop)
        self.XMLStructureTreeView.header().setStretchLastSection(False)
        self.XMLStructureTreeView.setIconSize(QSize(25,25))
        # self.XMLStructureTreeView.setDropIndicatorShown(True)

        self.verticalLayoutWidget = QtWidgets.QWidget(self.mainSplitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.XMLEditorLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.XMLEditorLayout.setContentsMargins(0, 0, 0, 0)
        self.XMLEditorLayout.setSpacing(0)
        self.XMLEditorLayout.setObjectName("XMLEditorLayout")
        
        self.XMLPreviewBrowser = xml_editor(self.application)
        self.current_file_label = QtWidgets.QLabel(self)
        self.current_file_label.setProperty("Widget", "FilePathLabel")
        self.current_file_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.current_file_label.setWordWrap(True)
        self.XMLEditorLayout.insertWidget(0, self.current_file_label)
        self.XMLEditorLayout.insertWidget(1, self.XMLPreviewBrowser)

        # XML Preview Handling
        self.xml_preview_timer = QTimer(self)
        self.xml_preview_timer.setSingleShot(True)
        self.xml_preview_timer.timeout.connect(self.refreshXMLPreview)
        self.xmlStructureChanged.connect(self.onXMLPreviewRefresh)

        # adjust UI Sections and widget sizes
        self.mainSplitter.setSizes([round(self.application.width()*0.6), round(self.application.width()*0.45)])
    
    def onWidgetClose(self):
        if self.XMLStructureTreeView.model().isDifferent():
            decision = QtWidgets.QMessageBox.question(self.application, "Save Changes?", f"Do you want to save changes before closing?")
            if decision == QtWidgets.QMessageBox.StandardButton.Yes:
                self.saveXMLTemplate()
        self.XMLPreviewBrowser.parent = None
        self.application = None
        self.parent = None
        self.current_file = None
        self.deleteLater()