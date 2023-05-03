from PyQt6.QtWidgets import QWidget, QGridLayout, QTreeView, QAbstractItemView, QTextEdit, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal
from lib.data.DataModels import TaskExecutionModel
from .ExecutionPlannerDelegate import ExecutionPlannerDelegate
from .ExecutionPlannerProcessRunner import ProcessRunner
class ExecutionPlannerWidget(QWidget):
    

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

        splitter = QSplitter(Qt.Orientation.Vertical)

        self.treeview = QTreeView()
        self.console = QTextEdit()

        splitter.addWidget(self.treeview)
        splitter.addWidget(self.console)
        splitter.setSizes([100, 30])

        self.layout.addWidget(splitter, 0, 0, 1, 1)

        self.console.hide()


        data = [
            {
                "Name": "Group 1",
                "objectclass": "TaskGroup",
                "Description": "This Group have a description which might help organize things around.",
                "Tasks": [
                        
                ]
            },
            {
                "Name": "Group 2",
                "objectclass": "TaskGroup",
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
        
        # self.treeview.setUniformRowHeights(True)
        self.treeview.setAlternatingRowColors(True)
        # self.treeview.setProperty("QTreeView::itemSpacing", 10)
        # self.treeview.setSortingEnabled(True)
        self.treeview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        view_header = self.treeview.header()
        view_header.setStretchLastSection(True)

        # section_width = round(self.treeview.viewport().width() / view_header.count()) * 1.5
        # for i in range(0, view_header.count()):
        #     self.treeview.setColumnWidth(i, section_width)

    def run_planner_task(self, task_item):
        print("start tasks", task_item)
        self.ProcessRunner.start_process(task_item)
        self.console.show()
        
    def run_planner_tasks_group(self, task_item):
        self.console.show()
        for child_task in task_item._children:
            if child_task.task_class == "TaskItem":
                self.ProcessRunner.start_process(child_task)
        

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


