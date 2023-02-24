from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMenu
)
from PyQt6.QtGui import QShortcut, QKeySequence, QIcon, QAction


""" qt traceback handling"""
import traceback

from lib.ui.Theme import Application_Theme

from PyQt6.QtCore import pyqtSignal

""" UI import """
from lib.ui.MainWindow_ui import Ui_MainWindow
from lib.ui.SessionDetailsDialog import SessionDetailsDialog

""" Custom Widgets """
from lib.ui.CustomWidgets.TemplateEditorTreeWidget import TemplateEditorTreeWidgetItem, TE_Table_TreeWidgetItem, TE_RelationColumn_TreeWidgetItem
from lib.ui.CustomWidgets.TemplateEditorListWidget import TemplateEditorListWidgetItem
from lib.ui.CustomWidgets.ContextMenu import relation_widget_context_menu, xml_structure_context_menu
""" database connector imports"""
from lib.db.database import DatabaseConnection

""" XML library """
from lib.xml.transport_template import transport_template

import re

VERSION = '0.1'

class Transport_Manager(QMainWindow):
    """Main window class for session launcher"""

    refresh_widget = pyqtSignal(object)
    
    def __init__(
        self, parent=None, clipboard=None, event_filter=None, qapplication=None
    ):
        QMainWindow.__init__(self, parent)
        """ Map QT UI from parsed file - created and updated in qt designer """

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"Transport Manager Tool - {VERSION}")

        """ Connect UI signals """
        self.closeEvent = self.close_application
        self.ui.actionAdd_DatabaseConnection.triggered.connect(self.get_session_details)
        self.ui.FindObjectButton.clicked.connect(self.find_objects)
        self.ui.TableComboBox.currentTextChanged.connect(self.load_db_objects)
        self.ui.AddSelectedObjectsWithRelationsButton.clicked.connect(self.add_selected_object_with_relation)
        self.ui.SearchResultsListWidget.currentItemChanged.connect(self.select_source_object)
        self.ui.XMLStructureTreeWidget.currentItemChanged.connect(self.select_source_object)

        """ UI style scheme """
        self.color_theme = Application_Theme()
        self.setStyleSheet(self.color_theme.style_sheet)

        """ UI Configurations """
        self.ui.PackageManagerSplitter_Left.setSizes([round(self.width()*0.2), round(self.width()*0.2)])
        self.ui.PackageManagerSplitter_Right.setSizes([round(self.width()*0.5), round(self.width()*0.5)])

        self.ui.TemplateEditorSplitter_Search.setSizes([round(self.height()*0.1), round(self.height()*0.3)])
        self.ui.TemplateEditorSplitter_Relations.setSizes([round(self.height()*0.2), round(self.height()*0.2)])

        self.ui.TemplateEditorSplitter_Left.setSizes([round(self.width()*0.2), round(self.width()*0.2)])
        self.ui.TemplateEditorSplitter_Right.setSizes([round(self.width()*0.4), round(self.width()*0.6)])

        """ Context Menu """
        self.ui.RelationsViewTreeWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.RelationsViewTreeWidget.customContextMenuRequested.connect(self.relation_context_menu)

        self.ui.XMLStructureTreeWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.XMLStructureTreeWidget.customContextMenuRequested.connect(self.xml_structure_context_menu)

        """ Shortcuts """
        QShortcut(QKeySequence.StandardKey.Delete, self, self.remove_selected_nodes)

        # self.ui.MainTabWidget.setCurrentIndex(1)
        """ Restore window settings """
        self.settings = QSettings("EmergencyCode", "Transport_Manager")
        if self.settings.value("geometry") is not None:
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("windowState") is not None:
            self.restoreState(self.settings.value("windowState"))

        self.show()

        """ Program variables """
        self.db_connection = None
        self.sessions = {}
        self.db_table_info = {}
        self.db_column_info = {}
        self.db_table_relations = {}

        # oi_test = {'session_name': 'oi-test', 'server_address': '172.21.49.199', 'database_name': 'OneIM', 'user_name': 'sa', 'user_password': 'P@ssw0rd12'}
        # self.sessions["oi-test"] = oi_test
        
        self.load_saved_sessions()
        self.transport_template = transport_template(self)
        self.load_xml_preview()

    def remove_selected_nodes(self):
        tree_widgets = [self.ui.XMLStructureTreeWidget, self.ui.RelationsViewTreeWidget]
        for tree_widget in tree_widgets:
            if tree_widget.hasFocus():
                for node_widget in tree_widget.selectedItems():
                    if node_widget.deleteObject():
                        parent_node = node_widget.parent()
                        if parent_node:
                            parent_node.removeChild(node_widget)
                        else:
                            root = tree_widget.invisibleRootItem()
                            root.removeChild(node_widget)
        self.load_xml_preview()

    def load_xml_preview(self):
        self.ui.XMLStructureTextBrowser.setText(self.transport_template.string)

    def load_saved_sessions(self):
        for session_name in self.sessions.keys():
            self.add_session_to_menu(session_name)

    def add_session_to_menu(self, session_name):
        NewActionItem = self.ui.menuConnections.addAction(session_name)
        NewActionItem.triggered.connect(lambda: self.connect_database(session_name))

    def connect_database(self, session_name):
        if session_name not in self.sessions.keys():
            return False
        
        self.ui.statusbar.showMessage(f"Using session info: {session_name}")

        session_params = self.sessions[session_name]

        if self.db_connection is not None:
            self.db_connection.disconnect_db()

        self.db_connection = DatabaseConnection(session_params)
        self.reload_ui_data()

    def clear_widgets(self):
        self.ui.TableComboBox.clear()
        self.ui.TableFilter.clear()

    def reload_ui_data(self):
        if self.db_connection is None:
            return False
        self.load_table_data()
        self.load_column_data()
        self.load_table_relations_data()

    def load_table_data(self):
        query = "select * from DialogTable order by TableName"
        query_result = self.db_connection.run_db_query(query)

        for row in query_result:
            self.ui.TableComboBox.addItem(row.TableName)
            self.db_table_info[row.TableName] = row

    def load_column_data(self):
        query = "select * from DialogColumn order by Caption"
        query_result = self.db_connection.run_db_query(query)

        for row in query_result:
            self.db_column_info[row.ColumnName] = row

    def load_table_relations_data(self):
        query = "select \
            BASE.Caption, \
            BASE.IsConnectedInTransport as 'Relation',\
            BASE.ParentTable as 'TableGroup',\
            BASE.ParentTable,\
            Base.ParentColumn, \
            BASE.ChildTable,  \
            Base.ChildColumn  \
            from QBM_VQBMRelationALL BASE \
            where isnull(BASE.IsConnectedInTransport, 0) > 0 \
            order by BASE.ParentTable"

        query_result = self.db_connection.run_db_query(query)
        self.save_relation_data(query_result)

        query = "select \
            BASE.Caption, \
            BASE.IsConnectedInTransport as 'Relation',\
            BASE.ChildTable as 'TableGroup',\
            BASE.ParentTable,\
            Base.ParentColumn, \
            BASE.ChildTable,  \
            Base.ChildColumn  \
            from QBM_VQBMRelationALL BASE \
            where isnull(BASE.IsConnectedInTransport, 0) > 0 \
            order by BASE.ParentTable"

        query_result = self.db_connection.run_db_query(query)
        self.save_relation_data(query_result)

    def save_relation_data(self, query_result):
        for row in query_result:
            relation = {
                "Caption": row.Caption,
                "TableGroup": row.TableGroup,
                "ParentTable": row.ParentTable, 
                "ParentColumn": row.ParentColumn, 
                "Relation": row.Relation,
                "ChildTable": row.ChildTable,
                "ChildColumn": row.ChildColumn
                }

            if row.TableGroup not in self.db_table_relations.keys():
                self.db_table_relations[row.TableGroup] = [relation]
                continue

            if relation not in self.db_table_relations[row.TableGroup]:
                self.db_table_relations[row.TableGroup].append(relation)

    def select_source_object(self, source_widget):
        if source_widget is not None:
            relations = source_widget.object_relations
            if relations is not None:
                self.load_table_relations(relations, source_widget)        
    
    def follow_table_relation(self, relation_widget):
        if relation_widget.follow_table:
            source_widget_relations = relation_widget.source_widget.object_relations
            new_relations = self.db_table_relations.get(relation_widget.follow_table, None)
            merged_relations = self.extend_table_relations(source_widget_relations, new_relations)
            relation_widget.source_widget.object_relations = merged_relations
            self.load_table_relations(merged_relations, relation_widget.source_widget)

    def extend_table_relations(self, current_relations, new_relations):
        current = current_relations
        new = new_relations
        for relation in new:
            if relation not in current:
                current.append(relation)
        return current

    def relation_context_menu(self, menuPosition):
        clickedItem = self.ui.RelationsViewTreeWidget.itemAt(menuPosition)
        if clickedItem:
            contextMenu = relation_widget_context_menu(self, clickedItem)
            contextMenu.follow_table_relations.connect(self.follow_table_relation)
            menu_target = self.ui.RelationsViewTreeWidget.mapToGlobal(menuPosition)
            contextMenu.popup(menu_target)
            
    def xml_structure_context_menu(self, menuPosition):
        clickedItem = self.ui.XMLStructureTreeWidget.itemAt(menuPosition)
        if clickedItem:
            contextMenu = xml_structure_context_menu(self, clickedItem)
            contextMenu.list_related_objects.connect(self.list_related_objects)
            menu_target = self.ui.XMLStructureTreeWidget.mapToGlobal(menuPosition)
            contextMenu.popup(menu_target)
        
    def list_related_objects(self, source_widget):
        if source_widget is not None:
            for i in reversed(range(source_widget.childCount())):
                source_widget.removeChild(source_widget.child(i))

            for table_name, results in source_widget.related_objects.items():
                table_widget = TE_Table_TreeWidgetItem(self, self.db_table_info.get(table_name, table_name))
                source_widget.addChild(table_widget)
                for selected_object in results:
                    selected_object_widget = TemplateEditorTreeWidgetItem(self, selected_object)
                    table_widget.addChild(selected_object_widget)
                # print(table_name, results)

    def load_db_objects(self, table_name=None, data_rows=[]):
        table_name = self.ui.TableComboBox.currentText()
        self.ui.SearchResultsListWidget.clear()

        if len(data_rows) == 0: 
            query = f"select * from {table_name}"
            data_rows = self.db_connection.run_db_query(query)

        for row in data_rows:
            w = TemplateEditorListWidgetItem(self, row)
            self.ui.SearchResultsListWidget.addItem(w)

    def get_objectkey_table(self, input_string):
        table_name = None
        regex = r"<T>(.*?)</T>"
        if input_string is not None:
            match = re.search(regex, input_string)
            if match:
                table_name = match.group(1)
        return table_name

    def find_objects(self):
        filter = self.ui.ObjectQueryTextEdit.toPlainText()
        filter_rows = filter.split(",")
        data_rows = []
        for object_query in filter_rows:
             object_query = object_query.strip()
             table_name = self.get_objectkey_table(object_query)
             if table_name is not None:
                query = f"select * from {table_name} where XObjectKey = '{object_query}'"
                data_rows += self.db_connection.run_db_query(query)

        self.load_db_objects(data_rows=data_rows)

    def load_table_relations(self, relations, source_widget):
        self.ui.RelationsViewTreeWidget.clear()
        tree_widgets = {}

        for relation in relations:
            parent_table_name = relation["ParentTable"]
            table_group_name = relation["TableGroup"]
            child_table_name = relation["ChildTable"]
            child_column_name = relation["ChildColumn"]

            if parent_table_name == table_group_name:
                parent_table_name = child_table_name

            if parent_table_name not in tree_widgets.keys():
                parent_widget = TE_Table_TreeWidgetItem(self, self.db_table_info.get(parent_table_name, parent_table_name), source_widget=source_widget)
                tree_widgets[parent_table_name] = parent_widget
            else:
                parent_widget = tree_widgets[parent_table_name]
            
            child_widget = TE_RelationColumn_TreeWidgetItem(self, relation, source_widget=source_widget)
            parent_widget.addChild(child_widget)
            parent_widget.setExpanded(True)
        
        for tree_widget in tree_widgets.values():
            self.ui.RelationsViewTreeWidget.addTopLevelItem(tree_widget)

        self.ui.RelationsViewTreeWidget.sortItems(1, Qt.SortOrder.AscendingOrder)
            
    def add_selected_object_with_relation(self):
        selected_source_widgets = self.ui.SearchResultsListWidget.selectedItems()
        if selected_source_widgets is not None:
            selected_target_widgets = self.ui.XMLStructureTreeWidget.selectedItems()
            task_item = None
            if len(selected_target_widgets) == 0:
                """ Create UI Node """
                object_data = {"Name": "Import Task", "Description": "Structural node that organizes all tasks of one group." }
                task_item = TemplateEditorTreeWidgetItem(self, object_data)
                self.ui.XMLStructureTreeWidget.addTopLevelItem(task_item)

                """ Create XML Node """
                task = self.transport_template.add_transport_task("ObjectTransport")
                task_item.xml_object = task
                
            else:
                """ Find Parent Node """
                for widget in selected_target_widgets:
                    while task_item is None:
                        if widget.parent() is None:
                            task_item = widget
                        widget = widget.parent()
                    break

            for source_widget in selected_source_widgets:
                """ Add all selected objects to selected Task Container """
                if isinstance(source_widget, TemplateEditorListWidgetItem):
                    object_container = TemplateEditorTreeWidgetItem(self, object_data=source_widget.object_data, source_widget=source_widget)
                    container_element = task_item.xml_object.add_container(object_container)
                    task_item.addChild(object_container)
                    object_container.xml_object = container_element
                    self.list_related_objects(object_container)
        self.load_xml_preview()


    def get_child_tables(self, table_name, depth=0):
        child_tables = []
        local_table_relations = self.db_table_relations.copy()

        table_relations = local_table_relations.get(table_name, None)
        if table_relations is not None:
            depth += 1
            child_tables = list(table_relations.values())
            
            if len(child_tables) > 0:
                child_tables = list(child_tables[0].keys())

            for child_table_name in child_tables:
                if depth < 3:
                    child_tables += self.get_child_tables(child_table_name, depth)
                    return list(set(child_tables))
        
        return child_tables

    def get_session_details(self):
        dialog = SessionDetailsDialog(self)
        if dialog.exec():
            if dialog.session_name not in self.sessions.keys():
                self.add_session_to_menu(dialog.session_name)

            self.sessions[dialog.session_name] = dialog.form_values

    def close_application(self, event, force=False):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        if event:
            event.accept()

        QApplication.quit()

    def qt_exception_hook(self, exc_type, exc_value, exc_traceback):
        """Checks if a QApplication instance is available and shows a messagebox with the exception message.
        If unavailable (non-console application), log an additional notice.
        """

        log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                '{0}: {1}'.format(exc_type.__name__, exc_value)])
        
        print (log_msg)



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    a = Transport_Manager(
        clipboard=app.clipboard(), event_filter=None, qapplication=app
    )

    sys.excepthook = a.qt_exception_hook
    app.exec()