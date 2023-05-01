from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QPalette, QPen, QPainterPath 
from lib.ui.Theme import Application_Theme

class PackageViewDelegate(QStyledItemDelegate):

    def __init__(self, model_data, application, parent=None):
        super().__init__(parent)
        # self.items = ["", "Import", "Export"]
        self.model_data = model_data
        self.application = application

    def createEditor(self, parent, option, index):
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if column_name == "Actions" and item.task_class == "TaskItem":
            editor = TaskDefinitionWidget(data_item=item, application=self.application)
            return editor
        
        if column_name == "Actions" and item.task_class == "PackageDefinition":
            editor = PackageDefinitionWidget(data_item=item, application=self.application)
            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if column_name == "Actions" and item.task_class in ["TaskItem", "PackageDefinition"]:
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
        super().setModelData(editor, model, index)

    def paint(self, painter, option, index):
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()

        if column_name == "Actions":
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

class PackageManagerItemWidget(QFrame):
        def __init__(self, data_item, application, parent=None):
            super().__init__(parent=parent)
            self.application = application
            self.data_item = data_item

            self.layout = QGridLayout(self)
            self.layout.setContentsMargins(2, 2, 2, 2)
            self.layout.setSpacing(3)

            self.element_label = QLabel(self)
            self.element_label.setProperty("ExecutionPlannerWidget", "ItemLabel")
            self.element_label.setText(self.data_item.data("Name"))

            self.element_description = QLabel(self)
            self.element_description.setProperty("ExecutionPlannerWidget", "ItemDescription")
            self.element_description.setText(self.data_item.data("Description"))
            self.element_description.setWordWrap(True)

            self.layout.addWidget(self.element_label, 0, 0, 1, 2)
            self.layout.addWidget(self.element_description, 1, 0, 1, 4)


class PackageDefinitionWidget(PackageManagerItemWidget):
    def __init__(self, data_item, application, parent=None):
        super().__init__(data_item=data_item, application=application, parent=parent)
        self.element_label.setText(self.data_item.data("FeatureName"))
        self.setProperty("ExecutionPlannerWidget", "GroupItem")


class TaskDefinitionWidget(PackageManagerItemWidget):
    def __init__(self, data_item, application, parent=None):
        super().__init__(data_item=data_item, application=application, parent=parent)

        self.setProperty("ExecutionPlannerWidget", "TaskItem")
        self.element_label.setText(self.data_item.data("TaskName"))

        """ Add Custom Widgets """
        self.task_type = QLabel()
        self.edit_xml_definition_button = QToolButton()
        self.edit_task_definition_button = QToolButton()

        """ Connect Signals """
        self.edit_xml_definition_button.clicked.connect(self.edit_task_definition)
        
        """ Add Widgets to the layout """
        self.layout.addWidget(self.task_type, 2, 0)
        self.layout.addWidget(self.edit_xml_definition_button, 0, 3)
        self.layout.addWidget(self.edit_task_definition_button, 0, 4)

        """ Refresh state based on the model data """
        self.refresh_data()

    def edit_task_definition(self):
        self.application.edit_definition.emit(self.data_item)

    def refresh_data(self):
        self.task_type.setText(self.data_item.data("TaskType"))
        self.edit_xml_definition_button.setText("Edit XML")
        self.edit_task_definition_button.setText("Edit Task")

        is_transport = self.data_item.data("TaskType") in ["Transport", "FeatureUpdate", "BugFix"]
        self.edit_xml_definition_button.setVisible(is_transport)

