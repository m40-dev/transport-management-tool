from PyQt6.QtWidgets import (QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, 
QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy, QLineEdit, QComboBox, QApplication, QGroupBox,
QWidget, QTextEdit, QPlainTextEdit, QAbstractScrollArea)
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QSize, QMimeData, QPoint
from PyQt6.QtGui import QPalette, QPen, QPainterPath,QDrag, QColor, QBrush, QPainter


from lib.ui.WidgetFactory.DialogScreens.FormEditorDialog import FormEditorObject
from lib.ui.WidgetFactory.CustomViewDelegate import CustomDelegateWidget

class ObjectModelConfigurationWidget(CustomDelegateWidget):

    def __init__(self, parent_view, application, model_item, parent_module):
        super().__init__(parent_view=parent_view, application=application, model_item=model_item, parent_module=parent_module)

        self.widget_data = self.ProgramConfiguration.getConfigurationParameters("ObjectModelConfiguration")
        self.isActive = model_item.isActive

        # self.drag_start_position = None
        self.setAcceptDrops(True)

        self.editors = {}
        self.setupUi()

        """ Refresh state based on the model data """
        self.refreshUi()
        self.animate()
        
        self.parent_view.model().layoutChanged.emit()
        self.model_item.data_changed.connect(self.refreshUi)
        self.parent_module.currentItemChanged.connect(self.toggleFieldConfiguration)
        if self.isActive:
            self.parent_module.currentItemChanged.emit(self.model_item)


    def refreshUi(self):
        #UI refresh
        self.setStyleSheet(self.styleSheet())

        #Attributes refresh - configure editors activity
        self.deactivateEditors()

        if self.parent_view.model():
            self.parent_view.model().layoutChanged.emit()

    def deactivateEditors(self):
        for column, editor in self.editors.items():
            field_configuration = self.widget_data.get(column, None)
            field_dependencies = field_configuration.get("EditDependency", None)
            
            if field_dependencies:
                isEditable = True
                for dependency_column_name, dependency_column_value in field_dependencies.items():
                    model_item_data = self.model_item.data(dependency_column_name)
                    if model_item_data != dependency_column_value:
                        isEditable = False
                    if isinstance(dependency_column_value, list) and model_item_data in dependency_column_value:
                        isEditable = True
                    
                editor.setVisible(isEditable)
                # print(column, "field dependencies", field_dependencies, "is Editable", isEditable)

    def updateConfigurationItem(self, column, value):
        self.model_item.setData(column, value)
        self.parent_module.configurationDataChanged()

    def setupUi(self):

        self.setProperty("ConfigurationEditor", "ObjectModelEditorWidget")
        self.frame.setProperty("ConfigurationEditor", "ObjectModelEditorFrame")

        self.handleBar = QLabel(self)
        self.handleBar.setText("::")
        self.handleBar.setProperty("ConfigurationEditor", "Handle")

        self.layout.addWidget(self.handleBar, 0, 0, 3, 1)

        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 6)
        self.layout.setColumnStretch(3, 1)

        # Collapsed view
        self.addToFormLayout(self.layout, "FieldId", 0, 1)
        self.addToFormLayout(self.layout, "Display", 1, 1)
        self.addToFormLayout(self.layout, "IsMandatory", 0, 3)
        self.addToFormLayout(self.layout, "ShowInEditor", 1, 3)

        #Extended view
        self.subFrame = QGroupBox("Field Configuration Options", self)
        self.subFrame.setProperty("ConfigurationEditor", "FieldConfigurationFrame")
        self.subFrame.setVisible(False)

        self.layout.addWidget(self.subFrame, 2, 1, 1, 4)
        self.layout.setRowStretch(2, 1)

        subFrameLayout = QGridLayout(self.subFrame)
        
        subFrameLayout.setContentsMargins(2,15,2,2)
        subFrameLayout.setSpacing(4)

        subFrameLayout.setColumnStretch(0, 2)
        subFrameLayout.setColumnStretch(1, 6)
        subFrameLayout.setColumnStretch(2, 2)
        subFrameLayout.setColumnStretch(3, 4)

        # Default property values setting

        self.addToFormLayout(subFrameLayout, "FieldType", 0, 0)
        self.addToFormLayout(subFrameLayout, "FieldRole", 1, 0)
        self.addToFormLayout(subFrameLayout, "DefaultValue", 0, 2, 1, 2)
        self.addToFormLayout(subFrameLayout, "PlaceholderText", 1, 2, 1, 2)

        self.addToFormLayout(subFrameLayout, "IsForDataExport", 2, 0)
        self.addToFormLayout(subFrameLayout, "ShowInTreeView", 2, 2)

        deleteItemButton = QToolButton(self)
        deleteItemButton.setText("[X]")
        deleteItemButton.setProperty("ToolButton", "DeleteItem")
        deleteItemButton.clicked.connect(self.removeItem)
        subFrameLayout.addWidget(deleteItemButton, 2, 4)

        editor = self.addToFormLayout(subFrameLayout, "Description", 3, 0, 1, 4)
        if editor and editor.editor:
            # editor.editor.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            editor.editor.setMaximumHeight(75)

        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.HLine)
        subFrameLayout.addWidget(separator, 4, 0, 1, 4, Qt.AlignmentFlag.AlignTop)
        separator.setProperty("FieldConfigurationFrame", "Separator")
        
        #Add field specific editors
        fieldSpecificLayout = QGridLayout()
        fieldSpecificLayout.setContentsMargins(0,0,0,0)
        fieldSpecificLayout.setSpacing(2)

        subFrameLayout.addLayout(fieldSpecificLayout, 5, 0, 1, 5)
        # subFrameLayout.setRowStretch(5, 1)

        #Dynamically load editor widgets into the subframe layout
        default_fields = ["FieldId", "Display", "IsMandatory", "ShowInEditor", "FieldType",
        "FieldRole", "DefaultValue", "PlaceholderText", "IsForDataExport", "ShowInTreeView", "Description"]

        row = 0
        for column_name in self.widget_data.keys():
            if column_name not in default_fields:
                self.addToFormLayout(fieldSpecificLayout, column_name, row, 0)
                row += 1

        fieldSpecificLayout.setColumnStretch(0, 2)
        fieldSpecificLayout.setColumnStretch(1, 12)
        
        fieldSpecificLayout.setRowStretch(fieldSpecificLayout.rowCount()+1, 1)
        self.parent_view.model().layoutChanged.emit()

    def removeItem(self):
        animation = self.animate(True)
        animation.finished.connect(lambda: self.parent_view.model().removeItems([self.model_item]))

    def addToFormLayout(self, layout, column_name, row, column, rowSpan=1, colSpan=1):
        current_value = self.model_item.data(column_name, None)
        
        field_configuration = self.widget_data.get(column_name, None)
        if field_configuration:
            if current_value is None and "DefaultValue" in field_configuration.keys():
                current_value = field_configuration["DefaultValue"]
                self.model_item.setData(column_name, current_value)
                
            field_editor = FormEditorObject(
                parent=self,
                application=self.application,
                column_name=column_name,
                column_configuration=field_configuration)
            
            if field_editor.editor:
                layout.addWidget(field_editor.label, row, column, rowSpan, 1)

                column+=1
                layout.addWidget(field_editor.editor, row, column, rowSpan, colSpan)
                
                # if current_value:
                field_editor.set_editor_data(current_value)

                field_editor.dataChanged.connect(self.updateConfigurationItem)

                field_editor.label.setProperty("ConfigurationEditor", "PropertyLabel")
                field_editor.editor.setProperty("ConfigurationEditor", "PropertyEditor")
                
                # if isinstance(field_editor.editor, (QTextEdit, QPlainTextEdit, FormEditorWidget)):
                #     field_editor.editor.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            else:
                if field_editor.label:
                    field_editor.label.deleteLater()
                field_editor.label=None
            self.editors[column_name] = field_editor
            return field_editor
        return None
    
    def toggleFieldConfiguration(self, event_source):
        
        isCurrentItem = event_source == self.model_item
        self.subFrame.setVisible(isCurrentItem)
        self.isActive = isCurrentItem
        self.model_item.isActive = isCurrentItem
        if isCurrentItem:
            self.setProperty("ConfigurationEditor", "Active")
        else:
            self.setProperty("ConfigurationEditor", "ObjectModelEditorWidget")
        self.refreshUi()
        # self.parent_view.model().layoutChanged.emit()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent_module.currentItemChanged.emit(self.model_item)
        QFrame.mousePressEvent(self, event)
    
    # def sizeHint(self):
    #     if not self.isActive:
    #         minimum_size = super().minimumSizeHint()
    #         minimum_size.setHeight(minimum_size.height()*1.1)
    #         return minimum_size
    #     else:
    #         minimum_size = super().minimumSizeHint()
    #         minimum_size.setHeight(minimum_size.height()*1.3)
    #         return minimum_size

    #     return super().sizeHint()
    