from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import pyqtSignal


class RelationPresetContextMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    editPresetData = pyqtSignal(object)
    removePresetData = pyqtSignal(object)

    def __init__(self, parent, source_item):
        super(RelationPresetContextMenu, self).__init__(parent)
        self.parent = parent

        self.menu_items = []

        from .RelationPresetManager import RELATION_PRESET

        if source_item.object_type == RELATION_PRESET:
            action_editPresetData = self.addAction("Edit Preset Definition")
            action_editPresetData.triggered.connect(lambda: self.editPresetData.emit(source_item))
            self.menu_items.append(action_editPresetData)
        
        if source_item:
            action_removePresetData = self.addAction("Remove Preset Data")
            action_removePresetData.triggered.connect(lambda: self.removePresetData.emit(source_item))
            self.menu_items.append(action_removePresetData)
            