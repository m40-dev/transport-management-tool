from PyQt6.QtWidgets import QWidget, QGridLayout, QTreeView, QAbstractItemView, QTextEdit, QSplitter, QLineEdit, QLabel, QToolButton
from PyQt6.QtCore import Qt, pyqtSignal, QProcess

from .ContextMenu import ExecutionPlannerContextMenu
from lib.data.DataModels import TaskExecutionModel
from .ExecutionPlannerDelegate import ExecutionPlannerDelegate
from .ExecutionPlannerProcessRunner import ProcessRunner
from lib.ui.WidgetFactory import FormEditorDialog

class ExecutionPlannerWidget(QWidget):
    plannerNameChanged = pyqtSignal(object)

    def __init__(self, application):
        super(ExecutionPlannerWidget, self).__init__()

        self.parent = application
        self.application = application
        self.object_configuration = self.application.object_configuration
        self.ProcessRunner = ProcessRunner(self)
        self.ProcessRunner.message.connect(self.logExecutionPlannerMessage)
        self.ProcessRunner.stateChanged.connect(self.processRunnerStateChanged)

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setProperty("TabWidget", "ExecutionPlanner")

        splitter = QSplitter(Qt.Orientation.Vertical)
        planner_label = QLabel("Planner Name")
        self.executionPlannerNameInput = QLineEdit("New Execution Plan...")

        self.stop_execution = QToolButton()
        self.stop_execution.setText("Stop Execution")
        self.stop_execution.setEnabled(False)
        self.stop_execution.clicked.connect(self.ProcessRunner.stopExecutionPlanner)

        self.treeview = QTreeView()
        self.console = QTextEdit()

        splitter.addWidget(self.treeview)
        splitter.addWidget(self.console)
        splitter.setSizes([100, 30])

        self.layout.addWidget(planner_label, 0, 0, 1, 1)
        self.layout.addWidget(self.executionPlannerNameInput, 0, 1, 1, 1)
        self.layout.addWidget(self.stop_execution, 0, 2, 1, 1)
        
        self.layout.addWidget(splitter, 1, 0, 1, 3)
        self.executionPlannerNameInput.textChanged.connect(lambda: self.plannerNameChanged.emit(self))

        self.console.hide()

        data = [
            {
                "GroupName": "Group 1",
                "objectclass": "ExecutionPlanner_ExecutionGroup",
                "Description": "Default Execution Planner tasks group.",
                "ExecutionTasks": [   
                ]
            }
        ]

        self.model_data = TaskExecutionModel(data=data, application=self.application)
        self.treeview.setModel(self.model_data)

        itemDelegate = ExecutionPlannerDelegate(
            model_data=self.model_data, 
            parent=self.treeview, 
            application=self.application, 
            planner_widget=self
            )
        
        itemDelegate.queueExecutionTask.connect(self.queueExecutionTask)
        itemDelegate.queueExecutionGroup.connect(self.queueExecutionGroup)

        self.treeview.setItemDelegate(itemDelegate)
        self.treeview.setHeaderHidden(True)

        self.treeview.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.treeview.setDragEnabled(True)
        self.treeview.setAcceptDrops(True)
        self.treeview.setDropIndicatorShown(True)
        self.treeview.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.treeview.dragMoveEvent = self.dragMoveEvent
        
        self.treeview.setAlternatingRowColors(True)
        self.treeview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.treeview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeview.customContextMenuRequested.connect(self.contextMenuRequested)

    def processRunnerStateChanged(self, running_state):
        is_running = True

        if running_state == QProcess.ProcessState.NotRunning:
            is_running = False

        self.stop_execution.setEnabled(is_running)

    @property
    def name(self):
        return self.executionPlannerNameInput.text()

    def contextMenuRequested(self, menuPosition):
        clickedIndex = self.treeview.indexAt(menuPosition)
        contextMenu = ExecutionPlannerContextMenu(self, clickedIndex)
        menu_target = self.treeview.mapToGlobal(menuPosition)

        """ Connect Signals """
        contextMenu.add_execution_group.connect(self.addPlannerEntry)
        contextMenu.edit_execution_group.connect(self.editPlannerEntry)
        contextMenu.edit_execution_task.connect(self.editPlannerEntry)

        if len(contextMenu.menu_items) > 0:
            contextMenu.popup(menu_target)

    def addPlannerEntry(self, source_index, object_class):
        print("Add Package Definition", source_index)
        editor_configuration = self.object_configuration.get("ExecutionPlanner_ExecutionGroup")
        if editor_configuration:
            dialog = FormEditorDialog(self.application, 
            configuration_class="ExecutionPlanner_ExecutionGroup", 
            dialog_name="Execution Group Definition"
            )
            if dialog.exec():
                data = dialog.form_data
                treeview_model = self.treeview.model()
                treeview_model.insert_item("ExecutionPlanner_ExecutionGroup", data, source_index)
        
    def editPlannerEntry(self, source_index, object_class):
        print("Edit Execution Planner Definition", source_index)
        if not source_index.isValid():
            return False
            
        editor_configuration = self.object_configuration.get(object_class)
        if editor_configuration:
            dialog = FormEditorDialog(self.application, 
            configuration_class=object_class,
            dialog_name="Execution Planner Object Definition"
            )
            dialog.set_form_data(source_index)
            if dialog.exec():
                data = dialog.form_data
                source_item = source_index.internalPointer()
                source_item.update_data(data)

    def queueExecutionTask(self, task_item):
        self.ProcessRunner.startProcessTask(task_item)
        self.console.show()
        
    def queueExecutionGroup(self, task_item):
        self.console.show()
        for child_task in task_item._children:
            print("Start task", child_task.task_class)
            if child_task.task_class in ["ExecutionPlanner_ExecutionTask", "PackageManager_TaskDefinition"]:
                self.ProcessRunner.startProcessTask(child_task)

            if child_task.childCount() > 0:
                self.queueExecutionGroup(child_task)

    def logExecutionPlannerMessage(self, message, severity=None):
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

        if drop_item:
            self.treeview.setDropIndicatorShown(True)

        if dropIndicator == QAbstractItemView.DropIndicatorPosition.OnItem:

            if drop_item._task_class != source_item._task_class:
                move_accept = True
            
            if drop_item and source_item:
                #allow group nesting
                if source_item._task_class == "ExecutionPlanner_ExecutionGroup" and drop_item._task_class == "ExecutionPlanner_ExecutionGroup":
                    move_accept = True

        if dropIndicator in [QAbstractItemView.DropIndicatorPosition.BelowItem, QAbstractItemView.DropIndicatorPosition.AboveItem]:
            if drop_item._task_class == source_item._task_class:
                move_accept = True

            if drop_item._task_class == "ExecutionPlanner_ExecutionTask" and source_item._task_class == "PackageManager_TaskDefinition":
                move_accept = True
            
            if source_item._task_class == "PackageManager_PackageDefinition":
                move_accept = True


        if drop_item is None:
            # no target item - drop at top level
            if source_item._task_class in ["ExecutionPlanner_ExecutionGroup", "PackageManager_PackageDefinition"]:
                move_accept = True

        if (event.mimeData().hasFormat("application/vnd.jsondataitem") or event.mimeData().hasFormat("application/vnd.ExecutionPlannerItem")) and move_accept:
            event.acceptProposedAction()
        else:
            event.ignore()

    def deleteSelectedItems(self):
        if self.treeview.hasFocus():
            for item_index in self.treeview.selectedIndexes():
                item = item_index.internalPointer()
                item_index.model().remove_item(item)
