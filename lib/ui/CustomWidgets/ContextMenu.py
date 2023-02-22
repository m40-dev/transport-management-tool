from PyQt6.QtWidgets import (QMenu)
from PyQt6.QtCore import pyqtSignal
from lib.ui.CustomWidgets.TemplateEditorTreeWidget import TE_Table_TreeWidgetItem, TE_RelationColumn_TreeWidgetItem, TemplateEditorTreeWidgetItem


class relation_widget_context_menu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    follow_table_relations = pyqtSignal(object)

    def __init__(self, parent, source_widget):
        super(relation_widget_context_menu, self).__init__(parent)
        self.parent = parent

        if source_widget:
            if isinstance(source_widget, TE_Table_TreeWidgetItem):
                action_follow_table_relations = self.addAction(f"Follow Table Relations: {source_widget.object_data.TableName}")
                action_follow_table_relations.triggered.connect(lambda: self.follow_table_relations.emit(source_widget) )
            if isinstance(source_widget, TE_RelationColumn_TreeWidgetItem):
                action_follow_table_relations = self.addAction(f"Follow Table Relations: {source_widget.object_data['follow_table']}")
                action_follow_table_relations.triggered.connect(lambda: self.follow_table_relations.emit(source_widget) )

class xml_structure_context_menu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    list_related_objects = pyqtSignal(object)

    def __init__(self, parent, source_widget):
        super(xml_structure_context_menu, self).__init__(parent)
        self.parent = parent

        if isinstance(source_widget, TemplateEditorTreeWidgetItem):
            action_list_related_objects = self.addAction(f"List Related Objects")
            action_list_related_objects.triggered.connect(lambda: self.list_related_objects.emit(source_widget) )
