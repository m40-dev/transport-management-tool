from PyQt6.QtCore import Qt, QSettings, QPoint, QRegularExpression, QRegularExpressionMatch, QTimer, QRectF, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QMenu, QHeaderView, QTreeWidget, QAbstractItemView, QTreeWidgetItemIterator, QFileDialog, QMessageBox, QStyleOptionViewItem, QStyle, QStyledItemDelegate, QTreeWidgetItem, QLabel
)
from PyQt6.QtGui import QShortcut, QKeySequence, QIcon, QAction, QTextDocument, QAbstractTextDocumentLayout


""" qt traceback handling"""
import traceback
import copy
import re
import hashlib
import json
from cryptography.fernet import Fernet, InvalidToken
import base64
from pathlib import Path

from lib.ui.Theme import Application_Theme

from PyQt6.QtCore import pyqtSignal

""" UI import """
from lib.ui.MainWindow_ui import Ui_MainWindow
from lib.ui.SessionDetailsDialog import SessionDetailsDialog
from lib.ui.EncryptionKeyDialog import EncryptionKeyDialog
from lib.ui.RelationPresetDialog import RelationPresetDialog
from lib.ui.ScriptEditorDialog import ScriptEditorDialog
from lib.ui.MessageBox import MsgBox


""" Custom Widgets """
from lib.ui.CustomWidgets.TemplateEditorTreeWidgetItem import TemplateEditorTreeWidgetItem
from lib.ui.CustomWidgets.TE_Table_TreeWidgetItem import TE_Table_TreeWidgetItem
from lib.ui.CustomWidgets.TE_RelationColumn_TreeWidgetItem import TE_RelationColumn_TreeWidgetItem
from lib.ui.CustomWidgets.TE_ObjectContainer_TreeWidgetItem import TE_ObjectContainer_TreeWidgetItem
from lib.ui.CustomWidgets.TE_TransportTask_TreeWidgetItem import TE_TransportTask_TreeWidgetItem, TE_ObjectTransportTask_TreeWidgetItem, TE_SQLTransportTask_TreeWidgetItem
from lib.ui.CustomWidgets.TE_ObjectContainerData_TreeWidgetItem import TE_ObjectContainerData_TreeWidgetItem
from lib.ui.CustomWidgets.TE_SQLScriptContainer_TreeWidgetItem import TE_SQLScriptContainer_TreeWidgetItem
from lib.ui.CustomWidgets.TemplateEditorListWidget import TemplateEditorListWidgetItem
from lib.ui.CustomWidgets.PackageManagerTreeWidgetItem import PackageManagerTreeWidgetItem
from lib.ui.CustomWidgets.PackageManagerTreeWidgetItem import PackageManagerXMLFile, PackageManagerXMLFolder
from lib.ui.ContextMenu import relation_widget_context_menu, xml_structure_context_menu
from lib.ui.CodeEditors import xml_editor
""" database connector imports"""
from lib.db.database import DatabaseConnection

""" XML library """
from lib.xml.transport_template import transport_template
from lib.xml.transport_template_custom_object import transport_template_custom_object
from lib.xml.transport_task import transport_task
from lib.xml.object_container import object_container
from lib.xml.sql_script_container import sql_script_container

VERSION = '0.4.1'
XML_PREVIEW_TIMER = 200
        
class Transport_Manager(QMainWindow):
    """Main window class for session launcher"""

    refresh_widget = pyqtSignal(object)
    xml_structure_changed = pyqtSignal()
    
    def __init__(
        self, parent=None, clipboard=None, event_filter=None, qapplication=None
    ):
        QMainWindow.__init__(self, parent)
        """ Map QT UI from parsed file - created and updated in qt designer """

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        

        self.setWindowTitle(f"Transport Manager Tool - {VERSION}")
        window_icon = QIcon("./icon.ico")
        self.setWindowIcon(window_icon)
        self.color_theme = Application_Theme()

        """ Connect UI signals """
        self.closeEvent = self.close_application
        self.ui.actionAdd_DatabaseConnection.triggered.connect(self.get_session_details)
        self.ui.FindObjectButton.clicked.connect(self.find_objects)
        self.ui.TableComboBox.currentTextChanged.connect(self.load_db_objects)
        self.ui.AddSelectedObjectsWithRelationsButton.clicked.connect(self.select_object_for_transport)
        self.ui.SearchResultsListWidget.itemClicked.connect(self.select_source_object)
        self.ui.XMLStructureTreeWidget.itemClicked.connect(self.select_source_object)
        self.ui.RelationsViewTreeWidget.itemChanged.connect(self.handle_data_change)
        self.ui.XMLStructureTreeWidget.itemChanged.connect(self.handle_data_change)
        self.ui.XMLStructureTreeWidget.dragMoveEvent = self.xml_structure_move_event
        self.ui.XMLStructureTreeWidget.dropEvent = self.xml_structure_drop_event
        self.ui.actionSaveFile.triggered.connect(self.save_file)
        self.ui.actionSave_As.triggered.connect(self.save_as_other_file)
        self.ui.actionOpen_File.triggered.connect(lambda: self.open_file())
        self.ui.actionChange_WorkingDirectory.triggered.connect(self.change_workdir)
        self.ui.DeselectAllToolButton.clicked.connect(self.deselect_all_relations)
        self.ui.AddAsSingleObjectsButton.clicked.connect(lambda: self.select_object_for_transport(add_without_relations=True))
        self.ui.ApplyPresetToolButton.clicked.connect(self.apply_table_relation_preset)
        self.ui.PackageViewTreeWidget.itemDoubleClicked.connect(self.load_package_definition)

        """ UI Configurations """
        
        self.ui.XMLEditorWidget = xml_editor(self)
        self.ui.current_file_label = QLabel(self)
        self.ui.current_file_label.setProperty("Widget", "FilePathLabel")
        self.ui.current_file_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse|Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.ui.XMLEditorLayout.insertWidget(0, self.ui.current_file_label)
        self.ui.XMLEditorLayout.insertWidget(1, self.ui.XMLEditorWidget)

        self.ui.PackageManagerSplitter_Left.setSizes([round(self.width()*0.2), round(self.width()*0.2)])
        self.ui.PackageManagerSplitter_Right.setSizes([round(self.width()*0.5), round(self.width()*0.5)])

        self.ui.TemplateEditorSplitter_Search.setSizes([round(self.height()*0.1), round(self.height()*0.3)])
        self.ui.TemplateEditorSplitter_Relations.setSizes([round(self.height()*0.2), round(self.height()*0.2)])

        self.ui.TemplateEditorSplitter_Left.setSizes([1, round(self.width()*0.8)])
        self.ui.TemplateEditorSplitter_Right.setSizes([round(self.width()*0.4), round(self.width()*0.6)])

        self.ui.RelationsViewTreeWidget.setHeaderHidden(False)
        self.ui.RelationsViewTreeWidget.setHeaderLabels(['Related Table(references)', 'FK', 'CR', 'SH'])
        self.ui.RelationsViewTreeWidget.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.ui.RelationsViewTreeWidget.header().setStretchLastSection(False)
        self.ui.RelationsViewTreeWidget.setColumnCount(4)
        self.ui.RelationsViewTreeWidget.setColumnWidth(1, 30)
        self.ui.RelationsViewTreeWidget.setColumnWidth(2, 30)
        self.ui.RelationsViewTreeWidget.setColumnWidth(3, 30)

        self.ui.XMLStructureTreeWidget.setHeaderHidden(False)
        self.ui.XMLStructureTreeWidget.setHeaderLabels(['Transport Structure', 'Task Options'])
        self.ui.XMLStructureTreeWidget.setColumnWidth(0, 500)    
        self.ui.XMLStructureTreeWidget.setColumnWidth(1, 200)    
        self.ui.XMLStructureTreeWidget.setWordWrap(True)
        self.ui.FindObjectButton.setEnabled(False)
        self.ui.TableComboBox.setEnabled(False)

        """ Context Menu """
        self.ui.RelationsViewTreeWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.RelationsViewTreeWidget.customContextMenuRequested.connect(self.relation_context_menu)
        self.ui.XMLStructureTreeWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.XMLStructureTreeWidget.customContextMenuRequested.connect(self.xml_structure_context_menu)

        self.xml_structure_changed.connect(self.reload_xml_preview)
        self.xml_preview_timer = QTimer(self)
        self.xml_preview_timer.setSingleShot(True)
        self.xml_preview_timer.timeout.connect(self.load_xml_preview)

        self.current_workdir = None
        self.current_file = None


        """ Shortcuts """
        QShortcut(QKeySequence.StandardKey.Delete, self, self.remove_selected_nodes)
        QShortcut(QKeySequence.StandardKey.Refresh, self, self.refresh_ui)

        self.refresh_ui()
        self.show()

        """ Program variables """
        self.db = None
        self.encryption_key = None
        self.last_widget_clicked = None

        """ Saved Session data """
        self.sessions = self.settings.value("sessions")
        if self.sessions is None:
            self.sessions = {}

        if len(self.sessions) > 0:
            encryption_key = self.get_encryption_key()
            if encryption_key:
                self.encryption_key = encryption_key
                if self.decrypt_session_details():
                    self.load_saved_sessions()
                else:
                    print("session data decryption failed")
                    self.sessions = {}
            else:
                print("session details were not loaded")
                self.sessions = {}
        
        """ Saved relation presets data """
        self.relation_presets = self.settings.value("relation_presets")
        if self.relation_presets is None:
            self.relation_presets = {}

        """ Initial transport template object """
        self.transport_template = transport_template(self)
        self.xml_structure_changed.emit()

    def refresh_ui(self):
        """ UI style scheme """
        self.setStyleSheet(self.color_theme.style_sheet)

        """ Restore window settings """
        self.settings = QSettings("EmergencyCode", "Transport_Manager")
        if self.settings.value("geometry") is not None:
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("windowState") is not None:
            self.restoreState(self.settings.value("windowState"))

        self.load_workdir()

    """ Database Session Management """

    def connect_database(self, session_name):
        if not isinstance(self.sessions, dict):
            return False
        
        if session_name not in self.sessions.keys():
            return False
        
        self.ui.statusbar.showMessage(f"Using session info: {session_name}")

        session_params = self.sessions[session_name]

        if self.db is not None:
            self.db.disconnect_db()
            self.db = None

        self.db = DatabaseConnection(session_params)
        
        if self.db is not None:
            self.db.load_session_data()
            self.reload_ui_data()

    """ Workdir and File Operations """

    def change_workdir(self):
        dialog = QFileDialog(self, "Transport Manager - Select Working Directory")
        dialog.setFileMode(QFileDialog.FileMode.Directory)

        file_path = dialog.getExistingDirectory(options=QFileDialog.Option.ReadOnly)
        if file_path != "":
            self.current_workdir = file_path
            self.load_workdir(file_path)
    
    def load_workdir(self, workdir=None):
        if workdir is None and self.current_workdir is not None:
            workdir = self.current_workdir
        if workdir is None:
            return False
        workdir_path = Path(workdir).absolute()
        # self.ui.PackageViewTreeWidget.setColumnCount(2)
        self.ui.PackageViewTreeWidget.clear()
        folders = {}
        for file_path in Path(workdir).rglob( '*.xml' ):
            
            parent_paths = file_path.parents
            
            folder = None
            for parent in parent_paths:
                parent_path = parent.absolute()
                if parent.is_dir() and workdir_path < parent_path:
                    if parent_path not in folders.keys():
                        folder = PackageManagerXMLFolder(self, parent)
                        folder.setData(1, Qt.ItemDataRole.InitialSortOrderRole, 10)
                        folders[parent_path] = folder

            if file_path.is_file():
                file_widget = PackageManagerXMLFile(self, file_path)
                file_widget.setData(1, Qt.ItemDataRole.InitialSortOrderRole, 20)
                parent_folder = folders.get(file_path.parent.absolute(), None)
                if parent_folder:
                    parent_folder.addChild(file_widget)
                else:
                    self.ui.PackageViewTreeWidget.addTopLevelItem(file_widget)

        for folder_path, folder_widget in folders.items():
            parent_widget = folders.get(folder_widget.parent_directory, None)
            if parent_widget:
                parent_widget.addChild(folder_widget)
            else:
                self.ui.PackageViewTreeWidget.addTopLevelItem(folder_widget)

        self.ui.PackageViewTreeWidget.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        

    def load_package_definition(self, source_widget=None):
        if isinstance(source_widget, PackageManagerXMLFile):
            self.open_file(source_widget.path)

    def open_file(self, file_path=None):
        if file_path is None:
            dialog = QFileDialog(self, "Open existing template file")
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

            file_path = dialog.getOpenFileName(filter="*.xml")
            file_path = file_path[0]

        if file_path:
            self.transport_template.parse_xml_file(file_path)
            self.current_file = file_path
            self.ui.current_file_label.setText(file_path)
        self.ui.MainTabWidget.setCurrentWidget(self.ui.MainTabWidget_Transport_Template_Editor)
        self.xml_structure_changed.emit()

    def save_file(self):
        if self.current_file is not None:
            with open(self.current_file, 'w') as doc:
                doc.write(self.transport_template.string)
        else:
            self.save_as_other_file()

    def save_as_other_file(self):
        dialog = QFileDialog(self, "Save As")
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)

        file_path = dialog.getSaveFileName(filter="*.xml")

        if file_path[0] != "":
            with open(file_path[0], 'w') as doc:
                doc.write(self.transport_template.string)

    """ Session Data Management """

    def get_encryption_key(self, initial=False):
        encryption_key = EncryptionKeyDialog(self, initial)
        if encryption_key.exec():
            enc = hashlib.sha3_512(bytes(encryption_key.encryption_key, 'utf-8'))
            return enc.hexdigest()
        return False
        
    def decrypt_session_details(self):
        encrypted_session_details = self.sessions
        if isinstance(encrypted_session_details, dict):
            return True

        if self.encryption_key is None:
            self.encryption_key = self.get_encryption_key()

        byte_key = bytes(self.encryption_key, 'utf-8')[0:32]
        b64_byte_key = base64.urlsafe_b64encode(byte_key)

        crypto = Fernet(b64_byte_key)
        try:
            decrypted_session_details = crypto.decrypt(encrypted_session_details)
        except:
            return False

        session_data = json.loads(decrypted_session_details)
        if session_data:
            self.sessions = session_data
            return True
        return False

    def save_session_details(self):
        if len(self.sessions) == 0:
            self.settings.setValue("sessions", {})
            return True
        
        encoded_session_data = json.dumps(self.sessions).encode('utf-8')

        if self.encryption_key is None:
            self.encryption_key = self.get_encryption_key(initial=True)

        byte_key = bytes(self.encryption_key, 'utf-8')[0:32]
        b64_byte_key = base64.urlsafe_b64encode(byte_key)

        crypto = Fernet(b64_byte_key)
        encrypted_session_details = crypto.encrypt(encoded_session_data)

        self.settings.setValue("sessions", encrypted_session_details)

    def load_saved_sessions(self):
        if self.sessions is not None:
            if isinstance(self.sessions, dict):
                for session_name in self.sessions.keys():
                    self.add_session_to_menu(session_name)

    def get_session_details(self, session_name=None):
        session_data = self.sessions.get(session_name, None)
        dialog = SessionDetailsDialog(self, session_data)
        if dialog.exec():
            if dialog.session_name not in self.sessions.keys() and not session_name:
                self.add_session_to_menu(dialog.session_name)

            if session_name and dialog.session_name != session_name:
                source_session = self.ui.menuConnections.findChildren(QMenu, session_name, Qt.FindChildOption.FindDirectChildrenOnly)
                if len(source_session) == 1:
                    source_session = source_session[0]
                    source_session.setObjectName(dialog.session_name)
                    source_session.setTitle(dialog.session_name)
                    self.sessions.pop(session_name)

            self.sessions[dialog.session_name] = dialog.form_values
            self.save_session_details()

    def add_session_to_menu(self, session_name):
        NewMenuItem = self.ui.menuConnections.addMenu(session_name)
        NewMenuItem.setObjectName(session_name)
        ConnectAction = NewMenuItem.addAction("Connect")
        EditAction = NewMenuItem.addAction("Edit")
        NewMenuItem.addSeparator()
        DeleteAction = NewMenuItem.addAction("Delete")

        ConnectAction.triggered.connect(lambda: self.connect_database(NewMenuItem.objectName()))
        EditAction.triggered.connect(lambda: self.get_session_details(NewMenuItem.objectName()))
        DeleteAction.triggered.connect(lambda: self.delete_session(NewMenuItem))

    def delete_session(self, session_menu_object):
        session_name = session_menu_object.title()

        decision = QMessageBox.question(self, "Confirm Session Delete", f"Are you sure to delete session info: {session_name}?")
        if decision == QMessageBox.StandardButton.Yes:
            action = session_menu_object.menuAction()
            self.ui.menuConnections.removeAction(action)
            
            self.sessions.pop(session_name)
            self.save_session_details()

    """ Relations Management """

    def relation_context_menu(self, menuPosition):
        clickedItem = self.ui.RelationsViewTreeWidget.itemAt(menuPosition)
        if clickedItem:
            contextMenu = relation_widget_context_menu(self, clickedItem)
            contextMenu.follow_table_relations.connect(self.follow_table_relation)
            menu_target = self.ui.RelationsViewTreeWidget.mapToGlobal(menuPosition)
            contextMenu.popup(menu_target)

    def get_table_initial_relations(self, table_name, extended_view=False):
        initial_relations = copy.deepcopy(self.db.table_relations.get(table_name, None))
        
        if initial_relations is None:
            return []
        get_extended_view = extended_view 
        if not get_extended_view:
            return initial_relations

        relation_tables = []

        for relation in initial_relations:
            child_table = relation.get("ChildTable", None)
            if child_table is not None:
                if child_table != table_name and child_table not in relation_tables:
                    relation_tables.append(child_table)
            
        for relation_table in relation_tables:
            new_table_relations = self.db.table_relations.get(relation_table, None)
            if new_table_relations is not None:
                initial_relations = self.extend_table_relations(initial_relations, new_table_relations)

        return initial_relations

    def deselect_all_relations(self):
        list_widgets = [self.ui.XMLStructureTreeWidget, self.ui.SearchResultsListWidget]
        select_element = None
        for selected_widget in list_widgets:
            if self.last_widget_clicked == selected_widget:
                for element in selected_widget.selectedItems():
                    if isinstance(element, (TE_ObjectContainer_TreeWidgetItem, TemplateEditorListWidgetItem)):
                        element.set_all_relations_state(0)
                        select_element = element

        if select_element is not None:
            self.select_source_object(select_element)

    def save_relation_preset(self, source_widget):
        relation_dialog = RelationPresetDialog(self)
        if isinstance(source_widget, TE_ObjectContainer_TreeWidgetItem):
            relation_dialog.relations = copy.deepcopy(source_widget.object_relations)

        if relation_dialog.exec():
            preset_dict = {relation_dialog.name: relation_dialog.preset_data}
            if source_widget.table_name not in self.relation_presets.keys():
                self.relation_presets[source_widget.table_name] = preset_dict

            if relation_dialog.name not in self.relation_presets[source_widget.table_name].keys():
                self.relation_presets[source_widget.table_name][relation_dialog.name] = relation_dialog.preset_data
            else:
                """ overwrite existing? """
                self.relation_presets[source_widget.table_name][relation_dialog.name] = relation_dialog.preset_data

        self.settings.setValue("relation_presets", self.relation_presets)

    def load_table_relation_presets(self, table_name):
        self.ui.RelationPresetsComboBox.clear()

        table_presets = self.relation_presets.get(table_name, None)
        if table_presets is not None:
            for preset_name, preset_data in table_presets.items():
                self.ui.RelationPresetsComboBox.addItem(preset_name)
    
    def apply_table_relation_preset(self):
        preset_name = self.ui.RelationPresetsComboBox.currentText()
        preset_data = None
        preset_table = None
        for table_name, relations in self.relation_presets.items():
            preset_data = relations.get(preset_name, None)
            if preset_data is not None:
                preset_table = table_name
                break
    
        if preset_data:
            if self.last_widget_clicked == self.ui.XMLStructureTreeWidget:
                for element in self.ui.XMLStructureTreeWidget.selectedItems():
                    if isinstance(element, TE_ObjectContainer_TreeWidgetItem) and element.table_name == preset_table:
                        preset_data_relations = copy.deepcopy(preset_data["table_relations"])
                        element.set_object_relations(preset_data_relations)
                        self.select_source_object(element)
            
            if self.last_widget_clicked == self.ui.SearchResultsListWidget:
                for element in self.ui.SearchResultsListWidget.selectedItems():
                    if isinstance(element, TemplateEditorListWidgetItem) and element.table_name == preset_table:
                        preset_data_relations = copy.deepcopy(preset_data["table_relations"])
                        element.set_object_relations(preset_data_relations)
                        self.select_source_object(element)

    def follow_table_relation(self, relation_widget):
        if relation_widget.follow_table:
            source_widget_relations = relation_widget.source_widget.object_relations

            # new_relations = copy.deepcopy(self.db.child_table_relations.get(relation_widget.follow_table, None))
            # if new_relations is None:
            new_relations = copy.deepcopy(self.db.table_relations.get(relation_widget.follow_table, None))

            if new_relations is not None:
                merged_relations = self.extend_table_relations(source_widget_relations, new_relations)
                relation_widget.source_widget.object_relations = merged_relations

                if isinstance(relation_widget.source_widget, TemplateEditorTreeWidgetItem):
                    relation_widget.source_widget.refresh()

                self.load_table_relations(new_relations, relation_widget.source_widget, relation_widget)

    def extend_table_relations(self, current_relations, new_relations):
        current = current_relations

        new = new_relations
        if new is None:
            return current
        
        for relation in new:
            check = next((current_item for current_item in current if current_item["ParentTable"] == relation["ParentTable"] and current_item["ChildTable"] == relation["ChildTable"]) , None)
            if check is None:
                current.append(relation)
            else:
                continue
        return current

    """ XML Structure Management """
    def xml_structure_context_menu(self, menuPosition):
        clickedItem = self.ui.XMLStructureTreeWidget.itemAt(menuPosition)
        contextMenu = xml_structure_context_menu(self, clickedItem)
        contextMenu.list_related_objects.connect(lambda: self.list_related_objects(clickedItem, True))
        contextMenu.load_object_from_database.connect(lambda: self.load_objects_from_database(clickedItem))
        contextMenu.save_relation_preset.connect(lambda: self.save_relation_preset(clickedItem))
        contextMenu.add_transport_task.connect(self.add_transport_task)
        contextMenu.edit_sql_script.connect(self.edit_sql_script)
        contextMenu.add_sql_script.connect(self.add_sql_script)

        if len(contextMenu.menu_items) > 0:
            menu_target = self.ui.XMLStructureTreeWidget.mapToGlobal(menuPosition)
            contextMenu.popup(menu_target)

    def reload_xml_preview(self):
        self.xml_preview_timer.start(XML_PREVIEW_TIMER)

    def load_xml_preview(self):
        # print("load xml preview")
        self.ui.XMLEditorWidget.setText(self.transport_template.string)

    def xml_structure_move_event(self, event):
        move_accept = True
        source_widget = event.source().currentItem()

        QTreeWidget.dragMoveEvent(self.ui.XMLStructureTreeWidget, event)

        dropItem = self.ui.XMLStructureTreeWidget.itemAt(event.position().toPoint())
        dropIndicator = self.ui.XMLStructureTreeWidget.dropIndicatorPosition()
        
        if dropItem is not None:
            self.ui.XMLStructureTreeWidget.setDropIndicatorShown(True)

        if dropIndicator == QAbstractItemView.DropIndicatorPosition.OnItem:
            if isinstance(dropItem, TE_ObjectContainer_TreeWidgetItem):
                move_accept = False

            if isinstance(dropItem, TE_Table_TreeWidgetItem):
                move_accept = False
            
            if isinstance(dropItem, TE_ObjectContainerData_TreeWidgetItem):
                move_accept = False

            if isinstance(dropItem, TE_TransportTask_TreeWidgetItem) and isinstance(source_widget, TE_TransportTask_TreeWidgetItem):
                move_accept = False

        if dropIndicator == QAbstractItemView.DropIndicatorPosition.BelowItem:
            if isinstance(dropItem, TE_TransportTask_TreeWidgetItem):
                move_accept = False
        
        if not move_accept:
            event.ignore()

    def xml_structure_drop_event(self, event):
        QTreeWidget.dropEvent(self.ui.XMLStructureTreeWidget, event)
        self.reset_xml_order()
    
    def reset_xml_order(self):
        self.transport_template.clear_xml_tasks()
        iterator = QTreeWidgetItemIterator(self.ui.XMLStructureTreeWidget, QTreeWidgetItemIterator.IteratorFlag.Selectable)
        current_task_data = None
        while iterator.value():
            item = iterator.value()
            iterator += 1
            if isinstance(item, TE_TransportTask_TreeWidgetItem) and item.xml_object is not None:
                self.transport_template.tasks_root.append(item.xml_object.data)
                if item.childCount() > 0:
                    item.xml_object.delete_child_items()
                current_task_data = item.xml_object.data
                continue

            if isinstance(item.xml_object, transport_template_custom_object):
                if item.xml_object.data is not None:
                    if item.xml_object.description is not None and current_task_data is not None:
                        current_task_data.append(item.xml_object.description)
                    current_task_data.append(item.xml_object.data)
        self.xml_structure_changed.emit()

    def reload_xml_structure(self):
        """ reload structure according to the xml structure data """
        self.ui.XMLStructureTreeWidget.clear()
        task_treewidget_item = None
        for task in self.transport_template.tasks:
            
            if task.task_class == "VI.Transport.ObjectTransport, VI.Transport":
                task_treewidget_item = TE_ObjectTransportTask_TreeWidgetItem(self, object_data=task, xml_object=task)
                for task_container_xml in task.task_containers:
                    container_element = object_container(self, source_element=task_container_xml)
                    object_container_widget = TE_ObjectContainer_TreeWidgetItem(self, object_data=None, xml_object=container_element)
                    task_treewidget_item.addChild(object_container_widget)

            if task.task_class == "VI.Transport.SQLTransport, VI.Transport":
                task_treewidget_item = TE_SQLTransportTask_TreeWidgetItem(self, object_data=task, xml_object=task)
                for task_container_xml in task.task_containers:
                    container_element = sql_script_container(self, source_element=task_container_xml)
                    if container_element.script_type != "PreImport":
                        object_container_widget = TE_SQLScriptContainer_TreeWidgetItem(self, object_data=None, xml_object=container_element)
                        task_treewidget_item.addChild(object_container_widget)
            if task_treewidget_item is None:
                task_treewidget_item = TE_TransportTask_TreeWidgetItem(self, object_data=task, xml_object=task)
                
            if task_treewidget_item:
                self.ui.XMLStructureTreeWidget.addTopLevelItem(task_treewidget_item)
                task_treewidget_item.setExpanded(True)

    """ Custom Widget Operations """

    def handle_data_change(self, changed_widget, column):       
        if isinstance(changed_widget, TemplateEditorTreeWidgetItem):
            changed_widget.handle_data_change(column)
        self.xml_structure_changed.emit()

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
        self.xml_structure_changed.emit()

    def clear_widgets(self):
        self.ui.TableComboBox.clear()
        self.ui.TableFilter.clear()

    def reload_ui_data(self):
        if self.db.is_connected:
            self.ui.FindObjectButton.setEnabled(True)
            self.ui.TableComboBox.setEnabled(True)

        self.ui.TableComboBox.clear()
        for table_name in self.db.table_info.keys():
            self.ui.TableComboBox.addItem(table_name)

    def select_source_object(self, source_widget):
        if isinstance(source_widget, TemplateEditorListWidgetItem):
            self.last_widget_clicked = source_widget.listWidget()
        
        if isinstance(source_widget, TE_ObjectContainer_TreeWidgetItem):
            self.last_widget_clicked = source_widget.treeWidget()

        if isinstance(source_widget, TE_ObjectContainer_TreeWidgetItem) or isinstance(source_widget, TemplateEditorListWidgetItem):
            relations = source_widget.object_relations
            self.ui.RelationsViewTreeWidget.clear()

            if relations is not None:
                self.load_table_relations(relations, source_widget)  

            if isinstance(source_widget, TE_ObjectContainer_TreeWidgetItem):
                self.ui.XMLEditorWidget.find_text(source_widget.search_text)
            
            self.load_table_relation_presets(source_widget.table_name)

    def add_transport_task(self, task_type):
        """ Create XML Node """

        task = self.transport_template.add_transport_task(task_type)
        task_item = None

        if task_type == "VI.Transport.ObjectTransport, VI.Transport":
            task_item = TE_ObjectTransportTask_TreeWidgetItem(self, task, task)
        elif task_type == "VI.Transport.SQLTransport, VI.Transport":
            task_item = TE_SQLTransportTask_TreeWidgetItem(self, task, task)
        else:
            task_item = TE_TransportTask_TreeWidgetItem(self, task, task)

        self.ui.XMLStructureTreeWidget.addTopLevelItem(task_item)

        self.xml_structure_changed.emit()
        return task_item
    
    def select_object_for_transport(self, add_without_relations=False):
        selected_source_widgets = self.ui.SearchResultsListWidget.selectedItems()
        if selected_source_widgets is not None:
            selected_target_widgets = self.ui.XMLStructureTreeWidget.selectedItems()
            task_item = None
            if len(selected_target_widgets) == 0:
                """ Create UI Node """
                task_item = self.add_transport_task("VI.Transport.ObjectTransport, VI.Transport")
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
                    pk_columns_dict = {}
                    for pk_column in source_widget.pk_columns:
                        if pk_column is not None and pk_column not in pk_columns_dict.keys():
                            pk_columns_dict[pk_column] = source_widget.get_value(pk_column)

                    container_element = task_item.xml_object.add_container(base_table=source_widget.table_name, display_name=source_widget.display_name, delete_residual_objects=str(int(self.ui.DeleteResidualCheckBox.isChecked())), pk_columns=pk_columns_dict, relations=source_widget.object_relations)

                    object_container = TE_ObjectContainer_TreeWidgetItem(self, object_data=source_widget.object_data, xml_object=container_element, source_widget=source_widget, table_name=source_widget.table_name)
                    
                    container_element.relations = object_container.object_relations

                    task_item.addChild(object_container)

                    if add_without_relations:
                        object_container.set_all_relations_state(0)
                    
                    task_item.setExpanded(True)

        self.xml_structure_changed.emit()

    """ SQL Script tasks handling """
    def add_sql_script(self, source_widget_item, script_type):
        if isinstance(source_widget_item, TE_SQLTransportTask_TreeWidgetItem):
            source_widget_item.add_script(script_type)
            self.xml_structure_changed.emit()

    def edit_sql_script(self, source_widget_item):
        dialog = ScriptEditorDialog(self, source_widget_item.script)
        if dialog.exec():
            source_widget_item.set_script(dialog.script)
            self.xml_structure_changed.emit()

    """ Object Loading and Listing  """

    def list_related_objects(self, source_widget_item, override=False):
        tree_widget = self.ui.XMLStructureTreeWidget
        for element in tree_widget.selectedItems():
            if isinstance(element, TE_ObjectContainer_TreeWidgetItem):
                element.list_related_objects(True)
        
        if len(tree_widget.selectedItems()) == 0:
            source_widget_item.list_related_objects(True)

    def load_objects_from_database(self, source_widget_item):
        tree_widget = self.ui.XMLStructureTreeWidget
        for element in tree_widget.selectedItems():
            if isinstance(element, TE_ObjectContainer_TreeWidgetItem):
                element.load_from_database()
        
        if len(tree_widget.selectedItems()) == 0:
            source_widget_item.load_from_database()

    def load_db_objects(self, table_name=None, data_rows=[]):
        self.ui.SearchResultsListWidget.clear()

        if len(data_rows) == 0 and table_name: 
            query = f"select * from {table_name}"
            data_rows = self.db.run_db_query(query)

        for row in data_rows:
            w = TemplateEditorListWidgetItem(self, row, table_name=table_name)
            self.ui.SearchResultsListWidget.addItem(w)

        self.load_table_relation_presets(table_name)

    def get_objectkey_table(self, input_string):
        table_name = None
        regex = r"<T>(.*?)</T>"
        if input_string is not None:
            match = re.search(regex, input_string)
            if match:
                table_name = match.group(1)
        return table_name

    def find_objects(self):
        if not self.db.is_connected:
            return False
        
        filter = self.ui.ObjectQueryTextEdit.toPlainText()
        data_rows = []

        if self.ui.XObjectKeysFilterRadioButton.isChecked():
            filter_rows = filter.splitlines()
            for object_query in filter_rows:
                object_query = object_query.strip()
                table_name = self.get_objectkey_table(object_query)
                if table_name is not None:
                    query = f"select * from {table_name} where XObjectKey = '{object_query}'"
                    data_rows += self.db.run_db_query(query)

        if self.ui.SelectedTableFilterRadioButton.isChecked() and self.ui.TableComboBox.currentText().strip() != "":
            object_query = filter.strip()
            table_name = self.ui.TableComboBox.currentText()
            if len(object_query) > 0:
                query = f"select * from {table_name} where {object_query}"
                data_rows += self.db.run_db_query(query)
            else:
                query = f"select * from {table_name}"
                data_rows += self.db.run_db_query(query)

        self.load_db_objects(data_rows=data_rows)

    def load_table_relations(self, relations, source_widget, append_to_existing_widget=None):
        if append_to_existing_widget is None:
            self.ui.RelationsViewTreeWidget.clear()

        tree_widgets = {}
        # print(len(relations))
        if relations is None:
            return False
        
        for relation in relations:
            parent_table_name = relation["ParentTable"]
            child_table_name = relation["ChildTable"]

            ui_parent_table_name = child_table_name

            if parent_table_name == child_table_name and child_table_name != source_widget.table_name:
            # if parent_table_name == source_widget.table_name:
                ui_parent_table_name = parent_table_name

            if ui_parent_table_name == source_widget.table_name and append_to_existing_widget is not None:
                """ skip relations referenced to the base table of the object """
                continue
            
            child_widget = TE_RelationColumn_TreeWidgetItem(self, relation, source_widget=source_widget)
            
            if append_to_existing_widget is not None and ui_parent_table_name == append_to_existing_widget.follow_table:
                if ui_parent_table_name not in tree_widgets.keys():
                    tree_widgets[ui_parent_table_name] = append_to_existing_widget

            if ui_parent_table_name not in tree_widgets.keys():
                table_info = ui_parent_table_name
                if self.db:
                    table_info = self.db.table_info.get(ui_parent_table_name, ui_parent_table_name)
                parent_widget = TE_Table_TreeWidgetItem(self, table_info, source_widget=source_widget)
                tree_widgets[ui_parent_table_name] = parent_widget
            else:
                parent_widget = tree_widgets[ui_parent_table_name]
            

            """ Connect main application signals """
            self.ui.ShowAllColumnsCheckBox.stateChanged.connect(child_widget.show_relation)
            # self.ui.SelectWithDatabaseModelCheckBox.stateChanged.connect(child_widget.select_relations_using_db_model)

            parent_widget.addChild(child_widget)
            # child_widget.show_relation(self.ui.ShowAllColumnsCheckBox.isChecked())

        for parent_widget in tree_widgets.values():
            if parent_widget.childCount() > 0:
                if isinstance(append_to_existing_widget, TemplateEditorTreeWidgetItem):
                    append_to_existing_widget.addChild(parent_widget)
                    continue
                self.ui.RelationsViewTreeWidget.addTopLevelItem(parent_widget)

        self.ui.RelationsViewTreeWidget.sortItems(0, Qt.SortOrder.AscendingOrder)

        self.ui.ShowAllColumnsCheckBox.stateChanged.emit(int(self.ui.ShowAllColumnsCheckBox.isChecked()))

        table_widget = tree_widgets.get(source_widget.table_name, None)

        if isinstance(table_widget, TE_Table_TreeWidgetItem):
            table_widget.setExpanded(True)

    """ Application close """

    def close_application(self, event, force=False):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("relation_presets", self.relation_presets)

        if len(self.sessions) > 0:
            self.save_session_details()

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
        MsgBox(self, exc_type.__name__, log_msg)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    a = Transport_Manager(
        clipboard=app.clipboard(), event_filter=None, qapplication=app
    )

    sys.excepthook = a.qt_exception_hook
    app.exec()