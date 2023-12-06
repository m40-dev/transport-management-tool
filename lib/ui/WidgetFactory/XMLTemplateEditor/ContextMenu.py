from PyQt6.QtWidgets import (QMenu)
from PyQt6.QtCore import pyqtSignal

class RelationContextMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    onFollowTableRelation = pyqtSignal(object)

    def __init__(self, parent, source_index):
        super(RelationContextMenu, self).__init__(parent=parent)
        self.parent = parent
        self.menu_items = []

        if source_index and source_index.isValid():
            source_item = source_index.internalPointer()
            if source_item.follow_table:
                menuActionFollowRelation = self.addAction(f"Add Table Relations: {source_item.follow_table}")
                menuActionFollowRelation.triggered.connect(lambda: self.onFollowTableRelation.emit(source_index))

OBJECT_LISTING_TABLES = ["DialogTag"]

class XMLObjectContextMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    onListRelatedObjectData = pyqtSignal(object)
    onLoadDatabaseObject = pyqtSignal(object)
    onSaveRelationPreset = pyqtSignal(object)
    onAddTransportTask = pyqtSignal(str)
    onEditSQLScript = pyqtSignal(object)
    onAddSQLScript = pyqtSignal(object, str)
    onCopySelectedNodes = pyqtSignal()
    onPasteSelectedNodes = pyqtSignal(object)
    onQueryTableData = pyqtSignal(object)

    def __init__(self, parent, source_index):
        super(XMLObjectContextMenu, self).__init__()
        self.parent = parent
        self.menu_items = []

        #clicked on a specific object
        if source_index and source_index.isValid():
            source_item = source_index.internalPointer()
            print("object clicked", source_item.xml_object_class)
            
            # Prepare Transport Object specific menu items
            if source_item.xml_object_class == "Transport_Object" or (source_item.xml_object_class == "Table_Object_Reference" and source_item.table_name in OBJECT_LISTING_TABLES):
                menuActionListRelatedObjectData = self.addAction("List Related Objects")
                menuActionListRelatedObjectData.triggered.connect(lambda: self.onListRelatedObjectData.emit(source_index))
                
                self.addSeparator()

                menuActionLoadDatabaseObject = self.addAction("Load Object From Database")
                menuActionLoadDatabaseObject.triggered.connect(lambda: self.onLoadDatabaseObject.emit(source_index))
                
                menuActionSavePreset = self.addAction("Save Relations as Preset")
                menuActionSavePreset.triggered.connect(lambda: self.onSaveRelationPreset.emit(source_index) )
                
                self.menu_items.append(menuActionListRelatedObjectData)
                self.menu_items.append(menuActionLoadDatabaseObject)
                self.menu_items.append(menuActionSavePreset)
            
            if source_item.xml_object_class == "VI.Transport.TagTransport, VI.Transport":
                # Configure Task menu options
                menuQueryDatabaseObject = self.addAction("Find Task objects")
                menuQueryDatabaseObject.triggered.connect(lambda: self.onQueryTableData.emit(source_index))
                self.menu_items.append(menuQueryDatabaseObject)

            if source_item.xml_object_class == "VI.Transport.FileTransport, VI.Transport":
                # Configure Task menu options
                menuQueryDatabaseObject = self.addAction("Find Task objects")
                menuQueryDatabaseObject.triggered.connect(lambda: self.onQueryTableData.emit(source_index))
                self.menu_items.append(menuQueryDatabaseObject)
                
            if source_item.xml_object_class == "VI.Transport.DPR.ShellTransport, VI.Transport.DPR":
                # Configure Task menu options
                menuQueryDatabaseObject = self.addAction("Find Task objects")
                menuQueryDatabaseObject.triggered.connect(lambda: self.onQueryTableData.emit(source_index))
                self.menu_items.append(menuQueryDatabaseObject)


            self.addSeparator()

            menuActionCopyNodes = self.addAction("Copy Selected Nodes")
            menuActionCopyNodes.triggered.connect(lambda: self.onCopySelectedNodes.emit() )  
            self.menu_items.append(menuActionCopyNodes)

            menuActionPasteNodes = self.addAction("Paste Selected Nodes")
            menuActionPasteNodes.triggered.connect(lambda: self.onPasteSelectedNodes.emit(source_index) )  
            self.menu_items.append(menuActionPasteNodes)

            self.addSeparator()

            # Prepare SQL Script object context Menu
            if source_item.xml_object_class == "Transport_SQL_Object":
                menuActionEditSQLScript = self.addAction("Edit SQL Script")
                menuActionEditSQLScript.triggered.connect(lambda: self.onEditSQLScript.emit(source_index))
                self.menu_items.append(menuActionEditSQLScript)

            # Prepare SQL Task context Menu
            if source_item.xml_object_class == "VI.Transport.SQLTransport, VI.Transport":
                if source_item._xml_data.common_sql is None:
                    menuActionAddSQLScript = self.addAction("Add System SQL Script (CommonSQL)")
                    menuActionAddSQLScript.triggered.connect(lambda: self.onAddSQLScript.emit(source_index, "CommonSQL"))
                    self.menu_items.append(menuActionAddSQLScript)
                
                if source_item._xml_data.payload_sql is None:
                    menuActionAddPayloadSQLScript = self.addAction("Add User Data SQL Script (PayloadSQL)")
                    menuActionAddPayloadSQLScript.triggered.connect(lambda: self.onAddSQLScript.emit(source_index, "PayloadSQL"))
                    self.menu_items.append(menuActionAddPayloadSQLScript)
        
        # no index, white space clicked
        if not source_index.isValid():

            menuActionPasteNodes = self.addAction("Paste Selected Nodes")
            menuActionPasteNodes.triggered.connect(lambda: self.onPasteSelectedNodes.emit(source_index) )  

            self.menu_items.append(menuActionPasteNodes)

            self.addSeparator()

            menuTransportTask = self.addMenu("Add Transport Task")
            
            menuActionAddObjectTransportTask = menuTransportTask.addAction("Add Object Transport Task")
            menuActionAddObjectTransportTask.triggered.connect(lambda: self.onAddTransportTask.emit("VI.Transport.ObjectTransport, VI.Transport"))

            menuActionAddSQLTransportTask = menuTransportTask.addAction("Add SQL Transport Task")
            menuActionAddSQLTransportTask.triggered.connect(lambda: self.onAddTransportTask.emit("VI.Transport.SQLTransport, VI.Transport"))

            menuActionAddTagTransportTask = menuTransportTask.addAction("Add Change Label Transport Task")
            menuActionAddTagTransportTask.triggered.connect(lambda: self.onAddTransportTask.emit("VI.Transport.TagTransport, VI.Transport"))

            menuActionAddFileTransportTask = menuTransportTask.addAction("Add File Transport Task")
            menuActionAddFileTransportTask.triggered.connect(lambda: self.onAddTransportTask.emit("VI.Transport.FileTransport, VI.Transport"))

            menuActionShellTransportTask = menuTransportTask.addAction("Add Synchronization Project Transport Task")
            menuActionShellTransportTask.triggered.connect(lambda: self.onAddTransportTask.emit("VI.Transport.DPR.ShellTransport, VI.Transport.DPR"))

            menuActionSchemaTransportTask = menuTransportTask.addAction("Add Schema Transport Task")
            menuActionSchemaTransportTask.triggered.connect(lambda: self.onAddTransportTask.emit("VI.Transport.SchemaTransport, VI.Transport"))

            menuActionBufferTransportTask = menuTransportTask.addAction("Add System Configuration Transport Task")
            menuActionBufferTransportTask.triggered.connect(lambda: self.onAddTransportTask.emit("VI.Transport.BufferTransport, VI.Transport"))
            
            self.menu_items.append(menuTransportTask)
            self.menu_items.append(menuActionAddObjectTransportTask)
            self.menu_items.append(menuActionAddSQLTransportTask)
            self.menu_items.append(menuActionAddTagTransportTask)
            self.menu_items.append(menuActionAddFileTransportTask)
            self.menu_items.append(menuActionShellTransportTask)
            self.menu_items.append(menuActionSchemaTransportTask)
            self.menu_items.append(menuActionBufferTransportTask)



        

            