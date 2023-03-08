from PyQt6.QtWidgets import (QMenu)
from PyQt6.QtCore import pyqtSignal

from lib.ui.CustomWidgets.TemplateEditorTreeWidgetItem import TemplateEditorTreeWidgetItem
from lib.ui.CustomWidgets.TE_Table_TreeWidgetItem import TE_Table_TreeWidgetItem
from lib.ui.CustomWidgets.TE_RelationColumn_TreeWidgetItem import TE_RelationColumn_TreeWidgetItem
from lib.ui.CustomWidgets.TE_ObjectContainer_TreeWidgetItem import TE_ObjectContainer_TreeWidgetItem
from lib.ui.CustomWidgets.TE_TransportTask_TreeWidgetItem import TE_TransportTask_TreeWidgetItem
from lib.ui.CustomWidgets.TE_ObjectContainerData_TreeWidgetItem import TE_ObjectContainerData_TreeWidgetItem
from lib.ui.CustomWidgets.TemplateEditorListWidget import TemplateEditorListWidgetItem
from lib.xml.transport_template_custom_object import transport_template_custom_object


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

    def __init__(self, parent, source_widget):
        super(xml_structure_context_menu, self).__init__(parent)
        self.parent = parent

        if isinstance(source_widget, TE_ObjectContainer_TreeWidgetItem):
            action_list_related_objects = self.addAction(f"List Related Objects")
            action_list_related_objects.triggered.connect(lambda: self.list_related_objects.emit(source_widget) )

            if isinstance(source_widget.xml_object, transport_template_custom_object) and source_widget.object_data is None:
                action_load_from_database = self.addAction(f"Load Object From Database")
                action_load_from_database.triggered.connect(source_widget.load_from_database)

