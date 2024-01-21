from PyQt6.QtWidgets import QWidget, QGridLayout, QTreeView, QAbstractItemView, QTextEdit, QSplitter, QLineEdit, QLabel, QToolButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QProcess, QSize
from PyQt6.QtGui import QTextCursor, QTextDocumentFragment, QTextOption
from .ContextMenu import ExecutionPlannerContextMenu
from lib.data.DataModels import TaskExecutionModel
from .ExecutionPlannerDelegate import ExecutionPlannerDelegate
from .ExecutionPlannerProcessRunner import ProcessRunner
from lib.ui.WidgetFactory import FormEditorDialog, MsgBox
from datetime import datetime
from .ExecutionLogConsole import ExecutionLogConsole

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class ExecutionPlannerWidget(QWidget):
    plannerNameChanged = pyqtSignal(object)

    def __init__(self, parent, application):
        super(ExecutionPlannerWidget, self).__init__()

        self.parent = parent
        self.application = application

        self.console = ExecutionLogConsole(self, self.application)

        self.ProcessRunner = ProcessRunner(self)
        self.ProcessRunner.logPreformattedMessage.connect(self.console.appendLogs)
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

        StopExecutionQueueIcon = self.application.ProgramConfiguration.getIcon("StopExecutionQueue")
        
        if StopExecutionQueueIcon:
            self.stop_execution.setText("")
            self.stop_execution.setToolTip("<b>Stop Execution Queue!</b>")
            self.stop_execution.setIcon(StopExecutionQueueIcon)
            self.stop_execution.setIconSize(QSize(23,23))
            self.stop_execution.setProperty("ExecutionPlannerWidget", "StopExecutionQueue")

        self.stop_execution.setEnabled(False)
        self.stop_execution.clicked.connect(self.ProcessRunner.stopExecutionPlanner)

        self.treeview = QTreeView()
        self.treeview.setObjectName("ExecutionPlannerTreeView")
        self.treeview.setProperty("TreeView", "ExecutionPlanner")
        

        # self.console = QTextEdit()
        # self.console.setProperty("ExecutionPlanner", "ConsoleReader")
        # self.console.setAcceptRichText(True)
        # self.console.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        # self.console.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        # self.console.setLineWrapColumnOrWidth(self.console.width())

        # self.defaultBlockFormat = self.console.textCursor().blockFormat()
        # self.defaultBlockFormat.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # self.defaultBlockFormat.setTopMargin(0)
        # self.defaultBlockFormat.setBottomMargin(0)
        # self.defaultBlockFormat.setLeftMargin(0)
        # self.defaultBlockFormat.setRightMargin(0)
        # self.console.textCursor().setBlockFormat(self.defaultBlockFormat)

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
            parent_view=self.treeview, 
            application=self.application, 
            parent_module=self
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
        
        self.treeview.setAlternatingRowColors(False)
        self.treeview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.treeview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeview.customContextMenuRequested.connect(self.contextMenuRequested)
        self.refresh_ui()

    def refresh_ui(self):
        # self.console.document().setDefaultStyleSheet(self.application.ProgramConfiguration.styleSheet())
        self.console.refresh_ui()

    def processRunnerStateChanged(self, running_state):
        is_running = True

        if running_state == QProcess.ProcessState.NotRunning:
            is_running = False

        self.stop_execution.setEnabled(is_running)

    @property
    def current_workdir(self):
        return self.parent.current_workdir

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
        # print("Add Package Definition", source_index)
        editor_configuration = self.application.getConfigurationParameters("ExecutionPlanner_ExecutionGroup")
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
        # print("Edit Execution Planner Definition", source_index)
        if not source_index.isValid():
            return False
            
        editor_configuration = self.application.getConfigurationParameters(object_class)
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
        self.console.show()

        self.ProcessRunner.queuePlannerTasks([task_item])
        self.ProcessRunner.continueExecutionQueue()
        
    def queueExecutionGroup(self, task_item, prompt=True):
        if len(task_item._children) > 0 and prompt:
            # continue_execution = QMessageBox.question(self, "Are You Sure?", "Are you sure to start the goup execution?\nAll Child elements and tasks in child groups will be queued for execution.")
            # if continue_execution in [QMessageBox.StandardButton.No, QMessageBox.StandardButton.Cancel]:
            #     return False
            msg_dialog = MsgBox(
                application=self.application,
                window_title="Question",
                message="Are you sure to start the goup execution?\nAll Child elements and tasks in child groups will be queued for execution.",
                window_mode=MsgBox.QUESTION
            )
            msg_dialog.exec()
            if not msg_dialog.accepted:
                return False
        
        for child_task in task_item._children:
            if child_task.childCount() > 0:
                self.queueExecutionGroup(child_task, prompt=False)

            self.ProcessRunner.queuePlannerTasks([child_task])

        self.console.show()
        self.ProcessRunner.continueExecutionQueue()

    def logExecutionPlannerMessage(self, formatted_message):
        if len(formatted_message.strip()) == 0:
            return False

        cursor = self.console.textCursor()

        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)

        if cursor.blockNumber() > 0:
            cursor.insertBlock(self.defaultBlockFormat)

        cursor.insertHtml(formatted_message)

        # restore cursor location at the end, this effectively scrolls the log view automatically
        self.console.setTextCursor(cursor)

    def changeData(self, col, row):
        # print("data changed in ", col, row)
        pass

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
