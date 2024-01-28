from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QRadioButton, QDialog, QComboBox, QHBoxLayout, QVBoxLayout, QSpacerItem
from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QHBoxLayout, QTextEdit, QGraphicsOpacityEffect, QSizePolicy, QTreeWidgetItem, QWidget
from PyQt6.QtCore import Qt, QRectF, QRect, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QPoint, QSize
from PyQt6.QtGui import QPalette, QPen, QPainterPath, QPainter, QTextOption, QTextCursor
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPalette, QPen, QPainterPath 
# from lib.ui.Theme import Application_Theme
from .ExecutionLogConsole import ExecutionLogConsole
from .ExecutionLogDialog import ExecutionLogDialog
from lib.ui.WidgetFactory.CustomViewDelegate import CustomViewDelegate, CustomDelegateWidget

class ExecutionPlannerDelegate(CustomViewDelegate):
    queueExecutionTask = pyqtSignal(object)
    queueExecutionGroup = pyqtSignal(object)

    def __init__(self, model_data, application, parent_view, parent_module):
        super().__init__(model_data=model_data, application=application, parent_view=parent_view, parent_module=parent_module)


    def createEditor(self, parent, option, index):
        # column_name = self.model_data.headerData(index.column())
        model_item = index.internalPointer()
        
        if index.column() == 0 and model_item.task_class in ["ExecutionPlanner_ExecutionTask"]:
            editor = ExecutionTaskWidget(
                model_item=model_item, 
                parent_view=self.parent_view, 
                application=self.application, 
                parent_module=self.parent_module)
            
            editor.taskExecutionRequested.connect(self.queueExecutionTask)
            return editor
        
        if index.column() == 0 and model_item.task_class in ["ExecutionPlanner_ExecutionGroup"]:
            editor = ExecutionGroupWidget(
                model_item=model_item, 
                parent_view=self.parent_view, 
                application=self.application, 
                parent_module=self.parent_module)
            
            editor.taskExecutionRequested.connect(self.queueExecutionGroup)
            return editor

        return super().createEditor(parent, option, index)

class ExecutionPlannerItem(CustomDelegateWidget):
    taskExecutionRequested = pyqtSignal(object)

    def __init__(self, parent_view, application, model_item, parent_module):
        super().__init__(parent_view=parent_view, application=application, model_item=model_item, parent_module=parent_module)

        self.setupUi()
    
    def setupUi(self):
        self.setProperty("ExecutionPlanner", "ExecutionPlannerWidget")
        self.frame.setProperty("ExecutionPlannerWidget", "ExecutionPlannerFrame")

        self.button1 = QToolButton(self)
        self.is_refresh = False

        self.button1.setText("Start")
        self.button1.setIconSize(QSize(25,25))

        self.element_label = QLabel(self)
        self.element_label.setProperty("CustomWidget", "ItemLabel")
        self.element_label.setWordWrap(True)

        self.element_description = QLabel(self)
        self.element_description.setProperty("CustomWidget", "ItemDescription")
        self.element_description.setWordWrap(True)

        object_configuration = self.application.getConfigurationParameters(self.model_item.task_class)
        # print(object_configuration)
        description_config = object_configuration.get("Description", None)
        if description_config:
            show_description = description_config.get("ShowInTreeView", True) == True
            if not show_description:
                self.element_description.setHidden(True)

        self.layout.addWidget(self.element_label, 0, 0, 1, 2)
        self.layout.addWidget(self.element_description, 1, 0, 1, 4)
        self.layout.addWidget(self.button1, 0, 4, 1, 1)
        
        self.model_item.data_changed.connect(self.refreshUI)
        self.refreshUI()
        self.animate()
        self.button1.clicked.connect(self.startTaskExecution)
    
    def startTaskExecution(self):
        self.taskExecutionRequested.emit(self.model_item)

    def refreshUI(self):
        self.element_label.setText(self.model_item.display)
        self.element_description.setText(self.model_item.description)
        if self.parent_view.model():
            self.parent_view.model().layoutChanged.emit()


class ExecutionGroupWidget(ExecutionPlannerItem):
    
    def __init__(self, model_item, parent_view, application, parent_module):
        super().__init__(parent_view=parent_view, application=application, model_item=model_item, parent_module=parent_module)
        
        self.frame.setProperty("ExecutionPlannerWidget", "ExecutionGroup")

        self.button1.setText("Start Group")
        start_icon = self.ProgramConfiguration.getIcon("ExecutionGroupAction")
        if start_icon:
            self.button1.setText("")
            self.button1.setToolTip("<i>Start Execution Group</i>")
            self.button1.setIcon(start_icon)

        self.button1.setProperty("ExecutionPlannerWidget", "ExecutionGroupAction")

        self.model_item.executionStateChanged.connect(self.handleExecutionStateChange)

    def handleExecutionStateChange(self, state):
        
        if state in ["Finished with Errors", "Terminated"]:
            state = "HasErrors"

        if state in ["Running", "Queued"]:
            state = "Running"

        self.frame.setProperty("GroupExecutionState", state)
        self.setStyleSheet(self.styleSheet())
    
    def sizeHint(self):
        minimum_size = super().minimumSizeHint()
        minimum_size.setHeight(round(minimum_size.height()*1.5))
        return minimum_size

class ExecutionTaskWidget(ExecutionPlannerItem):
    
    def __init__(self, model_item, parent_view, application, parent_module):
        super().__init__(parent_view=parent_view, application=application, model_item=model_item, parent_module=parent_module)

        self.frame.setProperty("ExecutionPlannerWidget", "ExecutionTask")

        self.button1.setText("Start Task")
        self.button1.setProperty("ExecutionPlannerWidget", "ExecutionTaskAction")
        start_icon = self.ProgramConfiguration.getIcon("ExecutionTaskAction")
        if start_icon:
            self.button1.setText("")
            self.button1.setToolTip("<i>Start Execution Task</i>")
            self.button1.setIcon(start_icon)
            self.button1.setIconSize(QSize(20,20))
        
        """ Add Custom Widgets """
        self.connection_box_label = QLabel("Use Connection:")
        self.connection_box_label.setProperty("Label", "PropertyName")

        self.task_execution_import = QRadioButton("Run Import Task")
        self.task_execution_import.setProperty("Label", "PropertyValue")

        self.task_execution_export = QRadioButton("Run Export Task")
        self.task_execution_export.setChecked(True)
        self.task_execution_export.setProperty("Label", "PropertyValue")

        self.connection_box = QComboBox(self)
        self.connection_box.setProperty("Label", "PropertyValue")

        self.refreshConnections()

        self.run_status = QLabel(self)
        self.run_status.setFixedWidth(90)
        self.run_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.run_status.setWordWrap(True)

        self.ExecutionLogs = QToolButton(self)
        self.ExecutionLogs.setText("Logs")
        self.ExecutionLogs.setProperty("ExecutionPlannerWidget", "ExecutionTaskAction")

        logs_icon = self.ProgramConfiguration.getIcon("ExecutionLogs")

        if logs_icon:
            self.ExecutionLogs.setText("")
            self.ExecutionLogs.setToolTip("<i>Show Execution Logs</i>")
            self.ExecutionLogs.setIcon(logs_icon)
            self.ExecutionLogs.setIconSize(QSize(20,20))
        
        self.dynamic_property_labels = {}
        dynamic_property_columns = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_setting(self.model_item.task_class, "ShowInTreeView")
        # lay out items in columns (labels and values)
        layout_columns = 6
        
        # task_details_layout.setColumnStretch(layout_columns, 2)
        task_details_layout = None
        if len(dynamic_property_columns) > 0:
            managed_roles = ["DisplayRole", "DescriptionRole"]
            task_details_layout = QGridLayout()
            row = task_details_layout.rowCount()
            column_count = 0
            for column, column_configuration in dynamic_property_columns.items():
                show_entry = column_configuration.get("ShowInTreeView", True) == True
                if not show_entry:
                    continue

                field_role = column_configuration.get("FieldRole", "")
                if field_role in managed_roles:
                    continue

                label = QLabel(f"{column}:")
                label.setProperty("Label", "PropertyName")
                value = QLabel()
                value.setProperty("Label", "PropertyValue")

                task_details_layout.addWidget(label, row, column_count)
                task_details_layout.addWidget(value, row, column_count+1)
                self.dynamic_property_labels[column] = value
                # add 2 added columns to the counter
                column_count += 2
                if column_count >= layout_columns:
                    row += 1
                    column_count = 0
        
        """ Add Widgets to the layouts """
        task_params_layout = QHBoxLayout()
        task_params_layout.addStretch(2)
        task_params_layout.addWidget(self.task_execution_import)
        task_params_layout.addWidget(self.task_execution_export)
        task_params_layout.addWidget(self.connection_box_label)
        task_params_layout.addWidget(self.connection_box)
        task_params_layout.addWidget(self.run_status)
        task_params_layout.addWidget(self.ExecutionLogs)
        task_params_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.layout.addLayout(task_params_layout, 0, 1, 1, 3)
        if task_details_layout:
            self.layout.addLayout(task_details_layout, 2, 0, 1, 3)

        """ Set initial values """
        self.configureTask()
        self.consoleDialog = ExecutionLogDialog(
            parent=self,
            application=self.application,
            model_item=self.model_item
        )
        """ Refresh state based on the model data """
        self.refreshTaskUI()

        """ Connect Signals """
        self.application.connectionDataChanged.connect(self.refreshConnections)
        self.task_execution_import.toggled.connect(self.setExecutionType)
        self.task_execution_export.toggled.connect(self.setExecutionType)
        self.connection_box.currentTextChanged.connect(self.setConnection)
        self.model_item.data_changed.connect(self.refreshTaskUI)
        self.ExecutionLogs.clicked.connect(self.consoleDialog.showLogs)

    def refreshConnections(self):
        connections = list(self.application.ConnectionHandler.connections.keys())
        self.connection_box.clear()
        self.connection_box.addItems(connections)

    def refreshTaskUI(self):
        for column, label_widget in self.dynamic_property_labels.items():
            label_widget.setText(str(self.model_item.data(column)))

        is_export = self.model_item.ExecutionType == "Export"
        if is_export:
            self.task_execution_export.setChecked(True)
        else:
            self.task_execution_import.setChecked(True)
        
        self.connection_box.setCurrentText(self.model_item.Connection)
        self.run_status.setText(self.model_item.ExecutionState)
        
        self.frame.setProperty("ExecutionState", str(self.model_item.ExecutionState))
        self.run_status.setProperty("ExecutionState", str(self.model_item.ExecutionState))
        self.setStyleSheet(self.styleSheet())
        self.consoleDialog.setStyleSheet(self.application.styleSheet())

    def setExecutionType(self):
        execution_type = "Export"
        # if self.task_execution_export.isChecked():
        #     execution_type = "Export"
        if self.task_execution_import.isChecked():
            execution_type = "Import"
        
        self.model_item.setData("ExecutionType", execution_type)

        for selected_index in self.parent_view.selectedIndexes():
            selected_item = selected_index.internalPointer()
            selected_item.setData("ExecutionType", execution_type)
        # print(self.parent_view.selectedIndexes())
        
    def setConnection(self):
        connection = self.connection_box.currentText()
        self.model_item.setData("Connection", connection)

        for selected_index in self.parent_view.selectedIndexes():
            selected_item = selected_index.internalPointer()
            selected_item.setData("Connection", connection)

    def configureTask(self):
        self.model_item.setData("ExecutionState", "Ready")
        self.setConnection()
        self.setExecutionType()
