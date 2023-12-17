from PyQt6.QtWidgets import QToolButton, QLabel, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from lib.ui.WidgetFactory.CustomViewDelegate import CustomViewDelegate, CustomDelegateWidget

class PackageViewDelegate(CustomViewDelegate):

    def __init__(self, model_data, application, parent_view, parent_module):
        super().__init__(model_data=model_data, application=application, parent_view=parent_view, parent_module=parent_module)

        
    def createEditor(self, parent, option, index):
        if not index.isValid():
            return False

        column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if column_name == "Actions" and item.task_class == "PackageManager_TaskDefinition":
            editor = TaskDefinitionWidget(model_item=item, application=self.application, parent_view=self.parent_view, parent_module=self.parent_module)
            return editor
        
        if column_name == "Actions" and item.task_class == "PackageManager_PackageDefinition":
            editor = PackageDefinitionWidget(model_item=item, application=self.application, parent_view=self.parent_view, parent_module=self.parent_module)
            return editor

        return super().createEditor(parent, option, index)


class PackageManagerItemWidget(CustomDelegateWidget):

    def __init__(self, parent_view, application, model_item, parent_module):
        super().__init__(parent_view=parent_view, application=application, model_item=model_item, parent_module=parent_module)

        self.object_configuration = self.application.getConfigurationParameters(model_item.task_class)
        self.setupUi()

        self.model_item.data_changed.connect(self.refreshUi)

    def setupUi(self):

        self.element_label = QLabel(self)
        self.element_label.setProperty("CustomWidget", "ItemLabel")
                
        self.element_description = QLabel(self)
        self.element_description.setProperty("CustomWidget", "ItemDescription")
        self.element_description.setWordWrap(True)

        description_config = self.object_configuration.get("Description", None)
        if description_config:
            show_description = description_config.get("ShowInTreeView", True) == True
            if not show_description:
                self.element_description.setHidden(True)

        self.layout.addWidget(self.element_label, 0, 0, 1, 4, Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.element_description, 1, 0, 1, 5)

        self.dynamic_property_labels = {}
        dynamic_property_columns = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_setting(self.model_item.task_class, "ShowInTreeView")
        # lay out items in columns (labels and values)
        layout_columns = 4
        self.layout.setColumnStretch(layout_columns, 1)
        
        if len(dynamic_property_columns) > 0:
            managed_roles = ["DisplayRole", "DescriptionRole"]
            row = self.layout.rowCount()
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

        """ Refresh state based on the model data """
        self.refreshUi()

    def refreshUi(self):
        object_display = self.model_item.display

        self.setProperty("ObjectSaved", str(self.model_item.is_saved))
        self.setStyleSheet(self.styleSheet())

        for column, label_widget in self.dynamic_property_labels.items():
            value = self.model_item.data(column)
            if value:
                label_widget.setText(str(value))

        if not self.model_item.is_saved:
            object_display = f"* {object_display}"
        
        self.element_label.setText(object_display)
        self.element_description.setText(self.model_item.description)
        
        self.parent_view.model().layoutChanged.emit()


class PackageDefinitionWidget(PackageManagerItemWidget):
    def __init__(self, parent_view, application, model_item, parent_module):
        
        super().__init__(parent_view=parent_view, application=application, model_item=model_item, parent_module=parent_module)

        self.edit_feature_button = QToolButton()
        self.edit_feature_button.setText("Properties")
        self.edit_feature_button.clicked.connect(self.edit_feature)

        edit_properties_icon = self.ProgramConfiguration.getIcon("ObjectProperties")
        if edit_properties_icon:
            self.edit_feature_button.setText("")
            self.edit_feature_button.setToolTip("<i>Edit Object Properties..</i>")
            self.edit_feature_button.setIcon(edit_properties_icon)
            self.edit_feature_button.setProperty("PackageManager", "PackageManagerIcon")
            self.edit_feature_button.setIconSize(QSize(20,20))

        self.save_feature_button = QToolButton()
        self.save_feature_button.setText("Save")

        save_icon = self.ProgramConfiguration.getIcon("SaveObject")
        if save_icon:
            self.save_feature_button.setText("")
            self.save_feature_button.setToolTip("<i>Save Package Definition..</i>")
            self.save_feature_button.setIcon(save_icon)
            self.save_feature_button.setProperty("PackageManager", "PackageManagerIcon")
            self.save_feature_button.setIconSize(QSize(20,20))

        self.layout.addWidget(self.edit_feature_button, 0, 4, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.save_feature_button, 0, 5, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.frame.setProperty("PackageManagerWidget", "PackageItem")

        self.save_feature_button.clicked.connect(self.save_feature)

    def save_feature(self, save_single=True):
        index = self.parent_view.model().indexOf(self.model_item)
        self.parent_module.savePackageDefinition(index, save_single)
    
    def edit_feature(self):
        index = self.parent_view.model().indexOf(self.model_item)
        self.parent_module.editPackageDefinition(index)


class TaskDefinitionWidget(PackageManagerItemWidget):
    edit_task_definition = pyqtSignal(object)
    
    def __init__(self, parent_view, application, model_item, parent_module):
        
        super().__init__(parent_view=parent_view, application=application, model_item=model_item, parent_module=parent_module)

        """ Add Custom Widgets """
        self.edit_xml_definition_button = QToolButton()
        self.edit_task_definition_button = QToolButton()

        self.edit_xml_definition_button.setText("Edit XML")
        self.edit_task_definition_button.setText("Properties")

        edit_properties_icon = self.ProgramConfiguration.getIcon("ObjectProperties")
        
        if edit_properties_icon:
            self.edit_task_definition_button.setText("")
            self.edit_task_definition_button.setToolTip("<i>Edit Object Properties..</i>")
            self.edit_task_definition_button.setIcon(edit_properties_icon)
            self.edit_task_definition_button.setProperty("PackageManager", "PackageManagerIcon")
            self.edit_task_definition_button.setIconSize(QSize(20,20))

        edit_xml_icon = self.ProgramConfiguration.getIcon("EditXMLDefinition")
        if edit_xml_icon:
            self.edit_xml_definition_button.setText("")
            self.edit_xml_definition_button.setToolTip("<i>Edit XML Template..</i>")
            self.edit_xml_definition_button.setIcon(edit_xml_icon)
            self.edit_xml_definition_button.setProperty("PackageManager", "PackageManagerIcon")
            self.edit_xml_definition_button.setIconSize(QSize(20,20))

        task_buttons_layout = QHBoxLayout()
        task_buttons_layout.addStretch(2)
        task_buttons_layout.addWidget(self.edit_xml_definition_button)
        task_buttons_layout.addWidget(self.edit_task_definition_button)
        
        self.frame.setProperty("PackageManagerWidget", "TaskItem")

        """ Connect Signals """
        self.edit_xml_definition_button.clicked.connect(self.edit_task_xml_definition)
        self.edit_task_definition_button.clicked.connect(self.edit_task_definition)
        
        """ Add Widgets to the layout """
        self.layout.addLayout(task_buttons_layout, 0, 2, 1, 3, Qt.AlignmentFlag.AlignRight)

        self.model_item.data_changed.connect(self.refresh_item_data)
        self.refresh_item_data()

    def edit_task_definition(self):
        index = self.parent_view.model().indexOf(self.model_item)
        self.parent_module.editTaskDefinition(index)

    def edit_task_xml_definition(self):
        index = self.parent_view.model().indexOf(self.model_item)
        self.parent_module.editXMLTemplate(index)

    def refresh_item_data(self):
        """ hide the edit button for non-transport tasks """               
        self.edit_xml_definition_button.setVisible(self.model_item.is_transport)

