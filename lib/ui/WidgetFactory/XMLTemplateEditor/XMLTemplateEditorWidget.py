# Standard modules
from pathlib import Path

#""" Required QT Libraries """
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6 import QtWidgets

# XML Management
from ..CodeEditors.XMLEditor import xml_editor
from .ContextMenu import XMLObjectContextMenu

# Data Models
from lib.data.DataModels import XMLDataItem, XMLDataModel, ObjectDataItem

XML_PREVIEW_TIMER = 100

class XMLTemplateEditorWidget(QtWidgets.QWidget):
    xml_structure_changed = pyqtSignal()

    def __init__(self, parent, application, file_path):
        super().__init__()
        self.parent = parent
        self.application = application
        self.current_file = file_path
        self.setupUi()

        # Initial refresh
        self.loadXMLStructureView()
        self.refreshXMLPreview()
        self.xml_structure_changed.connect(self.refreshXMLPreview)

    def reloadXMLFile(self):
        self.XMLStructureTreeView.model().reload_model_data()

    def reloadXMLPreview(self):
        self.XMLPreviewBrowser.setText(self.XMLStructureTreeView.model().exportXMLData())
        self.loadXMLStructureView()

    def loadXMLStructureView(self):
        data_model =  XMLDataModel(
            application=self.application,
            parent_widget=self.XMLStructureTreeView,
            data_source=self.current_file)

        self.XMLStructureTreeView.setModel(data_model)
        data_model.xmlDataStructureChanged.connect(self.xml_structure_changed)

    def refreshXMLPreview(self):
        print("refresh xml preview")
        self.XMLPreviewBrowser.setText(self.XMLStructureTreeView.model().exportXMLData())
        self.XMLPreviewBrowser.reconfigure_editor()
        self.setCurrentXMLTemplate()

    def saveXMLTemplate(self):
        if self.current_file is not None:
            # print(Path(self.current_file), Path(self.current_file).is_file())
            if Path(self.current_file).is_file():
                Path(self.current_file).parent.mkdir(parents=True, exist_ok=True)
                with open(self.current_file, 'w') as doc:
                    doc.write(self.XMLStructureTreeView.model().exportXMLData())
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
            self.setCurrentXMLTemplate(file_path[0])
            return file_path[0]
        return False

    def setCurrentXMLTemplate(self):          
        if self.current_file:
            self.current_file_label.setText(str(self.current_file))

    def xmlContextMenuRequested(self, menuPosition):
        clickedIndex = self.XMLStructureTreeView.indexAt(menuPosition)
        clickedItem = clickedIndex.internalPointer()
        if isinstance(clickedItem, ObjectDataItem):
            return False

        contextMenu = XMLObjectContextMenu(
            parent=self, 
            source_index=clickedIndex)
        
        contextMenu.onListRelatedObjectData.connect(lambda: self.listRelatedObjectData(
            source_index = clickedIndex, 
            override = True))

        contextMenu.onLoadDatabaseObject.connect(self.loadDatabaseObject)
        contextMenu.onSaveRelationPreset.connect(self.saveRelationPreset)
        contextMenu.onAddTransportTask.connect(self.addTransportTask)
        contextMenu.onAddSQLScript.connect(self.addSQLScript)
        contextMenu.onEditSQLScript.connect(self.editSQLScript)

        if len(contextMenu.menu_items) > 0:
            menu_target = self.XMLStructureTreeView.mapToGlobal(menuPosition)
            contextMenu.popup(menu_target)
    
    """ Context Menu handling functions  """

    def loadDatabaseObject(self, source_index):
        for source_index in self.XMLStructureTreeView.selectedIndexes():
            if source_index.isValid():
                source_item = source_index.internalPointer()
                if source_item.xml_object_class == "Transport_Object":
                    source_item.loadDatabaseObject()

        if len(self.XMLStructureTreeView.selectedIndexes()) == 0 and source_index.isValid():
            source_item = source_index.internalPointer()
            if source_item.xml_object_class == "Transport_Object":
                source_item.loadDatabaseObject()

    def listRelatedObjectData(self, source_index, override=False):
        for source_index in self.XMLStructureTreeView.selectedIndexes():
            if source_index.isValid():
                source_item = source_index.internalPointer()
                if source_item.xml_object_class == "Transport_Object":
                    source_item.listRelatedObjectData()
        
        if len(self.XMLStructureTreeView.selectedIndexes()) == 0 and source_index.isValid():
            source_item = source_index.internalPointer()
            if source_item.xml_object_class == "Transport_Object":
                source_item.listRelatedObjectData()
 
    def saveRelationPreset(self, source_index):
        pass

    def addTransportTask(self, source_index):
        pass

    def addSQLScript(self, source_index):
        pass

    def editSQLScript(self, source_index):
        pass

    def XMLStructureDragMoveEvent(self, event):
        move_accept = False
        source_index = event.source().currentIndex()
        source_item = source_index.internalPointer()

        QtWidgets.QTreeView.dragMoveEvent(self.XMLStructureTreeView, event)
        
        drop_index = self.XMLStructureTreeView.indexAt(event.position().toPoint())
        drop_item = drop_index.internalPointer()

        dropIndicator = self.XMLStructureTreeView.dropIndicatorPosition()

        if drop_item:
            self.XMLStructureTreeView.setDropIndicatorShown(True)
        
        if isinstance(source_item, XMLDataItem) and isinstance(drop_item, XMLDataItem):
            if dropIndicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.OnItem:
                if drop_item and source_item:
                    if source_item.xml_object_class == "Transport_Object" and drop_item.xml_object_class == "Object_Transport_Task":
                        move_accept = True

            if dropIndicator in [QtWidgets.QAbstractItemView.DropIndicatorPosition.BelowItem, QtWidgets.QAbstractItemView.DropIndicatorPosition.AboveItem]:
                if drop_item.xml_object_class == source_item.xml_object_class:
                    move_accept = True

        if drop_item is None and isinstance(source_item, XMLDataItem):
            # no target item - drop at top level
            if source_item.xml_object_class in ["Object_Transport_Task"]:
                move_accept = True

        if event.mimeData().hasFormat("application/vnd.xmldataitem") and move_accept:
            event.acceptProposedAction()
        else:
            event.ignore()

    def setupUi(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.mainSplitter = QtWidgets.QSplitter(self)
        self.layout.addWidget(self.mainSplitter, 0, 0, 1, 1)
        
        self.mainSplitter.setOrientation(Qt.Orientation.Horizontal)
        self.mainSplitter.setObjectName("XMLTemplateEditorWidgetSplitter")

        self.XMLStructureTreeView = QtWidgets.QTreeView(self.mainSplitter)
        self.XMLStructureTreeView.setObjectName("XMLStructureTreeView")
        # self.XMLStructureTreeView.header().setStretchLastSection(False)
        self.XMLStructureTreeView.setHeaderHidden(False)   
        self.XMLStructureTreeView.setSortingEnabled(False)
        self.XMLStructureTreeView.setWordWrap(True)
        self.XMLStructureTreeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.XMLStructureTreeView.customContextMenuRequested.connect(self.xmlContextMenuRequested)

        self.XMLStructureTreeView.dragMoveEvent = self.XMLStructureDragMoveEvent
        self.XMLStructureTreeView.setHeaderHidden(True)
        self.XMLStructureTreeView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.XMLStructureTreeView.setDragEnabled(True)
        self.XMLStructureTreeView.setAcceptDrops(True)
        self.XMLStructureTreeView.setUniformRowHeights(False)
        self.XMLStructureTreeView.setDropIndicatorShown(True)
        self.XMLStructureTreeView.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragDrop)

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
        self.xml_preview_timer.timeout.connect(self.reloadXMLPreview)
        self.xml_structure_changed.connect(self.refreshXMLPreview)