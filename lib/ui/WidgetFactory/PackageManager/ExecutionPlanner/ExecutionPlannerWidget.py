from PyQt6.QtWidgets import QWidget, QGridLayout, QTreeView, QAbstractItemView, QTextEdit, QSplitter, QLineEdit, QLabel, QToolButton
from PyQt6.QtCore import Qt, pyqtSignal, QProcess
from PyQt6.QtGui import QTextCursor
from .ContextMenu import ExecutionPlannerContextMenu
from lib.data.DataModels import TaskExecutionModel
from .ExecutionPlannerDelegate import ExecutionPlannerDelegate
from .ExecutionPlannerProcessRunner import ProcessRunner
from lib.ui.WidgetFactory import FormEditorDialog
from datetime import datetime

LOG_STD = "#333"
LOG_ERROR = "#b30000"
LOG_SUCCESS = "#006600"
LOG_TRANSPORT_MANAGER = "#232"
FONT_SIZE = "13px"
LOG_START = "#ff6600"

class ExecutionPlannerWidget(QWidget):
    plannerNameChanged = pyqtSignal(object)

    def __init__(self, parent, application):
        super(ExecutionPlannerWidget, self).__init__()

        self.parent = parent
        self.application = application
        self.object_configuration = self.application.object_configuration
        self.ProcessRunner = ProcessRunner(self)
        self.ProcessRunner.message.connect(self.logExecutionPlannerMessage)
        # self.ProcessRunner.stageFinished.connect(self.appendLogSeparator)
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
        self.console.setAcceptRichText(True)

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

    def logExecutionPlannerMessage(self, message, message_format=None):
        if len(message.strip()) == 0:
            return False

        cursor = self.console.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
        cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
        
        if cursor.columnNumber() > 0 and bytes(cursor.selectedText(), 'utf-8') == b'\xe2\x80\xa8':
            cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
            # cursor.insertHtml("<br>")

        message = message.strip()
        format_color = LOG_STD

        if message_format:
            if message_format.upper() == "ERROR":
                log_info = f'<p align=left style="color: {LOG_ERROR};font-size:{FONT_SIZE};">'
                log_info += f'<b>[Error] {message} </b></p><br>'

                cursor.insertHtml(log_info)
                self.console.setTextCursor(cursor)
                return True

            if message_format.upper() == "TRANSPORT MANAGER":
                log_info = f'<p align=left style="color: {LOG_TRANSPORT_MANAGER};font-size:{FONT_SIZE};">'
                log_info += f'<b>[Transport Manager]</b> {message} </p><br>'

                cursor.insertHtml(log_info)
                self.console.setTextCursor(cursor)
                return True
            
            if message_format.upper() == "INIT":
                format_color = LOG_SUCCESS

                execution_info = f'<p align=left style="color: {LOG_START};font-size:{FONT_SIZE};">'
                execution_info += f'<b>Start time: [{datetime.now()}]<br>'
                execution_info += f'Starting task execution [{self.ProcessRunner.current_item.display}].</b></p>'
                execution_info += f'<p align=left style="color: {LOG_STD};font-size:{FONT_SIZE};"><b>Action:</b> [{self.ProcessRunner.operation}]<br>'
                execution_info += f'<b>Connection:</b> [{self.ProcessRunner.connection_name}]</p><br>'
                
                cursor.insertHtml(execution_info)
                self.console.setTextCursor(cursor)
                return True
            
            if message_format.upper() == "FINISHED":
                end_state = "Successfully"
                format_color = LOG_SUCCESS
                if self.ProcessRunner.was_error:
                    format_color = LOG_ERROR
                    end_state = "with Error"

                execution_summary = f'<p align=left style="color: {format_color};font-size:{FONT_SIZE};">'
                execution_summary += f'<br><b>Task Execution Finished {end_state}!<br>'
                execution_summary += f'<b>Executed Task:</b> [{self.ProcessRunner.current_item.display}]<br>'
                execution_summary += f'<b>Task Execution time:</b> ({self.ProcessRunner.execution_time})'
                execution_summary += f'</p><hr><br>'

                cursor.insertHtml(execution_summary)
                self.console.setTextCursor(cursor)
                return True

        cursor.insertHtml(f'<p align=left style="color: {LOG_STD};font-size:{FONT_SIZE};">{message}</p><br>')
        self.console.setTextCursor(cursor)
    
    def appendLogSeparator(self, exitCode):
        print("process finished")
        cursor = self.console.textCursor()

        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
        task_display_name = self.ProcessRunner.current_item.display

        format_color = LOG_SUCCESS
        end_state = "Successfully"

        if exitCode != 0:
            format_color = LOG_ERROR
            end_state = "with Error"

        cursor.insertHtml(f'<div style="color: {format_color};font: bold;font-size:{FONT_SIZE};"> [Transport Manager] - Task Execution Finished {end_state} - [ {task_display_name} ] <hr> </div><br>')

        self.console.setTextCursor(cursor)
    
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
