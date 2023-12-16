from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QRadioButton, QComboBox, QHBoxLayout, QVBoxLayout, QSpacerItem
from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy, QTreeWidgetItem, QWidget
from PyQt6.QtCore import Qt, QRectF, QRect, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QPoint, QSize
from PyQt6.QtGui import QPalette, QPen, QPainterPath, QPainter
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPalette, QPen, QPainterPath 
# from lib.ui.Theme import Application_Theme
from lib.ui.WidgetFactory.PackageManager.PackageViewDelegate import PackageDefinitionWidget

class ExecutionPlannerDelegate(QStyledItemDelegate):
    queueExecutionTask = pyqtSignal(object)
    queueExecutionGroup = pyqtSignal(object)

    def __init__(self, model_data, application, planner_widget, parent=None):
        super().__init__(parent)
        self.application = application
        self.ProgramConfiguration = application.ProgramConfiguration
        self.planner_widget = planner_widget
        self.model_data = model_data

    def createEditor(self, parent, option, index):
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if column_name == "Actions" and item.task_class in [
            "ExecutionPlanner_ExecutionTask", 
            "PackageManager_TaskDefinition"]:
            editor = ItemActionWidget(
                data_item=item, 
                tree_view=self.parent(), 
                application=self.application, 
                planner_widget=self.planner_widget)
            
            editor.taskExecutionRequested.connect(self.queueExecutionTask)
            return editor
        
        if column_name == "Actions" and item.task_class in [
            "ExecutionPlanner_ExecutionGroup", 
            "PackageManager_PackageDefinition"]:
            editor = GroupActionWidget(
                data_item=item, 
                tree_view=self.parent(), 
                application=self.application, 
                planner_widget=self.planner_widget)
            
            editor.taskExecutionRequested.connect(self.queueExecutionGroup)
            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if column_name == "Actions" and item.task_class in [
            "ExecutionPlanner_ExecutionGroup", 
            "ExecutionPlanner_ExecutionTask", 
            "PackageManager_PackageDefinition",
            "PackageManager_TaskDefinition"
            ]:
            viewport = self.parent().viewport()
            editor.setParent(viewport)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        super().setModelData(editor, model, index)

    def paint(self, painter, option, index):
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()

        if column_name == "Actions" and item.task_class in [
            "ExecutionPlanner_ExecutionTask", 
            "ExecutionPlanner_ExecutionGroup", 
            "PackageManager_PackageDefinition",
            "PackageManager_TaskDefinition"]:
            widget = self.parent().indexWidget(index)
            if not widget:
                widget = self.createEditor(self.parent(), option, index)
                self.setEditorData(widget, index)
                self.parent().setIndexWidget(index, widget)
                widget.setGeometry(option.rect)
            else:
                widget.setGeometry(option.rect)

            # Check if the item is selected
            if option.state & QStyle.StateFlag.State_Selected:  
                widget.isSelected = True

                target_x = option.rect.x() + ((widget.rect().width() - widget.frame.rect().width()) / 2)

                # divide by 2 to get just widget size (difference includes both margins)
                target_y = option.rect.y() + ((widget.rect().height() - widget.frame.rect().height()) / 2)
                # print(target_x, target_y)
                # target_rect = QRect(QPoint(target_x, target_y), widget.frame.size())
                target_rect = QRect(QPoint(target_x, target_y), widget.frame.size())

                selection_color = self.application.ProgramConfiguration.getColor("SelectedObjectColor")
                # selection_color.setAlphaF(0.4)
                # # # Set the pen color to the selection color
                pen = QPen(selection_color)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.setBrush(selection_color)
                painter.drawRect(target_rect)
            else:
                widget.isSelected = False

        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        if index.isValid():
            widget = self.parent().indexWidget(index)
            if widget and isinstance(widget, QWidget):
                return widget.sizeHint()
        return QSize(30, 30)

class ExecutionPlannerItem(QFrame):
    taskExecutionRequested = pyqtSignal(object)

    def __init__(self, data_item, tree_view, application, planner_widget, parent=None):
        super().__init__(parent=parent)
        self.tree_view = tree_view
        self.application = application
        self.ProgramConfiguration = application.ProgramConfiguration
        self.planner_widget = planner_widget
        self.data_item = data_item
        self.button1 = QToolButton(self)
        self.is_refresh = False
        self.isSelected = False

        self.button1.setText("Start")
        self.button1.setIconSize(QSize(20,20))

        # self.layout = QGridLayout(self)
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(1,1,1,1)
        self.main_layout.setSpacing(1)
        self.isSelected = False

        self.frame = QFrame()
        self.setProperty("ExecutionPlanner", "ExecutionPlannerWidget")
        self.frame.setProperty("ExecutionPlannerWidget", "ExecutionPlannerFrame")

        self.main_layout.addWidget(self.frame, 0, 0)

        self.layout = QGridLayout(self.frame)

        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(1)

        self.element_label = QLabel(self)
        self.element_label.setProperty("CustomWidget", "ItemLabel")
        self.element_label.setWordWrap(True)

        self.element_description = QLabel(self)
        self.element_description.setProperty("CustomWidget", "ItemDescription")
        self.element_description.setWordWrap(True)

        object_configuration = self.application.getConfigurationParameters(self.data_item.task_class)
        # print(object_configuration)
        description_config = object_configuration.get("Description", None)
        if description_config:
            show_description = description_config.get("ShowInTreeView", True) == True
            if not show_description:
                self.element_description.setHidden(True)

        self.layout.addWidget(self.element_label, 0, 0, 1, 2)
        self.layout.addWidget(self.element_description, 1, 0, 1, 4)
        self.layout.addWidget(self.button1, 0, 4, 1, 1)
        self.data_item.data_changed.connect(self.refreshUI)
        self.refreshUI()
        self.animate()
        self.button1.clicked.connect(self.startTaskExecution)
    
    def startTaskExecution(self):
        self.taskExecutionRequested.emit(self.data_item)

    def refreshUI(self):
        self.element_label.setText(self.data_item.display)
        self.element_description.setText(self.data_item.description)
        if self.tree_view.model():
            self.tree_view.model().layoutChanged.emit()

    def animate(self, reverse=False):
        # animate startup
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        animation = QPropertyAnimation(self)
        animation.setPropertyName(bytes("opacity", "utf-8"))
        animation.setTargetObject(effect)
        animation.setDuration(200)
        animation.setStartValue(0)
        animation.setEndValue(1)
        if reverse:
            animation.setStartValue(1)
            animation.setEndValue(0)
            animation.setDuration(200)
        
        animation.setEasingCurve(QEasingCurve.Type.OutInCubic)
        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

class GroupActionWidget(ExecutionPlannerItem):
    
    def __init__(self, data_item, tree_view, application, planner_widget, parent=None):
        super().__init__(data_item=data_item, tree_view=tree_view, application=application, planner_widget=planner_widget, parent=parent)
        self.frame.setProperty("ExecutionPlannerWidget", "ExecutionGroup")

        self.button1.setText("Start Group")
        start_icon = self.application.ProgramConfiguration.getIcon("ExecutionGroupAction")
        if start_icon:
            self.button1.setText("")
            self.button1.setToolTip("<i>Start Execution Group</i>")
            self.button1.setIcon(start_icon)

        self.button1.setProperty("ExecutionPlannerWidget", "ExecutionGroupAction")

        self.data_item.executionStateChanged.connect(self.handleExecutionStateChange)

    def handleExecutionStateChange(self, state):
        
        if state in ["Finished with Errors", "Terminated"]:
            state = "HasErrors"

        if state in ["Running", "Queued"]:
            state = "Running"

        self.frame.setProperty("GroupExecutionState", state)
        self.setStyleSheet(self.styleSheet())
    
    def sizeHint(self):
        minimum_size = super().minimumSizeHint()
        minimum_size.setHeight(minimum_size.height()*1.5)
        return minimum_size

class ItemActionWidget(ExecutionPlannerItem):
    
    def __init__(self, data_item, tree_view, application, planner_widget, parent=None):
        super().__init__(data_item=data_item, tree_view=tree_view, application=application, planner_widget=planner_widget, parent=parent)

        self.treeview = self.parent()
        self.frame.setProperty("ExecutionPlannerWidget", "ExecutionTask")

        self.button1.setText("Start Task")
        self.button1.setProperty("ExecutionPlannerWidget", "ExecutionTaskAction")
        start_icon = self.application.ProgramConfiguration.getIcon("ExecutionTaskAction")
        if start_icon:
            self.button1.setText("")
            self.button1.setToolTip("<i>Start Execution Task</i>")
            self.button1.setIcon(start_icon)
        
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
        self.application.connectionDataChanged.connect(self.refreshConnections)

        self.run_status = QLabel(self)
        self.run_status.setFixedWidth(100)
        self.run_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.run_status.setWordWrap(True)
        
        self.dynamic_property_labels = {}
        dynamic_property_columns = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_setting(self.data_item.task_class, "ShowInTreeView")
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
        task_params_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.layout.addLayout(task_params_layout, 0, 1, 1, 3)
        if task_details_layout:
            self.layout.addLayout(task_details_layout, 2, 0, 1, 3)
        # self.layout.addWidget(self.run_status, 1, 3, 1, 2)

        # self.layout.setColumnStretch(3, 1)

        """ Set initial values """
        self.configureTask()

        """ Refresh state based on the model data """
        self.refreshTaskUI()

        """ Connect Signals """
        self.task_execution_import.toggled.connect(self.setExecutionType)
        self.task_execution_export.toggled.connect(self.setExecutionType)
        self.connection_box.currentTextChanged.connect(self.setConnection)
        self.data_item.data_changed.connect(self.refreshTaskUI)
        # self.data_item.executionStateChanged.connect(self.handleExecutionStateChange)


    def refreshConnections(self):
        connections = list(self.application.ConnectionHandler.connections.keys())
        self.connection_box.clear()
        self.connection_box.addItems(connections)

    def refreshTaskUI(self):
        for column, label_widget in self.dynamic_property_labels.items():
            label_widget.setText(str(self.data_item.data(column)))

        is_export = self.data_item.ExecutionType == "Export"
        if is_export:
            self.task_execution_export.setChecked(True)
        else:
            self.task_execution_import.setChecked(True)
        
        self.connection_box.setCurrentText(self.data_item.Connection)
        self.run_status.setText(self.data_item.ExecutionState)
        
        self.frame.setProperty("ExecutionState", str(self.data_item.ExecutionState))
        self.run_status.setProperty("ExecutionState", str(self.data_item.ExecutionState))
        self.setStyleSheet(self.styleSheet())

    def setExecutionType(self):
        execution_type = "Export"
        # if self.task_execution_export.isChecked():
        #     execution_type = "Export"
        if self.task_execution_import.isChecked():
            execution_type = "Import"
        
        self.data_item.setData("ExecutionType", execution_type)

        for selected_index in self.tree_view.selectedIndexes():
            selected_item = selected_index.internalPointer()
            selected_item.setData("ExecutionType", execution_type)
        # print(self.treeview.selectedIndexes())
        
    def setConnection(self):
        connection = self.connection_box.currentText()
        self.data_item.setData("Connection", connection)

        for selected_index in self.tree_view.selectedIndexes():
            selected_item = selected_index.internalPointer()
            selected_item.setData("Connection", connection)

    def configureTask(self):
        self.data_item.setData("ExecutionState", "Ready")
        self.setConnection()
        self.setExecutionType()
