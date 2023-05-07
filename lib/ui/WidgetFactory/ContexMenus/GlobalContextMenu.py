from PyQt6.QtWidgets import (QMenu)
from PyQt6.QtCore import pyqtSignal

from lib.xml.transport_template_custom_object import transport_template_custom_object
from lib.xml.transport_task import sql_script_transport_task
from lib.ui.WidgetFactory import TE_ObjectContainer_TreeWidgetItem, TE_Table_TreeWidgetItem, TE_RelationColumn_TreeWidgetItem, TE_SQLScriptContainer_TreeWidgetItem, TE_SQLTransportTask_TreeWidgetItem, PackageManagerXMLFolder

class relation_widget_context_menu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    follow_table_relations = pyqtSignal(object)

    def __init__(self, parent, source_widget):
        super(relation_widget_context_menu, self).__init__(parent)
        self.parent = parent

        if source_widget:
            
            if isinstance(source_widget, TE_Table_TreeWidgetItem):
                action_follow_table_relations = self.addAction(f"Add Table Relations: {source_widget.follow_table}")
                action_follow_table_relations.triggered.connect(lambda: self.follow_table_relations.emit(source_widget) )
            if isinstance(source_widget, TE_RelationColumn_TreeWidgetItem):
                action_follow_table_relations = self.addAction(f"Add Table Relations: {source_widget.follow_table}")
                action_follow_table_relations.triggered.connect(lambda: self.follow_table_relations.emit(source_widget) )

class xml_structure_context_menu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    list_related_objects = pyqtSignal(object)
    load_object_from_database = pyqtSignal(object)
    save_relation_preset = pyqtSignal(object)
    add_transport_task = pyqtSignal(str)
    edit_sql_script = pyqtSignal(object)
    add_sql_script = pyqtSignal(object, str)

    def __init__(self, parent, source_widget):
        super(xml_structure_context_menu, self).__init__(parent)
        self.parent = parent
        self.menu_items = []

        if isinstance(source_widget, TE_ObjectContainer_TreeWidgetItem):

            action_list_related_objects = self.addAction("List Related Objects")
            action_list_related_objects.triggered.connect(lambda: self.list_related_objects.emit(source_widget) )
            
            self.addSeparator()

            if isinstance(source_widget.xml_object, transport_template_custom_object) and source_widget.object_data is None:
                action_load_from_database = self.addAction("Load Object From Database")
                action_load_from_database.triggered.connect(lambda: self.load_object_from_database.emit(source_widget) )
                self.menu_items.append(action_load_from_database)

            if source_widget.object_data is not None:
                action_save_preset = self.addAction("Save Relations as Preset")
                action_save_preset.triggered.connect(lambda: self.save_relation_preset.emit(source_widget) )
                self.menu_items.append(action_save_preset)

        if isinstance(source_widget, TE_SQLScriptContainer_TreeWidgetItem):
            action_edit_script = self.addAction("Edit SQL Script")
            action_edit_script.triggered.connect(lambda: self.edit_sql_script.emit(source_widget))
            self.menu_items.append(action_edit_script)

        if isinstance(source_widget, TE_SQLTransportTask_TreeWidgetItem):
            if isinstance(source_widget.xml_object, sql_script_transport_task):
                if source_widget.xml_object.common_sql is None:
                    action_add_common_sql_script = self.addAction("Add System SQL Script (CommonSQL)")
                    action_add_common_sql_script.triggered.connect(lambda: self.add_sql_script.emit(source_widget, "CommonSQL"))
                    self.menu_items.append(action_add_common_sql_script)
                
                if source_widget.xml_object.payload_sql is None:
                    action_add_payload_sql_script = self.addAction("Add User Data SQL Script (PayloadSQL)")
                    action_add_payload_sql_script.triggered.connect(lambda: self.add_sql_script.emit(source_widget, "PayloadSQL"))
                    self.menu_items.append(action_add_payload_sql_script)

        if source_widget is None:
            transport_menu = self.addMenu("Add Transport Task")
            self.menu_items.append(transport_menu)

            action_add_object_task = transport_menu.addAction("Add Object Transport Task")
            action_add_object_task.triggered.connect(lambda: self.add_transport_task.emit("VI.Transport.ObjectTransport, VI.Transport"))

            action_add_sql_task = transport_menu.addAction("Add SQL Transport Task")
            action_add_sql_task.triggered.connect(lambda: self.add_transport_task.emit("VI.Transport.SQLTransport, VI.Transport"))


class package_definition_context_menu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    add_package_definition = pyqtSignal(object)
    add_task_definition = pyqtSignal(object)
    edit_task_definition = pyqtSignal(object)


    def __init__(self, parent, source_item):
        super(package_definition_context_menu, self).__init__(parent)
        self.parent = parent

        self.menu_items = []


        action_add_package_definition = self.addAction("Add Package Definition")
        action_add_package_definition.triggered.connect(lambda: self.add_package_definition.emit(source_item) )

        if source_item:
            print(source_item.task_class)
        if source_item.task_class == "PackageDefinition":
            action_add_task_definition = self.addAction("Add Task Definition")
            action_add_task_definition.triggered.connect(lambda: self.add_task_definition.emit(source_item) )
            self.menu_items.append(action_add_task_definition)

        if source_item.task_class == "TaskItem":
            action_edit_task_definition = self.addAction("Edit Task Definition")
            action_edit_task_definition.triggered.connect(lambda: self.edit_task_definition.emit(source_item) )
            self.menu_items.append(action_edit_task_definition)

        self.menu_items.append(action_add_package_definition)
            
            
class ExecutionPlannerContextMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    add_execution_group = pyqtSignal(object)
    edit_execution_group = pyqtSignal(object)


    def __init__(self, parent, source_item):
        super(ExecutionPlannerContextMenu, self).__init__(parent)
        self.parent = parent
        self.menu_items = []
        clickedItem = source_item.internalPointer()

        action_add_execution_group = self.addAction("Add Task Execution Group")
        action_add_execution_group.triggered.connect(lambda: self.add_execution_group.emit(source_item) )

        if clickedItem:
            if clickedItem.task_class != "TaskItem":
                # print(clickedItem.task_class)
                self.menu_items.append(action_add_execution_group)

            if clickedItem.task_class == "TaskGroup":
                action_edit_execution_group = self.addAction("Edit Task Execution Group")
                action_edit_execution_group.triggered.connect(lambda: self.edit_execution_group.emit(source_item) )
                self.menu_items.append(action_edit_execution_group)
        else:
            self.menu_items.append(action_add_execution_group)

        

            