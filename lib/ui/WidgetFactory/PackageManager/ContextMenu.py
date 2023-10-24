from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import pyqtSignal

class PackageDefinitionMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    
    addPackageDefinition = pyqtSignal(object)
    editPackageDefinition = pyqtSignal(object)
    addTaskDefinition = pyqtSignal(object)
    editXMLTemplate = pyqtSignal(object)
    editTaskDefinition = pyqtSignal(object)
    savePackageDefinition = pyqtSignal(object)
    editSelectedItems = pyqtSignal(object)

    collapseAll = pyqtSignal()
    expandAll = pyqtSignal()

    def __init__(self, parent, source_index):
        super(PackageDefinitionMenu, self).__init__(parent)
        self.parent = parent

        self.menu_items = []
        source_item = source_index.internalPointer()

        if len(self.parent.selectedItems()) > 1:
            action_EditSelectedItems = self.addAction("Edit Selected Items")
            action_EditSelectedItems.triggered.connect(lambda: self.editSelectedItems.emit(source_index))
            self.menu_items.append(action_EditSelectedItems)

        action_collapseAll = self.addAction("Collapse All Items")
        action_collapseAll.triggered.connect(self.collapseAll)

        action_expandAll = self.addAction("Expand All Items")
        action_expandAll.triggered.connect(self.expandAll)
        
        action_addPackageDefinition = self.addAction("Add Package Definition")
        action_addPackageDefinition.triggered.connect(lambda: self.addPackageDefinition.emit(source_index) )
        
        self.menu_items.append(action_expandAll)
        self.menu_items.append(action_collapseAll)
        self.menu_items.append(action_addPackageDefinition)

        if source_item:
            if source_item.task_class == "PackageManager_PackageDefinition":
                action_addPackageDefinition = self.addAction("Add Task Definition")
                action_addPackageDefinition.triggered.connect(lambda: self.addTaskDefinition.emit(source_index) )
                
                action_editPackageDefinition = self.addAction("Edit Package Definition")
                action_editPackageDefinition.triggered.connect(lambda: self.editPackageDefinition.emit(source_index))

                action_save_package_definition = self.addAction("Save Package Definition(s)")
                action_save_package_definition.triggered.connect(lambda: self.savePackageDefinition.emit(source_index))

                self.menu_items.append(action_addPackageDefinition)
                self.menu_items.append(action_editPackageDefinition)
                self.menu_items.append(action_save_package_definition)

            if source_item.task_class == "PackageManager_TaskDefinition":
                action_editTaskDefinition = self.addAction("Edit Task")
                action_editTaskDefinition.triggered.connect(lambda: self.editTaskDefinition.emit(source_index))
                self.menu_items.append(action_editTaskDefinition)

                action_editXMLTemplate = self.addAction("Edit Task Definition(s)")
                action_editXMLTemplate.triggered.connect(lambda: self.editXMLTemplate.emit(source_index))
                self.menu_items.append(action_editXMLTemplate)
        

            