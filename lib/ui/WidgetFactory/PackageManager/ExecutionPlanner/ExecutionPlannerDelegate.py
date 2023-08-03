from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QRadioButton, QComboBox, QHBoxLayout, QVBoxLayout, QSpacerItem
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPalette, QPen, QPainterPath 
from lib.ui.Theme import Application_Theme
from lib.ui.WidgetFactory.PackageManager.PackageViewDelegate import PackageDefinitionWidget

class ExecutionPlannerDelegate(QStyledItemDelegate):
    queueExecutionTask = pyqtSignal(object)
    queueExecutionGroup = pyqtSignal(object)

    def __init__(self, model_data, application, planner_widget, parent=None):
        super().__init__(parent)
        self.application = application
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
                widget.show()
            else:
                widget.setGeometry(option.rect)
            # Check if the item is selected
            
            if option.state & QStyle.StateFlag.State_Selected:
                palette = Application_Theme()
                selection_color = palette.color(QPalette.ColorRole.Highlight)
                
                # Set the pen color to the selection color
                pen = QPen(selection_color)
                pen.setWidth(3)
                painter.setPen(pen)
                painter.setBrush(selection_color)

                # Set the border color of the item
                painter.drawRoundedRect(option.rect, 3.0, 3.0, Qt.SizeMode.AbsoluteSize)
                # Fill the rounded rectangle with the brush
                painter_path = QPainterPath()
                rectf = QRectF(option.rect)
                painter_path.addRoundedRect(rectf, 3.0, 3.0)
                painter.fillPath(painter_path, painter.brush())
        else:
            super().paint(painter, option, index)

class ExecutionPlannerItem(QFrame):
    taskExecutionRequested = pyqtSignal(object)

    def __init__(self, data_item, tree_view, application, planner_widget, parent=None):
        super().__init__(parent=parent)
        self.tree_view = tree_view
        self.application = application
        self.planner_widget = planner_widget
        self.data_item = data_item
        self.button1 = QToolButton(self)
        self.is_refresh = False

        self.button1.setText("Start")
        self.button1.setProperty("ExecutionPlannerWidget", "ActionItem")

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(3)

        self.element_label = QLabel(self)
        self.element_label.setProperty("ExecutionPlannerWidget", "ItemLabel")
        self.element_label.setWordWrap(True)

        self.element_description = QLabel(self)
        self.element_description.setProperty("ExecutionPlannerWidget", "ItemDescription")
        self.element_description.setWordWrap(True)

        self.layout.addWidget(self.element_label, 0, 0, 1, 2)
        self.layout.addWidget(self.element_description, 1, 0, 1, 4)
        self.layout.addWidget(self.button1, 0, 4)
        self.data_item.data_changed.connect(self.refreshUI)
        self.refreshUI()

        self.button1.clicked.connect(self.startTaskExecution)
    
    def startTaskExecution(self):
        self.taskExecutionRequested.emit(self.data_item)

    def refreshUI(self):
        self.element_label.setText(self.data_item.display)
        self.element_description.setText(self.data_item.description)
        if self.tree_view.model():
            self.tree_view.model().layoutChanged.emit()


class GroupActionWidget(ExecutionPlannerItem):
    def __init__(self, data_item, tree_view, application, planner_widget, parent=None):
        super().__init__(data_item=data_item, tree_view=tree_view, application=application, planner_widget=planner_widget, parent=parent)
        self.setProperty("ExecutionPlannerWidget", "GroupItem")
        self.button1.setText("Start Group")
        

class ItemActionWidget(ExecutionPlannerItem):
    def __init__(self, data_item, tree_view, application, planner_widget, parent=None):
        super().__init__(data_item=data_item, tree_view=tree_view, application=application, planner_widget=planner_widget, parent=parent)

        self.treeview = self.parent()
        self.setProperty("ExecutionPlannerWidget", "TaskItem")
        self.button1.setText("Start Task")

        """ Add Custom Widgets """
        self.connection_box_label = QLabel("Use Connection:")
        self.task_execution_import = QRadioButton("Run Import Task")
        self.task_execution_export = QRadioButton("Run Export Task")
        self.task_execution_export.setChecked(True)

        self.connection_box = QComboBox(self)
        self.refreshConnections()
        self.application.connectionDataChanged.connect(self.refreshConnections)

        self.run_status = QLabel(self)
        
        self.dynamic_property_labels = {}
        dynamic_property_columns = self.application.object_configuration.get_columns_configuration_by_setting(self.data_item.task_class, "ShowInTreeView")
        # lay out items in columns (labels and values)
        layout_columns = 6
        task_details_layout = QGridLayout()
        # task_details_layout.setColumnStretch(layout_columns, 2)
        
        if len(dynamic_property_columns) > 0:
            row = task_details_layout.rowCount()
            column_count = 0
            for column, column_configuration in dynamic_property_columns.items():
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
        task_params_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.layout.addLayout(task_params_layout, 0, 1, 1, 3)
        self.layout.addLayout(task_details_layout, 2, 0, 1, 3)
        # self.layout.setColumnStretch(3, 1)
        self.layout.addWidget(self.run_status, 2, 4)

        """ Refresh state based on the model data """
        self.refreshTaskUI()

        """ Set initial values """
        self.configureTask()

        """ Connect Signals """
        self.task_execution_import.toggled.connect(self.setExecutionType)
        self.task_execution_export.toggled.connect(self.setExecutionType)
        self.connection_box.currentTextChanged.connect(self.setConnection)
        self.data_item.data_changed.connect(self.refreshTaskUI)

    def refreshConnections(self):
        connections = list(self.application.ConnectionHandler.connections.keys())
        self.connection_box.clear()
        self.connection_box.addItems(connections)

    def refreshTaskUI(self):
        
        for column, label_widget in self.dynamic_property_labels.items():
            label_widget.setText(str(self.data_item.data(column)))

        is_export = self.data_item.data("ExecutionType") == "Export"
        if is_export:
            self.task_execution_export.setChecked(True)
        else:
            self.task_execution_import.setChecked(True)
        
        self.connection_box.setCurrentText(self.data_item.data("Connection"))
        self.run_status.setText(self.data_item.data("task_execution_status"))

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
        self.setConnection()
        self.setExecutionType()
