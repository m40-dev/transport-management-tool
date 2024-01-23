#""" Required QT Libraries """
from PyQt6.QtCore import QSettings, QEvent
from PyQt6.QtWidgets import (
    QApplication, QFileDialog
    )
from PyQt6.QtGui import QShortcut, QKeySequence

#""" qt traceback handling"""
import traceback
import json

from PyQt6.QtCore import pyqtSignal

#""" Main UI import """
from lib.ui.MainWindow_ui import Ui_MainWindow

#""" Custom Widgets """
import lib.ui.WidgetFactory as WidgetFactory
from lib.ProgramConfiguration import ProgramConfiguration, ConnectionHandler

from lib.ui.CustomWindow.custom_window import CustomMainWindow

#""" Database Connector Module """
from lib.db.database import DatabaseConnection

VERSION = '0.9.2'
APP_NAME = f"Transport Management Tool - {VERSION}"

class Transport_Manager(CustomMainWindow):
    """Main window class for connection launcher"""
    statusBarUpdated = pyqtSignal(str)
    connectionDataChanged = pyqtSignal()
    currentViewChanged = pyqtSignal(int)
    styleSheetChanged = pyqtSignal()
    loginReady = pyqtSignal()
    
    def __init__(
        self, parent=None, 
        clipboard=None, 
        qapplication=None
    ):
        super().__init__(self)
        """ Map QT UI from parsed file - created and updated in qt designer """
        
        self.application_name = APP_NAME
        self.qt_app = qapplication
        self.clipboard = clipboard
        self.current_workdir = None

        self.settings = QSettings("EmergencyCode", "Transport_Manager")

        # QMessageBox.information(None, "debug", "application settings object created")

        self.ProgramConfiguration = ProgramConfiguration(self)
        self.color_theme = self.ProgramConfiguration.ColorPalette
        self.statusBarUpdated.connect(self.onStatusBarMessageReceived)
        self._relation_presets = {}

        self.ui = Ui_MainWindow(self)

        self.setWindowTitle(self.application_name)
        self.qt_app.setApplicationName(self.application_name)
        window_icon = self.ProgramConfiguration.getIcon("ApplicationLogo")
        self.setWindowIcon(window_icon)

        # Database and Connection handlers
        self.db = DatabaseConnection(self)
        self.ConnectionHandler = ConnectionHandler(self) 
        self.ConnectionHandler.databaseConnectionEstablished.connect(self.onDatabaseConnection)

        # Sidebar magic
        self.SideBar = WidgetFactory.SideBar(application=self)
        self.ui.SideBar_Layout.addWidget(self.SideBar)
        self.SideBar.buttonClicked.connect(lambda index: self.ui.MainTabWidget.setCurrentIndex(index))
        self.ui.MainTabWidget.currentChanged.connect(self.currentViewChanged)

        # Bring in the Main Tab Widgets
        self.PackageManager = WidgetFactory.PackageManager(self)
        self.XMLTemplateEditor = WidgetFactory.XMLTemplateEditor(self)

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
        self.styleSheetChanged.connect(self.onStyleSheetChange)

        """ Shortcuts """
        QShortcut(QKeySequence.StandardKey.Delete, self, self.deleteKeyPressEvent)
        # QShortcut(QKeySequence.StandardKey.InsertParagraphSeparator, self, self.onEnterKeyPress)
        QShortcut(QKeySequence.StandardKey.Refresh, self, self.refresh_ui)
        QShortcut(QKeySequence("Ctrl+0"), self, self.XMLTemplateEditor.expandXMLPreview)
        QShortcut(QKeySequence("Ctrl+9"), self, self.XMLTemplateEditor.foldXMLPreview)

        self.refresh_ui()
        
        """ Initial transport template object """
        # self.XMLTemplateEditor.newTransportTemplate()
        self.PackageManager.addExecutionPlan()

        # Application development testing helpers
        # self.ui.MainTabWidget.setCurrentIndex(2)
        self.show()
        self.setupApplication()

    def setupApplication(self):
        # load default workdir
        startup_workdir = self.ProgramConfiguration.getConfigurationValue("Package Manager", "InitialWorkdir")
        # print("startup workdir is set:", startup_workdir)
        if startup_workdir:
            self.PackageManager.loadWorkingDirectory(startup_workdir)

    def getConfigurationParameters(self, configuration_section):
        return self.ProgramConfiguration.getConfigurationParameters(configuration_section)

    def getConfigurationKey(self, configuration_section, configuration_key):
        return self.ProgramConfiguration.getConfigurationKey(configuration_section, configuration_key)

    def getConfigurationValue(self, configuration_section, configuration_key):
        return self.ProgramConfiguration.getConfigurationValue(configuration_section, configuration_key)

    def onStatusBarMessageReceived(self, message):
        self.ui.statusbar.showMessage(message)

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
        self.XMLTemplateEditor.reloadView()
        connection_name = self.db.connection_parameters.get("ConnectionName")
        if len(connection_name) > 45:
            connection_name = connection_name[:45] + "..."
        self.ui.WindowDecoration.setSubTitle(f"<b>Connected Session:</b> {connection_name}")

    def addExecutionPlan(self):
        self.PackageManager.addExecutionPlan()
        self.ui.MainTabWidget.setCurrentWidget(self.PackageManager)

    def manageRelationPresets(self):
        # print("manage relation presets")
        dialog = WidgetFactory.RelationPresetManager(self, self.relation_presets)
        if dialog:
            # print("closed")
            pass
    
    def updateRelationPresets(self):
        #iterate through the presets data and update 
        preset_data = self.relation_presets
        updated_presets = {}
        for table_name, relation_presets in preset_data.items():
            for relation_preset, relation_preset_data in relation_presets.items():
                preset_name = relation_preset
                if "name" in relation_preset_data.keys():
                    preset_name = relation_preset_data["name"]
                
                preset_dict = {preset_name: relation_preset_data}
                if table_name not in updated_presets.keys():
                    updated_presets[table_name] = preset_dict
                    continue
                #overwrite any existing preset with same name
                updated_presets[table_name][preset_name] = relation_preset_data

        self.relation_presets = updated_presets

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

    def onStyleSheetChange(self):
        self.setStyleSheet(self.ProgramConfiguration.styleSheet())
        self.XMLTemplateEditor.refresh_ui()
        self.PackageManager.refresh_ui()
        self.SettingsWidget.refresh_ui()
        self.ui.WindowDecoration.refresh_ui()

    def refresh_ui(self):
        """ UI style scheme """
        self.ProgramConfiguration.reloadStyleSheet()

        self.SideBar.animate()

        """ Restore window settings """
        if self.settings.value("MainWindowGeometry") is not None:
            self.restoreGeometry(self.settings.value("MainWindowGeometry"))
        if self.settings.value("MainWindowState") is not None:
            self.restoreState(self.settings.value("MainWindowState"))
        
        """ Reload Working Directory """
        self.ProgramConfiguration.reloadUserConfiguration()

        self.XMLTemplateEditor.refresh_ui()
        self.PackageManager.refresh_ui()

        self.PackageManager.loadWorkingDirectory()
        self.SettingsWidget.configurationReloaded.emit()

        self.ui.WindowDecoration.refresh_ui()
        
    
    def getObjectData(self, object_class, dialog_name="Object Data", source_index=None, editor_configuration=None):
        if editor_configuration is None:
            editor_configuration = self.getConfigurationParameters(object_class)

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

    def load_file(self, file_path):
        file_content = ""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return file_content

    def databaseConnectionRequired(self):
        # QMessageBox.information(self, "Database Connection Required", "This function requires active Database Connection to work.\nPlease connect to the target database and try again.")
        WidgetFactory.MsgBox(
            application=self,
            window_mode=WidgetFactory.MsgBox.INFO,
            window_title="Connection Required",
            message="This function requires active Database Connection to work.\nPlease connect to the target database and try again."
        ).exec()

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
        WidgetFactory.DialogScreens.MsgBox(self, exc_type.__name__, log_msg)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # splash = QSplashScreen()
    # splash.setFixedSize(500, 500)
    # splash.show()

    a = Transport_Manager(
        clipboard=app.clipboard(),
        qapplication=app
    )

    sys.excepthook = a.qtExceptionHandler
    app.exec()