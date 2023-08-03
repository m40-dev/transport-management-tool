from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import pyqtSignal

class ExecutionPlannerContextMenu(QMenu):
    """ Custom QMenu used to manage relation items """
    add_execution_group = pyqtSignal(object, str)
    edit_execution_group = pyqtSignal(object, str)
    edit_execution_task = pyqtSignal(object, str)

    def __init__(self, parent, source_item):
        super(ExecutionPlannerContextMenu, self).__init__(parent)
        self.parent = parent
        self.menu_items = []
        clickedItem = source_item.internalPointer()

        action_add_execution_group = self.addAction("Add Task Execution Group")
        action_add_execution_group.triggered.connect(lambda: self.add_execution_group.emit(source_item, "ExecutionPlanner_ExecutionGroup") )
        self.menu_items.append(action_add_execution_group)

        if clickedItem:
            if clickedItem.task_class == "ExecutionPlanner_ExecutionTask":
                action_edit_execution_task = self.addAction("Edit Execution Task")
                action_edit_execution_task.triggered.connect(lambda: self.edit_execution_task.emit(source_item, "ExecutionPlanner_ExecutionTask") )
                self.menu_items.append(action_edit_execution_task)

            if clickedItem.task_class == "ExecutionPlanner_ExecutionGroup":
                action_edit_execution_group = self.addAction("Edit Task Execution Group")
                action_edit_execution_group.triggered.connect(lambda: self.edit_execution_group.emit(source_item, "ExecutionPlanner_ExecutionGroup") )
                self.menu_items.append(action_edit_execution_group)
        else:
            self.menu_items.append(action_add_execution_group)

        

            