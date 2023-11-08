#""" Required QT Libraries """
from PyQt6.QtCore import Qt, QSettings, QEvent
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMenu, QWidget, QMessageBox, QFileDialog
    )
from PyQt6.QtGui import QShortcut, QKeySequence, QIcon

#""" qt traceback handling"""
import traceback
import json

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
from lib.ProgramConfiguration import ProgramConfiguration, ObjectConfiguration, ConnectionHandler

#""" Database Connector Module """
from lib.db.database import DatabaseConnection

VERSION = '0.7.3'

class Transport_Manager(QMainWindow):
    """Main window class for connection launcher"""

    connectionDataChanged = pyqtSignal()
    currentViewChanged = pyqtSignal(int)
    
    def __init__(
        self, parent=None, clipboard=None, event_filter=None, qapplication=None
    ):
        QMainWindow.__init__(self, parent)
        """ Map QT UI from parsed file - created and updated in qt designer """

        self.ui = Ui_MainWindow()
        
        self.qt_app = qapplication
        self.clipboard = clipboard
        self.current_workdir = None

        self.setWindowTitle(f"Transport Manager Tool - {VERSION}")
        window_icon = QIcon("./icon.ico")
        self.setWindowIcon(window_icon)

        self.color_theme = Application_Theme()
        self.qt_app.setPalette(self.color_theme)
        self.setStyleSheet(self.color_theme.style_sheet)

        self.program_configuration = ProgramConfiguration(self)
        self.object_configuration = ObjectConfiguration(self)
        self.settings = QSettings("EmergencyCode", "Transport_Manager")
        self._relation_presets = {}

        self.ui.setupUi(self)

        # Database and Connection handlers
        self.db = DatabaseConnection()
        self.ConnectionHandler = ConnectionHandler(self) 
        self.ConnectionHandler.databaseConnectionEstablished.connect(self.onDatabaseConnection)

        # Sidebar magic
        self.SideBar = SideBar(application=self)
        self.ui.SideBar_Layout.addWidget(self.SideBar)
        self.SideBar.buttonClicked.connect(lambda index: self.ui.MainTabWidget.setCurrentIndex(index))
        self.ui.MainTabWidget.currentChanged.connect(self.currentViewChanged)

        # Bring in the Main Tab Widgets
        self.PackageManager = PackageManager(self)
        self.XMLTemplateEditor = XMLTemplateEditor(self)

        self.ui.MainTabWidget.addTab(self.PackageManager, "Package Manager")
        self.ui.MainTabWidget.addTab(self.XMLTemplateEditor, "XML Template Editor")
        self.SettingsWidget = WidgetFactory.SettingsWidget(self)
        self.ui.MainTabWidget.addTab(self.SettingsWidget, "Settings")

        self.ui.MainTabWidget.tabBar().setVisible(False)

        """ Connect signals """
        self.closeEvent = self.closeApplicationEvent
        self.installEventFilter(self)

        self.ui.actionAdd_DatabaseConnection.triggered.connect(
            self.ConnectionHandler.getConnectionDetails)
        
        self.ui.actionSaveFile.triggered.connect(
            self.XMLTemplateEditor.saveXMLTemplate)
        
        self.ui.actionSave_As.triggered.connect(
            self.XMLTemplateEditor.saveXMLTemplateAs)
        
        self.ui.actionOpen_File.triggered.connect(
            lambda: self.XMLTemplateEditor.openXMLTemplate())

        self.ui.actionChange_WorkingDirectory.triggered.connect(
            self.PackageManager.changeWorkingDirectory)
        
        self.ui.actionNew_Transport_Template.triggered.connect(
            self.XMLTemplateEditor.newTransportTemplate)
        
        self.ui.actionSettings.triggered.connect(lambda: self.ui.MainTabWidget.setCurrentWidget(self.SettingsWidget))

        #TODO: Definitely rework required
        planner_menu = self.ui.menubar.addMenu("Execution Planner")
        new_plan_action = planner_menu.addAction("Add New Plan")
        config_action = planner_menu.addAction("Configure")
        # Connect Menu Signals
        config_action.triggered.connect(self.configure_execution_planner)
        new_plan_action.triggered.connect(self.PackageManager.addExecutionPlan)
        new_plan_action.triggered.connect(lambda: self.ui.MainTabWidget.setCurrentWidget(self.PackageManager))

        menu_Presets = self.ui.menubar.addMenu("Relation Presets")
        action_managePresets = menu_Presets.addAction("Manage Presets")
        action_ExportPresetData = menu_Presets.addAction("Export Preset Data")
        action_ImportPresetData = menu_Presets.addAction("Import Preset Data")
        #Connect Menu Signals
        action_managePresets.triggered.connect(self.manageRelationPresets)
        action_ExportPresetData.triggered.connect(self.exportRelationPresets)
        action_ImportPresetData.triggered.connect(self.importRelationPresets)

        """ Shortcuts """
        QShortcut(QKeySequence.StandardKey.Delete, self, self.deleteKeyPressEvent)
        # QShortcut(QKeySequence.StandardKey.InsertParagraphSeparator, self, self.onEnterKeyPress)
        QShortcut(QKeySequence.StandardKey.Refresh, self, self.refresh_ui)
        QShortcut(QKeySequence("Ctrl+0"), self, self.XMLTemplateEditor.expandXMLPreview)
        QShortcut(QKeySequence("Ctrl+9"), self, self.XMLTemplateEditor.foldXMLPreview)

        self.refresh_ui()
        
        """ Initial transport template object """
        self.XMLTemplateEditor.newTransportTemplate()
        self.PackageManager.addExecutionPlan()

    @property
    def relation_presets(self):
        if not self._relation_presets:
            settings = self.settings.value("RelationPresets")
            if settings:
                self._relation_presets = settings
        return self._relation_presets
    
    @relation_presets.setter
    def relation_presets(self, preset_data):
        self._relation_presets = preset_data
        if preset_data and len(preset_data) > 0:
            self.settings.setValue("RelationPresets", preset_data)

    def onDatabaseConnection(self):
        self.db.load_session_data()
        self.XMLTemplateEditor.refresh_ui()

    def manageRelationPresets(self):
        print("manage relation presets")
        dialog = WidgetFactory.RelationPresetEditor(self, self.relation_presets)
        if dialog:
            print("closed")
        pass

    def exportRelationPresets(self):
        if len(self.relation_presets) == 0:
            return False

        dialog = QFileDialog(self, "Save As")
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        

        file_path = dialog.getSaveFileName(
            filter="*.json")

        if file_path[0] != "":
            preset_data = json.dumps(self.relation_presets, indent=4)
            with open(file_path[0], 'w') as doc:
                doc.write(preset_data)

    def importRelationPresets(self):
        dialog = QFileDialog(self, "Import relation preset data")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        file_path = dialog.getOpenFileName(filter="*.json")
        file_path = file_path[0]
        if file_path:
            json_data = self.load_file(file_path=file_path)
            if len(json_data) == 0:
                return False

            preset_data = json.loads(json_data)
            for table_name, relation_preset in preset_data.items():
                if (table_name in self.relation_presets.keys() 
                    and relation_preset not in self.relation_presets.values()):
                        self.relation_presets[table_name].update(relation_preset)
                else:
                    self.relation_presets[table_name] = relation_preset
            self.XMLTemplateEditor.DatabaseRelations.loadRelationPresets()

    def relationPresetAdded(self, table_name, preset_name, preset_data):
        preset_dict = {preset_name: preset_data}
        relation_presets = self.relation_presets
        if table_name not in relation_presets.keys():
            relation_presets[table_name] = preset_dict

        if preset_name not in relation_presets[table_name].keys():
            relation_presets[table_name][preset_name] = preset_data
        else:
            """ overwrite existing? """
            relation_presets[table_name][preset_name] = preset_data

        # self.settings.setValue("RelationPresets", self.relation_presets)
        self.relation_presets = relation_presets
        self.XMLTemplateEditor.DatabaseRelations.loadRelationPresets()

    def autoLoadDatabaseObjects(self):
        state = self.XMLTemplateEditor.DatabaseRelations.AutoLoadCheckBox.isChecked()
        return state

    def autoListDatabaseObjects(self):
        state = self.XMLTemplateEditor.DatabaseRelations.AutoListObjectsFromDatabaseCheckBox.isChecked()
        return state

    def refresh_ui(self):
        """ UI style scheme """
        self.setStyleSheet(self.color_theme.style_sheet)

        """ Restore window settings """
        if self.settings.value("MainWindowGeometry") is not None:
            self.restoreGeometry(self.settings.value("MainWindowGeometry"))
        if self.settings.value("MainWindowState") is not None:
            self.restoreState(self.settings.value("MainWindowState"))
        
        """ Reload Working Directory """
        self.object_configuration.reload_configuration_file()
        self.program_configuration.reload_configuration_file()
        # self.ui.XMLEditorWidget.reconfigure_editor()
        self.XMLTemplateEditor.refresh_ui()
        self.PackageManager.loadWorkingDirectory()
    
    def getObjectData(self, object_class, dialog_name="Object Data", source_index=None, editor_configuration=None):
        if editor_configuration is None:
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
        
    def load_file(self, file_path):
        file_content = ""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return file_content

    def databaseConnectionRequired(self):
        QMessageBox.information(self, "Database Connection Required", "This function requires active Database Connection to work.\nPlease connect to the target database and try again.")

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
        self.settings.setValue("MainWindowGeometry", self.saveGeometry())
        self.settings.setValue("MainWindowState", self.saveState())

    """ Application close """
    def closeApplicationEvent(self, event, force=False):
        self.settings.setValue("MainWindowGeometry", self.saveGeometry())
        self.settings.setValue("MainWindowState", self.saveState())
        self.settings.setValue("RelationPresets", self.relation_presets)

        if len(self.ConnectionHandler.connections) > 0:
            self.ConnectionHandler.saveConnectionsData()

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