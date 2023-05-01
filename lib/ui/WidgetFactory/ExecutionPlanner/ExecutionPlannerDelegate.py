from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QRadioButton, QComboBox
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPalette, QPen, QPainterPath 
from lib.ui.Theme import Application_Theme

class ExecutionPlannerDelegate(QStyledItemDelegate):
    def __init__(self, model_data, parent=None):
        super().__init__(parent)
        # self.parent = parent
        # self.items = ["", "Import", "Export"]
        self.model_data = model_data

    def createEditor(self, parent, option, index):
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if column_name == "Actions" and item.task_class == "TaskItem":
            editor = ItemActionWidget(data_item=item, tree_view=self.parent())
            return editor
        
        if column_name == "Actions" and item.task_class == "TaskGroup":
            editor = GroupActionWidget(data_item=item, tree_view=self.parent())
            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if column_name == "Actions" and item.task_class in ["TaskItem", "TaskGroup"]:
            viewport = self.parent().viewport()
            editor.setParent(viewport)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        # column_name = self.model_data.headerData(index.column())
        # item = index.internalPointer()
        # if column_name == "Type" and item.task_class == "TaskItem":
        #     text = self.items[editor.currentIndex()]
        #     model.setData(index, text, Qt.ItemDataRole.EditRole)
        # else:
        #     super().setModelData(editor, model, index)
        # print("setting data?")
        super().setModelData(editor, model, index)

    def paint(self, painter, option, index):
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()

        if column_name == "Actions" and item.task_class in ["TaskItem", "TaskGroup"]:
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
                pen.setWidth(2)
                painter.setPen(pen)
                painter.setBrush(selection_color)

                # Set the border color of the item
                painter.drawRoundedRect(option.rect, 4.0, 4.0, Qt.SizeMode.AbsoluteSize)
                # Fill the rounded rectangle with the brush
                painter_path = QPainterPath()
                rectf = QRectF(option.rect)
                painter_path.addRoundedRect(rectf, 4.0, 4.0)
                painter.fillPath(painter_path, painter.brush())
        else:
            super().paint(painter, option, index)

class ExecutionPlannerItem(QFrame):
    def __init__(self, data_item, tree_view, parent=None):
        super().__init__(parent=parent)
        self.tree_view = tree_view
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

        self.element_description = QLabel(self)
        self.element_description.setProperty("ExecutionPlannerWidget", "ItemDescription")
        self.element_description.setWordWrap(True)

        self.layout.addWidget(self.element_label, 0, 0, 1, 2)
        self.layout.addWidget(self.element_description, 1, 0, 1, 4)
        self.layout.addWidget(self.button1, 0, 3)
        self.refresh_data()
    
    def refresh_data(self):
        self.element_label.setText(self.data_item.data("Name"))
        self.element_description.setText(self.data_item.data("Description"))


class GroupActionWidget(ExecutionPlannerItem):
    def __init__(self, data_item, tree_view, parent=None):
        super().__init__(data_item=data_item, tree_view=tree_view, parent=parent)

    def refresh_data(self):
        super().refresh_data()
        self.setProperty("ExecutionPlannerWidget", "GroupItem")
        self.button1.setText("Start Group")


class ItemActionWidget(ExecutionPlannerItem):
    def __init__(self, data_item, tree_view, parent=None):
        super().__init__(data_item=data_item, tree_view=tree_view, parent=parent)

        self.treeview = self.parent()
        self.setProperty("ExecutionPlannerWidget", "TaskItem")
        self.button1.setText("Start Task")

        """ Add Custom Widgets """
        self.transport_type_label = QLabel(self)
        self.task_execution_import = QRadioButton("Run Import Task")
        self.task_execution_export = QRadioButton("Run Export Task")
        self.connection_box = QComboBox(self)
        self.connection_box.addItems(["Import Connection", "Export Connection"])
        
        """ Add Widgets to the layout """
        self.layout.addWidget(self.transport_type_label, 2, 0)
        self.layout.addWidget(self.task_execution_import, 2, 1)
        self.layout.addWidget(self.task_execution_export, 2, 2)
        self.layout.addWidget(self.connection_box, 2, 3)

        """ Refresh state based on the model data """
        
        self.refresh_model_data(self.data_item)

        """ Connect Signals """
        self.task_execution_import.toggled.connect(self.set_task_execution_type)
        self.task_execution_export.toggled.connect(self.set_task_execution_type)
        self.connection_box.currentTextChanged.connect(self.set_task_connection)

        self.data_item.data_changed.connect(self.refresh_display)

    def start_task_execution(self):
        self.application.start_task_execution.emit(self.data_item)

    def refresh_display(self, model_item=None):
        if model_item == self.data_item:
            self.is_refresh = True
            self.refresh_model_data(model_item)
            self.is_refresh = False

    def refresh_model_data(self, model_item=None):
        if model_item != self.data_item:
            return False

        self.element_label.setText(self.data_item.data("TaskName"))
        
        # print("refresh", model_item, self.data_item)
        model_task_type = self.data_item.data("TaskType")
        task_type_label = f"Task Type: {model_task_type}"
        self.transport_type_label.setText(task_type_label)

        is_export = self.data_item.data("ExecutionType") == "Export"
        if is_export:
            self.task_execution_export.setChecked(True)
        else:
            self.task_execution_import.setChecked(True)
        
        self.connection_box.setCurrentText(self.data_item.data("Connection"))


    def set_task_execution_type(self):
        if self.is_refresh:
            return False

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
        
    def set_task_connection(self):
        connection = self.connection_box.currentText()

        self.data_item.setData("Connection", connection)

        for selected_index in self.tree_view.selectedIndexes():
            selected_item = selected_index.internalPointer()
            selected_item.setData("Connection", connection)


