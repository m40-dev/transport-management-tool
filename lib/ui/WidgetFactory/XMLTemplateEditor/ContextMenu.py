from PyQt6.QtWidgets import (QMenu)
from PyQt6.QtCore import pyqtSignal
from lib.data.DataModels.XMTemplateEditor.xml_object_definitions.transport_template_custom_object import transport_template_custom_object
class RelationContextMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    onFollowTableRelation = pyqtSignal(object)

    def __init__(self, parent, source_index):
        super(RelationContextMenu, self).__init__()
        self.parent = parent

        if source_index and source_index.isValid():
            source_item = source_index.internalPointer()
            if source_item.follow_table:
                menuActionFollowRelation = self.addAction(f"Add Table Relations: {source_item.follow_table}")
                menuActionFollowRelation.triggered.connect(lambda: self.onFollowTableRelation.emit(source_index))

class XMLObjectContextMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    onListRelatedObjectData = pyqtSignal(object)
    onLoadDatabaseObject = pyqtSignal(object)
    onSaveRelationPreset = pyqtSignal(object)
    onAddTransportTask = pyqtSignal(str)
    onEditSQLScript = pyqtSignal(object)
    onAddSQLScript = pyqtSignal(object, str)

    def __init__(self, parent, source_index):
        super(XMLObjectContextMenu, self).__init__()
        self.parent = parent
        self.menu_items = []

        #clicked on a specific object
        if source_index and source_index.isValid():
            source_item = source_index.internalPointer()
            print("object clicked", source_item.xml_object_class)
            
            # Prepare Transport Object specific menu items
            if source_item.xml_object_class == "Transport_Object":
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
            
            # Prepare SQL Script object context Menu
            if source_item.xml_object_class == "Transport_SQL_Object":
                menuActionEditSQLScript = self.addAction("Edit SQL Script")
                menuActionEditSQLScript.triggered.connect(lambda: self.onEditSQLScript.emit(source_index))
                self.menu_items.append(menuActionEditSQLScript)

            # Prepare SQL Task context Menu
            if source_item.xml_object_class == "SQL_Transport_Task":
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
            menuTransportTask = self.addMenu("Add Transport Task")
            
            menuActionAddObjectTransportTask = menuTransportTask.addAction("Add Object Transport Task")
            menuActionAddObjectTransportTask.triggered.connect(lambda: self.onAddTransportTask.emit("VI.Transport.ObjectTransport, VI.Transport"))

            menuActionAddSQLTransportTask = menuTransportTask.addAction("Add SQL Transport Task")
            menuActionAddSQLTransportTask.triggered.connect(lambda: self.onAddTransportTask.emit("VI.Transport.SQLTransport, VI.Transport"))

            self.menu_items.append(menuTransportTask)
            self.menu_items.append(menuActionAddObjectTransportTask)
            self.menu_items.append(menuActionAddSQLTransportTask)


        

            