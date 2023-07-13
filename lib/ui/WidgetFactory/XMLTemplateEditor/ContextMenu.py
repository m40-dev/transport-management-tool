from PyQt6.QtWidgets import (QMenu)
from PyQt6.QtCore import pyqtSignal

from .xml.transport_template_custom_object import transport_template_custom_object
from .xml.transport_task import sql_script_transport_task
from .TreeWidgets import TE_ObjectContainer_TreeWidgetItem, TE_Table_TreeWidgetItem, TE_RelationColumn_TreeWidgetItem, TE_SQLScriptContainer_TreeWidgetItem, TE_SQLTransportTask_TreeWidgetItem

class RelationContextMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    follow_table_relations = pyqtSignal(object)

    def __init__(self, parent, source_widget_item):
        super(RelationContextMenu, self).__init__()
        self.parent = parent

        if source_widget_item:
            
            if isinstance(source_widget_item, TE_Table_TreeWidgetItem):
                action_follow_table_relations = self.addAction(f"Add Table Relations: {source_widget_item.follow_table}")
                action_follow_table_relations.triggered.connect(lambda: self.follow_table_relations.emit(source_widget_item) )
            if isinstance(source_widget_item, TE_RelationColumn_TreeWidgetItem):
                action_follow_table_relations = self.addAction(f"Add Table Relations: {source_widget_item.follow_table}")
                action_follow_table_relations.triggered.connect(lambda: self.follow_table_relations.emit(source_widget_item) )

class XMLObjectContextMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    list_related_objects = pyqtSignal(object)
    load_object_from_database = pyqtSignal(object)
    save_relation_preset = pyqtSignal(object)
    add_transport_task = pyqtSignal(str)
    edit_sql_script = pyqtSignal(object)
    add_sql_script = pyqtSignal(object, str)

    def __init__(self, parent, source_widget_item):
        super(XMLObjectContextMenu, self).__init__()
        self.parent = parent
        self.menu_items = []

        if isinstance(source_widget_item, TE_ObjectContainer_TreeWidgetItem):

            action_list_related_objects = self.addAction("List Related Objects")
            action_list_related_objects.triggered.connect(lambda: self.list_related_objects.emit(source_widget_item) )
            
            self.addSeparator()

            if isinstance(source_widget_item.xml_object, transport_template_custom_object) and source_widget_item.object_data is None:
                action_load_from_database = self.addAction("Load Object From Database")
                action_load_from_database.triggered.connect(lambda: self.load_object_from_database.emit(source_widget_item) )
                self.menu_items.append(action_load_from_database)

            if source_widget_item.object_data is not None:
                action_save_preset = self.addAction("Save Relations as Preset")
                action_save_preset.triggered.connect(lambda: self.save_relation_preset.emit(source_widget_item) )
                self.menu_items.append(action_save_preset)

        if isinstance(source_widget_item, TE_SQLScriptContainer_TreeWidgetItem):
            action_edit_script = self.addAction("Edit SQL Script")
            action_edit_script.triggered.connect(lambda: self.edit_sql_script.emit(source_widget_item))
            self.menu_items.append(action_edit_script)

        if isinstance(source_widget_item, TE_SQLTransportTask_TreeWidgetItem):
            if isinstance(source_widget_item.xml_object, sql_script_transport_task):
                if source_widget_item.xml_object.common_sql is None:
                    action_add_common_sql_script = self.addAction("Add System SQL Script (CommonSQL)")
                    action_add_common_sql_script.triggered.connect(lambda: self.add_sql_script.emit(source_widget_item, "CommonSQL"))
                    self.menu_items.append(action_add_common_sql_script)
                
                if source_widget_item.xml_object.payload_sql is None:
                    action_add_payload_sql_script = self.addAction("Add User Data SQL Script (PayloadSQL)")
                    action_add_payload_sql_script.triggered.connect(lambda: self.add_sql_script.emit(source_widget_item, "PayloadSQL"))
                    self.menu_items.append(action_add_payload_sql_script)

        if source_widget_item is None:
            transport_menu = self.addMenu("Add Transport Task")
            self.menu_items.append(transport_menu)

            action_add_object_task = transport_menu.addAction("Add Object Transport Task")
            action_add_object_task.triggered.connect(lambda: self.add_transport_task.emit("VI.Transport.ObjectTransport, VI.Transport"))

            action_add_sql_task = transport_menu.addAction("Add SQL Transport Task")
            action_add_sql_task.triggered.connect(lambda: self.add_transport_task.emit("VI.Transport.SQLTransport, VI.Transport"))


        

            