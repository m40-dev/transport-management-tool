from PyQt6.QtWidgets import QWidget, QGridLayout, QTreeView, QAbstractItemView, QTextEdit, QSplitter, QLineEdit, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QShortcut, QKeySequence
from lib.ui.WidgetFactory import ExecutionPlannerContextMenu
from lib.data.DataModels import TaskExecutionModel
from .ExecutionPlannerDelegate import ExecutionPlannerDelegate
from .ExecutionPlannerProcessRunner import ProcessRunner
from lib.ui.WidgetFactory import ExecutionPlannerGroupDialog

class ExecutionPlannerWidget(QWidget):
    planner_name_changed = pyqtSignal(object)

    def __init__(self, parent):
        super(ExecutionPlannerWidget, self).__init__()

        self.parent = parent
        self.application = parent
        self.ProcessRunner = ProcessRunner(self)
        self.ProcessRunner.message.connect(self.log_message)

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setProperty("TabWidget", "ExecutionPlanner")

        splitter = QSplitter(Qt.Orientation.Vertical)
        planner_label = QLabel("Planner Name")
        self.planner_name = QLineEdit("New Execution Plan...")
        self.treeview = QTreeView()
        self.console = QTextEdit()

        splitter.addWidget(self.treeview)
        splitter.addWidget(self.console)
        splitter.setSizes([100, 30])

        self.layout.addWidget(planner_label, 0, 0, 1, 1)
        self.layout.addWidget(self.planner_name, 0, 1, 1, 1)
        self.layout.addWidget(splitter, 1, 0, 1, 2)
        self.planner_name.textChanged.connect(lambda: self.planner_name_changed.emit(self))

        self.console.hide()

        data = [
            {
                "Name": "Group 1",
                "objectclass": "TaskGroup",
                "Description": "Default Execution Planner tasks group.",
                "Tasks": [   
                ]
            }
        ]

        self.model_data = TaskExecutionModel(data)
        self.treeview.setModel(self.model_data)

        custom_item_delegate = ExecutionPlannerDelegate(
            model_data=self.model_data, 
            parent=self.treeview, 
            application=self.application, 
            planner_widget=self
            )
        
        custom_item_delegate.start_single_task_execution.connect(self.run_planner_task)
        custom_item_delegate.start_group_task_execution.connect(self.run_planner_tasks_group)

        self.treeview.setItemDelegate(custom_item_delegate)

        self.treeview.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.treeview.setDragEnabled(True)
        self.treeview.setAcceptDrops(True)
        self.treeview.setDropIndicatorShown(True)
        self.treeview.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.treeview.dragMoveEvent = self.dragMoveEvent
        
        self.treeview.setAlternatingRowColors(True)
        self.treeview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.treeview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeview.customContextMenuRequested.connect(self.open_context_menu)

    @property
    def name(self):
        return self.planner_name.text()

    def open_context_menu(self, menuPosition):
        clickedIndex = self.treeview.indexAt(menuPosition)
        contextMenu = ExecutionPlannerContextMenu(self, clickedIndex)
        menu_target = self.treeview.mapToGlobal(menuPosition)

        """ Connect Signals """
        contextMenu.add_execution_group.connect(self.add_execution_group)
        contextMenu.edit_execution_group.connect(self.edit_execution_group)

        if len(contextMenu.menu_items) > 0:
            contextMenu.popup(menu_target)

    def add_execution_group(self, parent):
        
        new_group = {
                "Name": "Group Name",
                "objectclass": "TaskGroup",
                "Description": "New Execution Group Description.",
                "Tasks": [
                ]
            }
        dialog = ExecutionPlannerGroupDialog(self.application, form_data=new_group)
        dialog.setupForm()
        if dialog.exec():
            group_details = dialog.form_data
            self.model_data.addExecutionGroup(task_data=group_details, parentIndex=parent)
        
    def edit_execution_group(self, index):
        item = index.internalPointer()
        form_data = item.task_data
        dialog = ExecutionPlannerGroupDialog(self.application, form_data=form_data)
        dialog.setupForm()
        if dialog.exec():
            group_details = dialog.form_data
            item._task_data = group_details
            item.data_changed.emit(item)
            print(item.task_data)


    def run_planner_task(self, task_item):
        print("start tasks", task_item)
        self.ProcessRunner.start_process(task_item)
        self.console.show()
        
    def run_planner_tasks_group(self, task_item):
        self.console.show()
        for child_task in task_item._children:

            if child_task.task_class == "TaskItem":
                self.ProcessRunner.start_process(child_task)

            if child_task.childCount() > 0:
                self.run_planner_tasks_group(child_task)
        

    def log_message(self, message, severity=None):
        if len(message.strip()) == 0:
            return False
        if severity:
            self.console.append(f"[{severity}]:{message.strip()}")
        else:
            self.console.append(message.strip())
    
    def changeData(self, col, row):
        print("data changed in ", col, row)

    def dragMoveEvent(self, event):
        move_accept = False
        source_index = event.source().currentIndex()
        source_item = source_index.internalPointer()

        QTreeView.dragMoveEvent(self.treeview, event)
        
        drop_index = self.treeview.indexAt(event.position().toPoint())
        drop_item = drop_index.internalPointer()

        dropIndicator = self.treeview.dropIndicatorPosition()

        # print("Drop Event:", drop_index, drop_item, source_index, source_item)

        if drop_item:
            self.treeview.setDropIndicatorShown(True)

        if dropIndicator == QAbstractItemView.DropIndicatorPosition.OnItem:

            if drop_item._task_class != source_item._task_class:
                move_accept = True
            
            if drop_item and source_item:
                #allow group nesting
                if source_item._task_class == "TaskGroup" and drop_item._task_class == "TaskGroup":
                    move_accept = True

        if dropIndicator in [QAbstractItemView.DropIndicatorPosition.BelowItem, QAbstractItemView.DropIndicatorPosition.AboveItem]:
            if drop_item._task_class == source_item._task_class:
                move_accept = True

        if drop_item is None:
            # no target item - drop at top level
            if source_item._task_class == "TaskGroup":
                move_accept = True

        if event.mimeData().hasFormat("application/vnd.jsondataitem") and move_accept:
            event.acceptProposedAction()
        else:
            event.ignore()

    def remove_selected_items(self):
        for item_index in self.treeview.selectedIndexes():
            item = item_index.internalPointer()
            item_index.model().remove_item(item)
