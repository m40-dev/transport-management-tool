#""" Required QT Libraries """
from PyQt6.QtCore import Qt, QSettings, QEvent
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMenu, QWidget, QMessageBox
    )
from PyQt6.QtGui import QShortcut, QKeySequence, QIcon

#""" qt traceback handling"""
import traceback

#""" built-in modules """
import hashlib
import json
from cryptography.fernet import Fernet
import base64

from lib.ui.Theme import Application_Theme

from PyQt6.QtCore import pyqtSignal

#""" Main UI import """
from lib.ui.MainWindow_ui import Ui_MainWindow

#""" Custom Widgets """
import lib.ui.WidgetFactory as WidgetFactory
import lib.ui.WidgetFactory.DialogScreens as DialogScreens
from lib.ui.WidgetFactory.PackageManager import PackageManager
from lib.ui.WidgetFactory.SideBar import SideBar
from lib.ui.WidgetFactory.XMLTemplateEditor import XMLTemplateEditor
from lib.ProgramConfiguration import ProgramConfiguration, ObjectConfiguration

#""" Database Connector Module """
from lib.db.database import DatabaseConnection

VERSION = '0.6.1'

class Transport_Manager(QMainWindow):
    """Main window class for connection launcher"""

    # refresh_widget = pyqtSignal(object)
    # xml_structure_changed = pyqtSignal()
    connectionDataChanged = pyqtSignal()
    currentViewChanged = pyqtSignal(int)
    
    def __init__(
        self, parent=None, clipboard=None, event_filter=None, qapplication=None
    ):
        QMainWindow.__init__(self, parent)
        """ Map QT UI from parsed file - created and updated in qt designer """

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.qt_app = qapplication
        self.current_workdir = None

        self.setWindowTitle(f"Transport Manager Tool - {VERSION}")
        window_icon = QIcon("./icon.ico")
        self.setWindowIcon(window_icon)

        self.color_theme = Application_Theme()
        self.qt_app.setPalette(self.color_theme)

        self.program_configuration = ProgramConfiguration(self)
        self.object_configuration = ObjectConfiguration(self)

        self.settings = QSettings("EmergencyCode", "Transport_Manager")

        # Database handler
        self.db = DatabaseConnection()

        # Sidebar magic -> to be moved to widget factory
        self.SideBar = SideBar(application=self, target_layout=self.ui.SideBar_Layout)
        self.SideBar.buttonClicked.connect(lambda index: self.ui.MainTabWidget.setCurrentIndex(index))
        self.ui.MainTabWidget.currentChanged.connect(self.currentViewChanged)

        # Bring in the Main Tab Widgets
        self.PackageManager = PackageManager(self)
        self.XMLTemplateEditor = XMLTemplateEditor(self)

        self.ui.MainTabWidget.addTab(self.PackageManager, "Package Manager")
        self.ui.MainTabWidget.addTab(self.XMLTemplateEditor, "XML Template Editor")
        self.ui.MainTabWidget.addTab(QWidget(), "Settings")

        self.ui.MainTabWidget.tabBar().setVisible(False)


        """ Connect UI signals """
        self.closeEvent = self.closeApplicationEvent
        self.installEventFilter(self)

        #TODO: Rework required
        self.ui.actionAdd_DatabaseConnection.triggered.connect(self.get_connection_details)
        self.ui.actionSaveFile.triggered.connect(self.XMLTemplateEditor.XMLTemplate.saveXMLTemplate)
        self.ui.actionSave_As.triggered.connect(self.XMLTemplateEditor.XMLTemplate.saveXMLTemplateAs)
        self.ui.actionOpen_File.triggered.connect(
            lambda: self.XMLTemplateEditor.openXMLTemplate())
        self.ui.actionChange_WorkingDirectory.triggered.connect(self.PackageManager.changeWorkingDirectory)
        self.ui.actionNew_Transport_Template.triggered.connect(self.XMLTemplateEditor.XMLTemplate.newTransportTemplate)

        planner_menu = self.ui.menubar.addMenu("Execution Planner")
        new_plan_action = planner_menu.addAction("Add New Plan")
        config_action = planner_menu.addAction("Configure")
        config_action.triggered.connect(self.configure_execution_planner)
        new_plan_action.triggered.connect(self.PackageManager.addExecutionPlan)

        """ Shortcuts """
        QShortcut(QKeySequence.StandardKey.Delete, self, self.deleteKeyPressEvent)
        QShortcut(QKeySequence.StandardKey.InsertParagraphSeparator, self, self.enter_shortcut)
        QShortcut(QKeySequence.StandardKey.Refresh, self, self.refresh_ui)
        # QShortcut(QKeySequence("Ctrl+0"), self, self.ui.XMLEditorWidget.expand_by_level)
        # QShortcut(QKeySequence("Ctrl+9"), self, self.ui.XMLEditorWidget.fold_by_level)

        self.refresh_ui()

        """ Program variables """
        self.db = None
        self.encryption_key = None
        self.last_widget_clicked = None

        """ Saved connection data """
        self.connections = self.settings.value("connections")
        if self.connections is None:
            self.connections = {}

        if len(self.connections) > 0:
            encryption_key = self.get_encryption_key()
            if encryption_key:
                self.encryption_key = encryption_key
                if self.decrypt_connection_details():
                    self.load_saved_connections()
                else:
                    print("connection data decryption failed")
                    self.connections = {}
            else:
                print("connection details were not loaded")
                self.connections = {}
        

        """ Initial transport template object """
        self.XMLTemplateEditor.XMLTemplate.newTransportTemplate()
        self.PackageManager.addExecutionPlan()

    def enter_shortcut(self):
        if self.ui.SearchPackageLineEdit.hasFocus():
            self.filter_packages(self.ui.SearchPackageLineEdit.text())

    def refresh_ui(self):
        """ UI style scheme """
        self.setStyleSheet(self.color_theme.style_sheet)

        """ Restore window settings """
        if self.settings.value("geometry") is not None:
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("windowState") is not None:
            self.restoreState(self.settings.value("windowState"))
        
        """ Reload Working Directory """
        self.object_configuration.reload_configuration_file()
        self.program_configuration.reload_configuration_file()
        # self.ui.XMLEditorWidget.reconfigure_editor()
        self.XMLTemplateEditor.refresh_ui()
        self.PackageManager.loadWorkingDirectory()
    
    def getObjectData(self, object_class, dialog_name="Object Data", source_index=None):
        editor_configuration = self.object_configuration.get(object_class)
        if editor_configuration:
            dialog = WidgetFactory.FormEditorDialog(
                application=self, 
                configuration_class=object_class, 
                dialog_name=dialog_name,
                form_configuration=editor_configuration
                )
            if source_index:
                dialog.set_form_data(source_index)
            if dialog.exec():
                data = dialog.form_data
                return data
        return None

    """ Execution Planner Configuration """
    def configure_execution_planner(self):
        configuration = self.settings.value("ExecutionPlannerSettings")
        new_configuration = WidgetFactory.DialogScreens.ExecutionPlannerConfigDialog(self)
        new_configuration.setupForm(configuration)
        if new_configuration.exec():
            new_config_data = new_configuration.to_dict
            self.settings.setValue("ExecutionPlannerSettings", new_config_data)
    
    """ Database connection Management """
    def connect_database(self, connection_name):
        if not isinstance(self.connections, dict):
            return False
        
        if connection_name not in self.connections.keys():
            return False
        
        self.ui.statusbar.showMessage(f"Using connection info: {connection_name}")

        connection_params = self.connections[connection_name]

        if self.db is not None:
            self.db.disconnect_db()
            self.db = None

        self.db = DatabaseConnection(connection_params)
        self.db.connect_db()
        
        if self.db is not None:
            self.db.load_session_data()
            self.XMLTemplateEditor.refresh_ui()
        
    def load_file(self, file_path):
        file_content = ""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return file_content

    """ connection Data Management """
    def get_encryption_key(self, initial=False):
        encryption_key = DialogScreens.EncryptionKeyDialog(self, initial)
        if encryption_key.exec():
            enc = hashlib.sha3_512(bytes(encryption_key.encryption_key, 'utf-8'))
            return enc.hexdigest()
        return False
        
    def decrypt_connection_details(self):
        encrypted_connection_details = self.connections
        if isinstance(encrypted_connection_details, dict):
            return True

        if self.encryption_key is None:
            self.encryption_key = self.get_encryption_key()

        byte_key = bytes(self.encryption_key, 'utf-8')[0:32]
        b64_byte_key = base64.urlsafe_b64encode(byte_key)

        crypto = Fernet(b64_byte_key)
        try:
            decrypted_connection_details = crypto.decrypt(encrypted_connection_details)
        except:
            return False

        connection_data = json.loads(decrypted_connection_details)
        if connection_data:
            self.connections = connection_data
            return True
        return False

    def save_connection_details(self):
        if len(self.connections) == 0:
            self.settings.setValue("connections", {})
            return True
        
        encoded_connection_data = json.dumps(self.connections).encode('utf-8')

        if self.encryption_key is None:
            self.encryption_key = self.get_encryption_key(initial=True)

        byte_key = bytes(self.encryption_key, 'utf-8')[0:32]
        b64_byte_key = base64.urlsafe_b64encode(byte_key)

        crypto = Fernet(b64_byte_key)
        encrypted_connection_details = crypto.encrypt(encoded_connection_data)

        self.settings.setValue("connections", encrypted_connection_details)
        self.connectionDataChanged.emit()

    def load_saved_connections(self):
        if self.connections is not None:
            if isinstance(self.connections, dict):
                for connection_name in self.connections.keys():
                    self.add_connection_to_menu(connection_name)

    def get_connection_details(self, connection_name=None):
        connection_data = self.connections.get(connection_name, None)

        editor_configuration = self.program_configuration.get("Connection_Configuration")
        if editor_configuration:
            dialog = WidgetFactory.FormEditorDialog(self, 
            configuration_class="Connection_Configuration",
            dialog_name="Connection Configuration",
            form_configuration=editor_configuration
            )
            dialog.set_dictionary_data(connection_data)
            if dialog.exec():
                data = dialog.form_data
                dialog_connection_name = data.get("ConnectionName", None)

                if dialog_connection_name and dialog_connection_name not in self.connections.keys() and not connection_name:
                    self.add_connection_to_menu(dialog_connection_name)

                if connection_name and dialog_connection_name != connection_name:
                    source_connection = self.ui.menuConnections.findChildren(QMenu, connection_name, Qt.FindChildOption.FindDirectChildrenOnly)
                    if len(source_connection) == 1:
                        source_connection = source_connection[0]
                        source_connection.setObjectName(dialog_connection_name)
                        source_connection.setTitle(dialog_connection_name)
                        self.connections.pop(connection_name)

                self.connections[dialog_connection_name] = data
                self.save_connection_details()

    def add_connection_to_menu(self, connection_name):
        NewMenuItem = self.ui.menuConnections.addMenu(connection_name)
        NewMenuItem.setObjectName(connection_name)
        ConnectAction = NewMenuItem.addAction("Connect")
        EditAction = NewMenuItem.addAction("Edit")
        NewMenuItem.addSeparator()
        DeleteAction = NewMenuItem.addAction("Delete")

        ConnectAction.triggered.connect(lambda: self.connect_database(NewMenuItem.objectName()))
        EditAction.triggered.connect(lambda: self.get_connection_details(NewMenuItem.objectName()))
        DeleteAction.triggered.connect(lambda: self.delete_connection(NewMenuItem))

    def delete_connection(self, connection_menu_object):
        connection_name = connection_menu_object.title()

        decision = QMessageBox.question(self, "Confirm connection Delete", f"Are you sure to delete connection info: {connection_name}?")
        if decision == QMessageBox.StandardButton.Yes:
            action = connection_menu_object.menuAction()
            self.ui.menuConnections.removeAction(action)
            
            self.connections.pop(connection_name)
            self.save_connection_details()

    def deleteKeyPressEvent(self):

        if self.ui.MainTabWidget.currentWidget() == self.PackageManager:
            self.PackageManager.deleteSelectedItems()

        if self.ui.MainTabWidget.currentWidget() == self.XMLTemplateEditor:
            self.XMLTemplateEditor.deleteSelectedItems()

    def eventFilter(self, source, event):
        if source == self:
            if event.type() == QEvent.Type.Move:
                self.saveMainWindowState()
        return super().eventFilter(source, event)

    def saveMainWindowState(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    """ Application close """
    def closeApplicationEvent(self, event, force=False):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("relation_presets", self.XMLTemplateEditor.DatabaseRelations.relation_presets)

        if len(self.connections) > 0:
            self.save_connection_details()

        if event:
            event.accept()

        QApplication.quit()

    def qtExceptionHandler(self, exc_type, exc_value, exc_traceback):
        """Checks if a QApplication instance is available and shows a messagebox with the exception message.
        If unavailable (non-console application), log an additional notice.
        """

        log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                '{0}: {1}'.format(exc_type.__name__, exc_value)])
        
        print (log_msg)
        DialogScreens.MsgBox(self, exc_type.__name__, log_msg)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # splash = QSplashScreen()
    # splash.show()
    
    a = Transport_Manager(
        clipboard=app.clipboard(), event_filter=None, qapplication=app
    )
    
    # splash.finish(a)
    a.show()

    sys.excepthook = a.qtExceptionHandler
    app.exec()