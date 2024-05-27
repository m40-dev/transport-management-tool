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
    sortChildItems = pyqtSignal(object)
    reapplyTemplates = pyqtSignal(object)
    deleteSelectedItems = pyqtSignal(object)
    cloneSelectedItem = pyqtSignal(object)

    collapseTree = pyqtSignal(object)
    expandTree = pyqtSignal(object)

    def __init__(self, parent, source_index):
        super(PackageDefinitionMenu, self).__init__(parent)
        self.parent = parent
        self.useExperimentalFeatures = self.parent.ProgramConfiguration.getConfigurationValue("ObjectModel", "UseExperimental")
        self.menu_items = []
        source_item = source_index.internalPointer()

        if len(self.parent.selectedItems()) > 1:
            action_EditSelectedItems = self.addAction("Edit Selected Items")
            action_EditSelectedItems.triggered.connect(lambda: self.editSelectedItems.emit(source_index))
            self.menu_items.append(action_EditSelectedItems)

        self.addSeparator()

        action_addPackageDefinition = self.addAction("Add Package Definition")
        action_addPackageDefinition.triggered.connect(lambda: self.addPackageDefinition.emit(source_index) )
        
        self.menu_items.append(action_addPackageDefinition)

        if source_item:
            self.addSeparator()

            action_collapseTree = self.addAction("Collapse Selected Items")
            action_collapseTree.triggered.connect(lambda: self.collapseTree.emit(source_index))

            action_expandTree = self.addAction("Expand Selected Items")
            action_expandTree.triggered.connect(lambda: self.expandTree.emit(source_index))

            self.menu_items.append(action_expandTree)
            self.menu_items.append(action_collapseTree)

            self.addSeparator()

            if source_item.task_class == "PackageManager_PackageDefinition":
                action_addPackageDefinition = self.addAction("Add Task Definition")
                action_addPackageDefinition.triggered.connect(lambda: self.addTaskDefinition.emit(source_index) )
                
                action_editPackageDefinition = self.addAction("Edit Package Definition")
                action_editPackageDefinition.triggered.connect(lambda: self.editPackageDefinition.emit(source_index))

                action_clonePackageItem = self.addAction("Clone Package Definition")
                action_clonePackageItem.triggered.connect(lambda: self.cloneSelectedItem.emit(source_index))

                action_save_package_definition = self.addAction("Save Package Definition(s)")
                action_save_package_definition.triggered.connect(lambda: self.savePackageDefinition.emit(source_index))

                self.addSeparator()

                action_sortChildren = self.addAction("Sort Task items")
                action_sortChildren.triggered.connect(lambda: self.sortChildItems.emit(source_index))

                self.menu_items.append(action_addPackageDefinition)
                self.menu_items.append(action_editPackageDefinition)
                self.menu_items.append(action_save_package_definition)
                self.menu_items.append(action_sortChildren)
                self.menu_items.append(action_clonePackageItem)

            if source_item.task_class == "PackageManager_TaskDefinition":
                action_editTaskDefinition = self.addAction("Edit Task")
                action_editTaskDefinition.triggered.connect(lambda: self.editTaskDefinition.emit(source_index))
                self.menu_items.append(action_editTaskDefinition)

                action_editXMLTemplate = self.addAction("Edit Task XML Definition(s)")
                action_editXMLTemplate.triggered.connect(lambda: self.editXMLTemplate.emit(source_index))
                self.menu_items.append(action_editXMLTemplate)

                action_cloneTaskItem = self.addAction("Clone Task")
                action_cloneTaskItem.triggered.connect(lambda: self.cloneSelectedItem.emit(source_index))
                self.menu_items.append(action_cloneTaskItem)
            
            self.addSeparator()
            action_deleteSelectedItems = self.addAction("Delete Selected Items")
            action_deleteSelectedItems.triggered.connect(lambda: self.deleteSelectedItems.emit(source_index))
            self.menu_items.append(action_deleteSelectedItems)

            if self.useExperimentalFeatures:
                self.addSeparator()
                action_reapplyTemplates = self.addAction("Reapply Attribute Templates")
                action_reapplyTemplates.triggered.connect(lambda: self.reapplyTemplates.emit(source_index))
                self.menu_items.append(action_reapplyTemplates)
            
        self.setStyleSheet(self.parent.styleSheet())
        

            