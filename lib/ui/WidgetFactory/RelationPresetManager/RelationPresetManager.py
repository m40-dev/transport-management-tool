# Standard modules


#""" Required QT Libraries """
from PyQt6 import QtWidgets, QtCore
from .RelationPresetContextMenu import RelationPresetContextMenu
from lib.ui.WidgetFactory import FormEditorDialog

# Data Models
# from lib.data.DataModels import RelationPresetConfigurationModel

RELATION_PRESET = "Relation Preset"
OBJECT_TABLE = "Base Object Class"
TABLE_REFERENCE = "Relation Reference Table"
OBJECT_RELATION = "Object Relation"

from PyQt6.QtGui import QShortcut, QKeySequence
class RelationPresetManager(QtWidgets.QWidget):

    def __init__(self, parent, preset_data):
        super().__init__(parent=parent, flags=QtCore.Qt.WindowType.Dialog)
        self.parent = parent
        self.application = parent
        self.preset_data = preset_data
        self.setWindowTitle(self.application.application_name + " - Manage Relation Presets") 
        
        self.setupUi()
        self.loadPresetData()
        self.show()
        self.restoreWindowState()
        self.closeEvent = self.windowCloseEventHandler

    def windowCloseEventHandler(self, event):
        self.saveWindowState()
        event.accept()

    def restoreWindowState(self):
        """ Restore window settings """
        # print("restore window")
        self.settings = self.application.settings
        if self.settings.value("RelationPresetManagerGeometry") is not None:
            self.restoreGeometry(self.settings.value("RelationPresetManagerGeometry"))

    def saveWindowState(self):
        # print("save window")
        self.application.settings.setValue("RelationPresetManagerGeometry", self.saveGeometry())

    def loadPresetData(self):
        for table_name, table_presets in self.preset_data.items():
            table_widget = RelationPresetTreeWidgetItem(self.RelationPresetTreeWidget, table_name, table_presets)
            self.RelationPresetTreeWidget.addTopLevelItem(table_widget)

    def contextMenuRequested(self, menuPosition):
        clickedItem = self.RelationPresetTreeWidget.itemAt(menuPosition)
        contextMenu = RelationPresetContextMenu(self, clickedItem)
        menu_target = self.RelationPresetTreeWidget.mapToGlobal(menuPosition)

        """ Connect Signals """
        contextMenu.editPresetData.connect(self.editPresetData)
        contextMenu.removePresetData.connect(self.removeSelectedItems)

        if len(contextMenu.menu_items) > 0:
            contextMenu.popup(menu_target)
    
    def editPresetData(self, selectedItem):
        dialog = FormEditorDialog(self.application, "XMLTemplateEditor_RelationPreset")
        dialog.set_dictionary_data(selectedItem.preset_data)
        if dialog.exec():
            selectedItem.preset_data.update(dialog.form_data)
            selectedItem.refresh_ui()
            self.parent.updateRelationPresets()

    def removeSelectedItems(self, selectedItem):
        selectedItems = self.RelationPresetTreeWidget.selectedItems()
        if len(selectedItems) > 1:
            for item in selectedItems:
                self.removePresetData(item)
            return True

        self.removePresetData(selectedItem)

    def removePresetData(self, selectedItem):
        parent_object = selectedItem.parent()
        if parent_object:
            parent_data = selectedItem.parent().preset_data

            if isinstance(parent_data, dict):
                if selectedItem.display in parent_data.keys():
                    parent_data.pop(selectedItem.display)

                if selectedItem.parent().object_type == RELATION_PRESET:
                    if ("table_relations" in parent_data.keys() 
                        and selectedItem.display in parent_data["table_relations"].keys()):
                        parent_data["table_relations"].pop(selectedItem.display)

            if isinstance(parent_data, list):
                parent_data.remove(selectedItem.preset_data)
            
            parent_object.removeChild(selectedItem)

        else:
            if selectedItem.display in self.preset_data.keys():
                self.preset_data.pop(selectedItem.display)
                self.RelationPresetTreeWidget.invisibleRootItem().removeChild(selectedItem)

    def setupUi(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.RelationPresetTreeWidget = QtWidgets.QTreeWidget()
        self.RelationPresetTreeWidget.setHeaderHidden(True)
        self.RelationPresetTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.RelationPresetTreeWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.RelationPresetTreeWidget.customContextMenuRequested.connect(self.contextMenuRequested)
        self.layout.addWidget(self.RelationPresetTreeWidget, 0, 0, 1, 1)

    
class RelationPresetTreeWidgetItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, parent, display_name="", preset_data={}):
        super().__init__(parent)
        self._display_name = display_name
        self.preset_data = preset_data
        self._object_type = OBJECT_TABLE

        if isinstance(preset_data, dict) and self.object_type == OBJECT_TABLE:
            for preset_name, preset_data in preset_data.items():
                RelationPresetTreeWidgetItem(self, preset_name, preset_data)
        
        if isinstance(preset_data, dict) and self.object_type == RELATION_PRESET:
            for target_table, table_relations in preset_data["table_relations"].items():
                RelationPresetTreeWidgetItem(self, target_table, table_relations)

        if isinstance(preset_data, list):
            for relation_entry in preset_data:
                if isinstance(relation_entry, dict) and "Relation" in relation_entry.keys():
                    RelationPresetTreeWidgetItem(self, relation_entry["Caption"], relation_entry)
        
        if self.object_type == OBJECT_RELATION:
            pass

        self.refresh_ui()

    def refresh_ui(self):
        if isinstance(self.preset_data, dict) and "name" in self.preset_data.keys():
            self.display = self.preset_data["name"]
            return True
        
        self.display = self._display_name

    @property
    def object_type(self):
        if isinstance(self.preset_data, dict) and "table_relations" in self.preset_data.keys():
            return RELATION_PRESET

        if isinstance(self.preset_data, list) and self.parent().object_type == RELATION_PRESET:
            return TABLE_REFERENCE

        if isinstance(self.preset_data, dict) and "Relation" in self.preset_data.keys():
            return OBJECT_RELATION

        return self._object_type

    @property
    def display(self):
        return self._display_name

    @display.setter
    def display(self, value):
        self.setText(0, f'{self.object_type} - {value}')
        self._display_name = value
        if self.object_type == OBJECT_RELATION:
            self.setText(0, f'{self.object_type} - {value}: {self.preset_data["ChildTable"]}|{self.preset_data["ChildColumn"]}|{self.preset_data["Relation"]}')



