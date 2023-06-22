from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPropertyAnimation, QSize, QEasingCurve, QAbstractAnimation
from PyQt6.QtGui import QPalette, QPen, QPainterPath
import json
import os
import pathlib

class PackageViewDelegate(QStyledItemDelegate):

    def __init__(self, model_data, application, parent_widget=None):
        super().__init__(parent_widget)
        # self.items = ["", "Import", "Export"]
        self.model_data = model_data
        self.application = application
        self.object_definitions = self.application.object_definitions
        self.application_palette = self.application.color_theme
        self.parent().setAlternatingRowColors(False)

    def createEditor(self, parent, option, index):
        if not index.isValid():
            return False
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        # print("create editor for column", column_name, item, item.task_class)
        if column_name == "Actions" and item.task_class == "PackageManager_TaskDefinition":
            editor = TaskDefinitionWidget(data_item=item, application=self.application, parent=self.parent())
            return editor
        
        if column_name == "Actions" and item.task_class == "PackageManager_PackageDefinition":
            editor = PackageDefinitionWidget(data_item=item, application=self.application, parent=self.parent())
            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if not index.isValid():
            return False
            
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if column_name == "Actions" and item.task_class in ["PackageManager_TaskDefinition", "PackageManager_PackageDefinition"]:
            viewport = self.parent().viewport()
            editor.setParent(viewport)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if not index.isValid():
            return False
        super().setModelData(editor, model, index)

    def paint(self, painter, option, index):
        if not index.isValid():
            return False

        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()

        if column_name == "Actions":
            widget = self.parent().indexWidget(index)
            if not widget:
                widget = self.createEditor(self.parent(), option, index)
                self.setEditorData(widget, index)
                self.parent().setIndexWidget(index, widget)
                widget.setGeometry(option.rect)
            else:
                widget.setGeometry(option.rect)
            # widget.show()
            # Check if the item is selected

            if option.state & QStyle.StateFlag.State_Selected:
                selection_color = self.application_palette.color(QPalette.ColorRole.Highlight)
                
                # Set the pen color to the selection color
                pen = QPen(selection_color)
                pen.setWidth(3)
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

    def sizeHint(self, arg1, arg2):
        return QSize(55, 55)

class PackageManagerItemWidget(QFrame):

    def __init__(self, data_item, application, parent):
        super().__init__(parent=parent)
        self.application = application
        self.data_item = data_item
        self.treeview = parent
        self.parent = parent
        self.object_definitions = self.application.object_definitions

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)

        self.element_label = QLabel(self)
        self.element_label.setProperty("ExecutionPlannerWidget", "ItemLabel")

        self.element_description = QLabel(self)
        self.element_description.setProperty("ExecutionPlannerWidget", "ItemDescription")
        self.element_description.setWordWrap(True)

        self.layout.addWidget(self.element_label, 0, 0, 1, 2)
        self.layout.addWidget(self.element_description, 1, 0, 1, 5)
        self.data_item.data_changed.connect(self.refresh_data)
        # self.data_item.filter_object.connect(self.filter_object)
        """ Refresh state based on the model data """
        self.refresh_data()

        self.treeview.expanded.connect(self.expand_children)
        self.treeview.collapsed.connect(self.collapse_children)
        self.animate()
    
    def animate(self, reverse=False):
        # animate startup
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        animation = QPropertyAnimation(self)
        animation.setPropertyName(bytes("opacity", "utf-8"))
        animation.setTargetObject(effect)
        animation.setDuration(350)
        animation.setStartValue(0)
        animation.setEndValue(1)
        if reverse:
            animation.setStartValue(1)
            animation.setEndValue(0)
            animation.setDuration(100)
        
        animation.setEasingCurve(QEasingCurve.Type.OutInCubic)
        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def expand_children(self, index):
        if not index.isValid():
            return False
        expanded_item = index.internalPointer()

        if expanded_item != self.data_item.parent():
            return False
        self.animate()
        
    def collapse_children(self, index):
        if not index.isValid():
            return False
        collapsed_item = index.internalPointer()

        if collapsed_item != self.data_item.parent():
            return False
        
        self.animate(reverse=True)
        
    def refresh_data(self):
        object_display = self.data_item.display

        self.setProperty("ObjectSaved", str(self.data_item.is_saved))
        self.setStyleSheet(self.styleSheet())

        # print(self.data_item.display, "is saved", self.data_item.is_saved, self.property("ObjectSaved"))

        if not self.data_item.is_saved:
            object_display = f"* {object_display}"
        
        self.element_label.setText(object_display)
        self.element_description.setText(self.data_item.description)


class PackageDefinitionWidget(PackageManagerItemWidget):
    def __init__(self, data_item, application, parent):
        
        super().__init__(data_item=data_item, application=application, parent=parent)

        self.edit_feature_button = QToolButton()
        self.edit_feature_button.setText("Properties")
        self.edit_feature_button.clicked.connect(self.edit_feature)

        self.save_feature_button = QToolButton()
        self.save_feature_button.setText("Save")

        self.layout.addWidget(self.edit_feature_button, 0, 3, 1, 1)
        self.layout.addWidget(self.save_feature_button, 0, 4, 1, 1)

        self.setProperty("ExecutionPlannerWidget", "GroupItem")

        self.save_feature_button.clicked.connect(self.save_feature)

    def save_feature(self):
        self.data_item.save()
    
    def edit_feature(self):
        index = self.treeview.model().indexOf(self.data_item)
        self.application.edit_package_definition(index)

class TaskDefinitionWidget(PackageManagerItemWidget):
    
    edit_task_definition = pyqtSignal(object)
    
    def __init__(self, data_item, application, parent):

        """ init parent class """
        super().__init__(data_item=data_item, application=application, parent=parent)

        """ Add Custom Widgets """
        self.parent=parent
        self.task_type_label = QLabel()
        self.task_state_label = QLabel()
        self.task_compiler_label = QLabel()
        self.task_autoupdate_label = QLabel()

        self.edit_xml_definition_button = QToolButton()
        self.edit_task_definition_button = QToolButton()

        type_label = QLabel("Type: ")
        state_label = QLabel("State: ")
        compiler_label = QLabel("Compiler Option: ")
        autoupdate_label = QLabel("AutoUpdate: ")

        """ Set Properties for Labels """
        type_label.setProperty("Label", "PropertyName")
        state_label.setProperty("Label", "PropertyName")
        compiler_label.setProperty("Label", "PropertyName")
        autoupdate_label.setProperty("Label", "PropertyName")

        self.task_type_label.setProperty("Label", "PropertyValue")
        self.task_state_label.setProperty("Label", "PropertyValue")
        self.task_compiler_label.setProperty("Label", "PropertyValue")
        self.task_autoupdate_label.setProperty("Label", "PropertyValue")

        task_buttons_layout = QHBoxLayout()
        task_buttons_layout.addStretch(2)
        task_buttons_layout.addWidget(self.edit_xml_definition_button)
        task_buttons_layout.addWidget(self.edit_task_definition_button)
        
        self.setProperty("ExecutionPlannerWidget", "TaskItem")

        """ Connect Signals """
        self.edit_xml_definition_button.clicked.connect(self.edit_task_xml_definition)
        self.edit_task_definition_button.clicked.connect(self.edit_task_definition)
        
        """ Add Widgets to the layout """
        self.layout.addLayout(task_buttons_layout, 0, 2, 1, 3)
        self.layout.addWidget(type_label, 2, 0)
        self.layout.addWidget(self.task_type_label, 2, 1)
        self.layout.addWidget(state_label, 2, 2)
        self.layout.addWidget(self.task_state_label, 2, 3)
        self.layout.addWidget(compiler_label, 3, 0)
        self.layout.addWidget(self.task_compiler_label, 3, 1)
        self.layout.addWidget(autoupdate_label, 3, 2)
        self.layout.addWidget(self.task_autoupdate_label, 3, 3)
        self.layout.setColumnStretch(4, 1)

        self.data_item.data_changed.connect(self.refresh_item_data)
        self.refresh_item_data()

    def edit_task_definition(self):
        index = self.treeview.model().indexOf(self.data_item)
        self.application.edit_task_definition(index)

    def edit_task_xml_definition(self):
        index = self.treeview.model().indexOf(self.data_item)
        self.application.edit_task_xml_definition(index)

    def refresh_item_data(self):
        # super().refresh_data()
        # self.element_description.setText(self.data_item.data("Description"))

        self.task_type_label.setText(self.data_item.data("TaskType"))
        self.task_state_label.setText(self.data_item.data("State"))
        self.task_compiler_label.setText(self.data_item.data("CompilerOption"))
        self.task_autoupdate_label.setText(self.data_item.data("AutoUpdate"))

        self.edit_xml_definition_button.setText("Edit XML")
        self.edit_task_definition_button.setText("Properties")
        
        """ hide the edit button for non-transport tasks """
        is_transport = self.data_item.data("TaskType") in ["Transport", "FeatureUpdate", "BugFix"]
        self.edit_xml_definition_button.setVisible(is_transport)

