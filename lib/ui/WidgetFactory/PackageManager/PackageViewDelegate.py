from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QEvent
from PyQt6.QtGui import QPalette, QPen, QPainterPath 
from lib.ui.Theme import Application_Theme
import lib.ui.WidgetFactory as WidgetFactory
import json
import os
import pathlib

class PackageViewDelegate(QStyledItemDelegate):

    def __init__(self, model_data, application, parent=None):
        super().__init__(parent)
        # self.items = ["", "Import", "Export"]
        self.model_data = model_data
        self.application = application
        self.object_definitions = self.application.object_definitions
        self.application_palette = self.application.color_theme
        self.parent().setAlternatingRowColors(False)

    def createEditor(self, parent, option, index):
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
        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if column_name == "Actions" and item.task_class in ["PackageManager_TaskDefinition", "PackageManager_PackageDefinition"]:
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

class PackageManagerItemWidget(QFrame):
    def __init__(self, data_item, application, parent=None):
        super().__init__(parent=parent)
        self.application = application
        self.data_item = data_item
        self.treeview = parent
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

    # def filter_object(self, show_widget):
    #     print("filter here", self.data_item.display, show_widget)
    #     self.setHidden(not show_widget)


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
    def __init__(self, data_item, application, parent=None):
        
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
        export = self.data_item.export_data
        if "ExportFilesLocation" in export.keys():
            export.pop("ExportFilesLocation")
        if "DefinitionFile" in export.keys():
            export.pop("DefinitionFile")

        export_data = json.dumps(export, indent=4, separators=(',',':'))
        print("Export Data" , export_data)
        definition_file = self.data_item.data("DefinitionFile")
        if definition_file and self.application.current_workdir:
            export_file = f"{self.application.current_workdir}/{definition_file}"
            print("export to: ", definition_file, export_file)
            pathlib.Path(export_file).parent.mkdir(parents=True, exist_ok=True)
            with open(export_file, 'w') as doc:
                doc.write(export_data)
            self.data_item.save()
    
    def edit_feature(self):
        index = self.treeview.model().indexOf(self.data_item)
        self.application.edit_package_definition(index)


class TaskDefinitionWidget(PackageManagerItemWidget):
    
    edit_task_definition = pyqtSignal(object)
    
    def __init__(self, data_item, application, parent=None):

        """ Add Custom Widgets """
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

        """ init parent class """

        super().__init__(data_item=data_item, application=application, parent=parent)
        
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


    def edit_task_definition(self):
        index = self.treeview.model().indexOf(self.data_item)
        self.application.edit_task_definition(index)

    def edit_task_xml_definition(self):
        index = self.treeview.model().indexOf(self.data_item)
        self.application.edit_task_xml_definition(index)

    def refresh_data(self):
        super().refresh_data()

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

