from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PyQt6.QtGui import QPalette, QPen, QPainterPath
from lib.ui.WidgetFactory import MsgBox

class PackageViewDelegate(QStyledItemDelegate):

    def __init__(self, model_data, application, parent_widget, package_manager):
        super().__init__(parent_widget)
        # self.items = ["", "Import", "Export"]
        self.model_data = model_data
        self.application = application
        self.package_manager = package_manager
        self.application_palette = self.application.color_theme
        
    def createEditor(self, parent, option, index):
        if not index.isValid():
            return False
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        # print("create editor for column", column_name, item, item.task_class)
        if column_name == "Actions" and item.task_class == "PackageManager_TaskDefinition":
            editor = TaskDefinitionWidget(data_item=item, application=self.application, parent=self.parent(), package_manager=self.package_manager)
            return editor
        
        if column_name == "Actions" and item.task_class == "PackageManager_PackageDefinition":
            editor = PackageDefinitionWidget(data_item=item, application=self.application, parent=self.parent(), package_manager=self.package_manager)
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
                if selection_color:
                    selection_color.setAlphaF(0.2)
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

class PackageManagerItemWidget(QFrame):

    def __init__(self, data_item, application, parent, package_manager):
        super().__init__(parent=parent)
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self.package_manager = package_manager
        self.data_item = data_item
        self.treeview = parent
        self.parent = parent
        self.object_configuration = self.application.getConfigurationParameters(data_item.task_class)

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)

        self.element_label = QLabel(self)
        self.element_label.setProperty("ExecutionPlannerWidget", "ItemLabel")
                
        self.element_description = QLabel(self)
        self.element_description.setProperty("ExecutionPlannerWidget", "ItemDescription")
        self.element_description.setWordWrap(True)

        description_config = self.object_configuration.get("Description", None)
        if description_config:
            show_description = description_config.get("ShowInTreeView", True) == True
            if not show_description:
                self.element_description.setHidden(True)

        self.layout.addWidget(self.element_label, 0, 0, 1, 4, Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.element_description, 1, 0, 1, 5)

        self.element_description.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        # self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self.dynamic_property_labels = {}
        dynamic_property_columns = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_setting(self.data_item.task_class, "ShowInTreeView")
        # lay out items in columns (labels and values)
        layout_columns = 4
        self.layout.setColumnStretch(layout_columns, 1)
        
        if len(dynamic_property_columns) > 0:
            row = self.layout.rowCount()
            column_count = 0
            for column, column_configuration in dynamic_property_columns.items():
                show_entry = column_configuration.get("ShowInTreeView", True) == True
                if not show_entry:
                    continue
                label = QLabel(f"{column}:")
                label.setProperty("Label", "PropertyName")
                value = QLabel()
                value.setProperty("Label", "PropertyValue")
                value.setWordWrap(True)
                value.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

                self.layout.addWidget(label, row, column_count, 1, 1)
                self.layout.addWidget(value, row, column_count+1, 1, 1)
                self.dynamic_property_labels[column] = value
                # add 2 added columns to the counter
                column_count += 2
                if column_count >= layout_columns:
                    row += 1
                    column_count = 0
        self.layout.setColumnStretch(4, 2)
        self.data_item.data_changed.connect(self.refresh_data)
        # self.data_item.filter_object.connect(self.filter_object)
        """ Refresh state based on the model data """
        self.refresh_data()

        self.treeview.expanded.connect(self.expand_children)
        self.treeview.collapsed.connect(self.collapse_children)
        self.animate()
    
    # def sizeHint(self):
    #     # print("getting size hint for widget", self.layout.sizeHint())
    #     return self.layout.sizeHint()

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

        for column, label_widget in self.dynamic_property_labels.items():
            label_widget.setText(str(self.data_item.data(column)))

        if not self.data_item.is_saved:
            object_display = f"* {object_display}"
        
        self.element_label.setText(object_display)
        self.element_description.setText(self.data_item.description)
        self.treeview.model().layoutChanged.emit()

class PackageDefinitionWidget(PackageManagerItemWidget):
    def __init__(self, data_item, application, parent, package_manager):
        
        super().__init__(data_item=data_item, application=application, parent=parent, package_manager=package_manager)

        self.edit_feature_button = QToolButton()
        self.edit_feature_button.setText("Properties")
        self.edit_feature_button.clicked.connect(self.edit_feature)

        self.save_feature_button = QToolButton()
        self.save_feature_button.setText("Save")

        self.layout.addWidget(self.edit_feature_button, 0, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.save_feature_button, 0, 5, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.setProperty("ExecutionPlannerWidget", "GroupItem")

        self.save_feature_button.clicked.connect(self.save_feature)

    def save_feature(self, save_single=True):
        index = self.treeview.model().indexOf(self.data_item)
        self.package_manager.savePackageDefinition(index, save_single)
    
    def edit_feature(self):
        index = self.treeview.model().indexOf(self.data_item)
        self.package_manager.editPackageDefinition(index)

class TaskDefinitionWidget(PackageManagerItemWidget):
    
    edit_task_definition = pyqtSignal(object)
    
    def __init__(self, data_item, application, parent, package_manager):

        """ init parent class """
        super().__init__(data_item=data_item, application=application, parent=parent, package_manager=package_manager)

        """ Add Custom Widgets """
        self.parent=parent
        self.edit_xml_definition_button = QToolButton()
        self.edit_task_definition_button = QToolButton()

        task_buttons_layout = QHBoxLayout()
        task_buttons_layout.addStretch(2)
        task_buttons_layout.addWidget(self.edit_xml_definition_button)
        task_buttons_layout.addWidget(self.edit_task_definition_button)
        
        self.setProperty("ExecutionPlannerWidget", "TaskItem")

        """ Connect Signals """
        self.edit_xml_definition_button.clicked.connect(self.edit_task_xml_definition)
        self.edit_task_definition_button.clicked.connect(self.edit_task_definition)
        
        """ Add Widgets to the layout """
        self.layout.addLayout(task_buttons_layout, 0, 2, 1, 3, Qt.AlignmentFlag.AlignRight)

        self.data_item.data_changed.connect(self.refresh_item_data)
        self.refresh_item_data()

    def edit_task_definition(self):
        index = self.treeview.model().indexOf(self.data_item)
        self.package_manager.editTaskDefinition(index)

    def edit_task_xml_definition(self):
        index = self.treeview.model().indexOf(self.data_item)
        self.package_manager.editXMLTemplate(index)

    def refresh_item_data(self):
        self.edit_xml_definition_button.setText("Edit XML")
        self.edit_task_definition_button.setText("Properties")
        
        """ hide the edit button for non-transport tasks """               
        self.edit_xml_definition_button.setVisible(self.data_item.is_transport)

