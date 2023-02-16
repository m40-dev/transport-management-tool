from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMenu, QListWidgetItem, QTreeWidgetItem
)

""" qt traceback handling"""
import traceback

from lib.ui.Theme import Application_Theme

from PyQt6.QtCore import pyqtSignal

""" UI import """
from lib.ui.MainWindow_ui import Ui_MainWindow
from lib.ui.SessionDetailsDialog import SessionDetailsDialog

""" database connector imports"""
from lib.db.database import DatabaseConnection

""" XML library """
from lib.xml.transport_template import transport_template

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
        self.ui.actionConnect_to_database.triggered.connect(self.get_session_details)
        self.ui.TableFilterButton.clicked.connect(self.filter_tables)
        self.ui.TableComboBox.currentTextChanged.connect(self.load_selected_table)
        self.ui.AddWithRelationsButton.clicked.connect(self.add_object_with_relations)

        """ Show main window """
        self.settings = QSettings("EmergencyCode", "Transport_Manager")
        if self.settings.value("geometry") is not None:
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("windowState") is not None:
            self.restoreState(self.settings.value("windowState"))

        """ UI style scheme """
        self.color_theme = Application_Theme()
        self.setStyleSheet(self.color_theme.style_sheet)

        """ UI Configurations """
        self.ui.main_splitter.setSizes([round(self.width()*0.2), round(self.width()*0.8)])
        self.ui.preview_splitter.setSizes([round(self.width()*0.3), round(self.width()*0.7)])

        """ Sessions Menu Configurations """

        self.ui.SessionsMenu = QMenu("Sessions")
        self.ui.menuMenu.addMenu(self.ui.SessionsMenu)
        NewActionItem = self.ui.SessionsMenu.addAction("Add Session details")
        NewActionItem.triggered.connect(self.get_session_details)
        self.ui.SessionsMenu.addSeparator()

        self.show()

        """ Program variables """
        self.db_connection = None
        self.sessions = {}

        oi_test = {'session_name': 'oi-test', 'server_address': '172.23.251.214', 'database_name': 'OneIM', 'user_name': 'sa', 'user_password': 'P@ssw0rd12'}
        self.sessions["oi-test"] = oi_test
        
        self.load_saved_sessions()

        self.transport_template = transport_template(self)

        self.load_xml_preview()

    def load_xml_preview(self):
        string_data = self.transport_template.to_string()
        self.ui.StructurePreviewTextBrowser.setText(string_data)

    def add_object_with_relations(self):
        selected = self.ui.TableItemsListWidget.currentItem()
        if selected is not None:
            container_item = QTreeWidgetItem(self.ui.StructurePreviewTreeWidget)
            container_item.setText(0, "Import Task")
            
            child_item = QTreeWidgetItem(container_item)
            child_item.setText(0, selected.text())
            container_item.addChild(child_item)

            self.ui.StructurePreviewTreeWidget.addTopLevelItem(container_item)

            task = self.transport_template.add_transport_task("ObjectTransport")
            task_container = task.add_container(child_item)

        self.load_xml_preview()


    def load_saved_sessions(self):
        for session_name in self.sessions.keys():
            self.add_session_to_menu(session_name)

    def add_session_to_menu(self, session_name):
        NewActionItem = self.ui.SessionsMenu.addAction(session_name)
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
        self.load_table_selector()

    def load_table_selector(self):
        query = "select TableName from DialogTable order by TableName"
        query_result = self.db_connection.run_db_query(query)

        for row in query_result:
            self.ui.TableComboBox.addItem(row.TableName)

    def load_selected_table(self):

        table_name = self.ui.TableComboBox.currentText()

        self.ui.TableItemsListWidget.clear()

        query = f"select * from {table_name}"
        query_result = self.db_connection.run_db_query(query)

        for row in query_result:
            w = QListWidgetItem(self.ui.TableItemsListWidget)
            w.setText(row.XObjectKey)
            self.ui.TableItemsListWidget.addItem(w)

        self.load_table_relations(table_name)

    def filter_tables(self):
        filter = self.ui.TableFilter.text()
        index = self.ui.TableComboBox.findText(filter, Qt.MatchFlag.MatchContains)

        print(len(self.ui.TableComboBox), " find table: ", filter, index)

    def load_table_relations(self, parent_table):
        self.ui.RelationsViewListWidget.clear()
        relations = self.get_table_relations([parent_table])
        
        for relation in relations:
            CR = f"{relation.ChildTable}|{relation.ParentColumn}|CR"
            FK = f"{relation.ChildTable}|{relation.ChildColumn}|FK"
            
            if not self.ui.RelationsViewListWidget.findItems(CR, Qt.MatchFlag.MatchCaseSensitive):
                self.ui.RelationsViewListWidget.addItem(CR)

            if not self.ui.RelationsViewListWidget.findItems(FK, Qt.MatchFlag.MatchCaseSensitive):
                self.ui.RelationsViewListWidget.addItem(FK)
            

    def get_table_relations(self, include_tables, depth=0):

        table_query = "', '".join(include_tables)

        query = f"select \
                BASE.ParentTable, BASE.ChildTable, Base.ParentColumn, Base.ChildColumn \
                from QBM_VQBMRelationALL BASE \
                where \
                BASE.IsConnectedInTransport > 0 \
                and \
                ( \
                BASE.ChildTable in ('{table_query}') \
                or \
                BASE.ParentTable in ('{table_query}') \
                ) \
                order by BASE.ParentTable"

        new_child_tables = []

        query_result = self.db_connection.run_db_query(query)

        for row in query_result:
            if row.ChildTable not in include_tables:
                new_child_tables.append(row.ChildTable)

        if len(new_child_tables) > 0 and depth <= 3:
            depth += 1
            for table_name in include_tables:
                if table_name not in new_child_tables:
                    new_child_tables.append(table_name)

            return self.get_table_relations(new_child_tables, depth)

        return query_result


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