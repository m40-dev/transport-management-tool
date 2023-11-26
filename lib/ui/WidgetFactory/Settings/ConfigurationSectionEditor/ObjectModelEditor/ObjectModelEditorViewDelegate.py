from PyQt6.QtWidgets import (QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, 
QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy, QLineEdit, QComboBox, QApplication, QGroupBox,
QWidget)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QSize, QMimeData
from PyQt6.QtGui import QPalette, QPen, QPainterPath,QDrag, QColor, QBrush


from lib.ui.WidgetFactory.DialogScreens.FormEditorDialog import FormEditorObject

class ObjectModelEditorViewDelegate(QStyledItemDelegate):

    def __init__(self, parent_widget, model_data, application, configuration_editor):
        super().__init__(parent_widget)
        # self.items = ["", "Import", "Export"]
        self.model_data = model_data
        self.application = application
        self.configuration_editor = configuration_editor
        self.application_palette = self.application.color_theme    
    
    def createEditor(self, parent, option, index):
        if not index.isValid():
            return False
        # column_name = self.model_data.headerData(index.column())
        configuration_item = index.internalPointer()
        # print("create editor for column", column_name, item, item.task_class)

        if configuration_item:
            editor = ObjectModelConfigurationWidget(
                configuration_item=configuration_item, 
                application=self.application, 
                parent=self.parent(), 
                configuration_editor=self.configuration_editor)
            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if not index.isValid():
            return False
            
        # column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()
        
        if item:
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

        # column_name = self.model_data.headerData(index.column())
        item = index.internalPointer()

        if item:
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
                selection_color = self.application_palette.color(QPalette.ColorRole.Highlight)
                if selection_color:
                    selection_color.setAlphaF(0.3)
                # Set the pen color to the selection color
                pen = QPen(selection_color)
                pen.setWidth(3)
                painter.setPen(pen)
                # painter.setBrush(selection_color)
                painter.save()

                # Set the border color of the item
                painter.drawRoundedRect(option.rect, 4.0, 4.0, Qt.SizeMode.AbsoluteSize)
                # Fill the rounded rectangle with the brush
                painter_path = QPainterPath()
                rectf = QRectF(option.rect)
                painter_path.addRoundedRect(rectf, 4.0, 4.0)

                painter.fillPath(painter_path, painter.brush())
                painter.restore()
        else:
            super().paint(painter, option, index)
    
    def paintEvent(self, option, index):
        print(option, index)
        QStyledItemDelegate.paintEvent(self, option, index)

    def sizeHint(self, option, index):
        if index.isValid():
            widget = self.parent().indexWidget(index)
            if widget and isinstance(widget, QWidget):
                return widget.sizeHint()
        return QSize(70, 70)

class ObjectModelConfigurationWidget(QFrame):

    def __init__(self, parent, configuration_item, application, configuration_editor):
        super().__init__(parent=parent)
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self.configuration_editor = configuration_editor
        self.configuration_item = configuration_item
        self.widget_data = self.ProgramConfiguration.getConfigurationParameters("ObjectModelConfiguration")
        self.listview = parent
        self.parent = parent
        self.isActive = configuration_item.isActive
        # self.drag_start_position = None
        self.setAcceptDrops(True)

        self.setProperty("ConfigurationEditor", "ObjectModelItemWidget")
        self.editors = {}
        self.setupUi()

        """ Refresh state based on the model data """
        self.refreshUi()
        self.animate()
        
        self.listview.model().layoutChanged.emit()
        self.configuration_item.data_changed.connect(self.refreshUi)
        self.configuration_editor.currentItemChanged.connect(self.toggleFieldConfiguration)
        if self.isActive:
            self.configuration_editor.currentItemChanged.emit(self.configuration_item)

    def animate(self, reverse=False):
        # animate startup
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        animation = QPropertyAnimation(self)
        animation.setPropertyName(bytes("opacity", "utf-8"))
        animation.setTargetObject(effect)
        animation.setDuration(400)
        animation.setStartValue(0)
        animation.setEndValue(1)
        if reverse:
            animation.setStartValue(1)
            animation.setEndValue(0)
            animation.setDuration(200)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        return animation

    def refreshUi(self):
        #UI refresh
        self.setStyleSheet(self.application.color_theme.style_sheet)

        #Attributes refresh - configure editors activity
        self.deactivateEditors()

        if self.listview.model():
            self.listview.model().layoutChanged.emit()

    def deactivateEditors(self):
        for column, editor in self.editors.items():
            field_configuration = self.widget_data.get(column, None)
            field_dependencies = field_configuration.get("EditDependency", None)
            
            if field_dependencies:
                isEditable = True
                for dependency_column_name, dependency_column_value in field_dependencies.items():
                    configuration_item_data = self.configuration_item.data(dependency_column_name)
                    if configuration_item_data != dependency_column_value:
                        isEditable = False
                    if isinstance(dependency_column_value, list) and configuration_item_data in dependency_column_value:
                        isEditable = True
                    
                editor.setVisible(isEditable)
                # print(column, "field dependencies", field_dependencies, "is Editable", isEditable)

    def updateConfigurationItem(self, column, value):
        self.configuration_item.setData(column, value)
        self.configuration_editor.configurationDataChanged()

    def setupUi(self):
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(2,2,2,2)
        self.layout.setSpacing(4)

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.handleBar = QLabel(self)
        self.handleBar.setText("::")
        self.handleBar.setProperty("ConfigurationEditor", "Handle")

        self.layout.addWidget(self.handleBar, 0, 0, 3, 1)

        # Collapsed view
        self.addToFormLayout(self.layout,"FieldId", 0, 1)
        self.addToFormLayout(self.layout,"Display", 1, 1)
        self.addToFormLayout(self.layout,"IsMandatory", 0, 3)
        self.addToFormLayout(self.layout,"ShowInEditor", 1, 3)

        #Extended view
        self.subFrame = QGroupBox("Field Configuration Options", self)
        self.subFrame.setProperty("ConfigurationEditor", "FieldConfigurationFrame")
        self.subFrame.setVisible(False)

        self.layout.addWidget(self.subFrame, 2, 1, 1, 4)
        self.layout.setRowStretch(2, 1)

        subFrameLayout = QGridLayout(self.subFrame)
        
        subFrameLayout.setContentsMargins(2,15,2,2)
        subFrameLayout.setSpacing(4)

        # subFrameLayout.setColumnStretch(7, 1)
        # Default property values setting

        self.addToFormLayout(subFrameLayout, "FieldType", 0, 0)
        self.addToFormLayout(subFrameLayout, "FieldRole", 1, 0)
        self.addToFormLayout(subFrameLayout, "DefaultValue", 0, 2, 1, 2)
        self.addToFormLayout(subFrameLayout, "PlaceholderText", 1, 2, 1, 2)

        self.addToFormLayout(subFrameLayout, "IsForDataExport", 2, 0)
        self.addToFormLayout(subFrameLayout, "ShowInTreeView", 2, 2)

        deleteItemButton = QToolButton(self)
        deleteItemButton.setText("[ X ]")
        deleteItemButton.setProperty("ToolButton", "DeleteItem")
        deleteItemButton.clicked.connect(self.removeItem)
        subFrameLayout.addWidget(deleteItemButton, 2, 4)

        self.addToFormLayout(subFrameLayout, "Description", 3, 0, 1, 4)

        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.HLine)
        subFrameLayout.addWidget(separator, 4, 0, 1, 5)
        separator.setProperty("FieldConfigurationFrame", "Separator")

        #Add field specific editors
        fieldSpecificLayout = QGridLayout()
        fieldSpecificLayout.setContentsMargins(0,0,0,0)
        fieldSpecificLayout.setSpacing(3)

        subFrameLayout.addLayout(fieldSpecificLayout, 5, 0, 1, 5)

        #Dynamically load editor widgets into the subframe layout
        default_fields = ["FieldId", "Display", "IsMandatory", "ShowInEditor", "FieldType",
        "FieldRole", "DefaultValue", "PlaceholderText", "IsForDataExport", "ShowInTreeView", "Description"]

        row = 0
        for column_name in self.widget_data.keys():
            if column_name not in default_fields:
                self.addToFormLayout(fieldSpecificLayout, column_name, row, 0)
                row += 1

        # #Integer input mode controls
        # self.addToFormLayout(fieldSpecificLayout, "MinValue", row, 0)
        # self.addToFormLayout(fieldSpecificLayout, "MaxValue", row, 2)

        
        # row +=1
        # self.addToFormLayout(fieldSpecificLayout, "DistributeEvenly", row, 0)

        # row +=1
        # #File selection Modes
        # self.addToFormLayout(fieldSpecificLayout, "FileSelectionMode", row, 0)
        # row +=1

        # self.addToFormLayout(fieldSpecificLayout, "RedirectDirectoryStatic", row, 0)
        # row +=1

        # self.addToFormLayout(fieldSpecificLayout, "RedirectDirectoryDynamic", row, 0)

        # row += 1
        # self.addToFormLayout(fieldSpecificLayout, "RedirectDirectoryRelativeTo", row, 0)

        # #Object References
        # row += 1
        # self.addToFormLayout(fieldSpecificLayout, "Class", row, 0)
        # row += 1
        # self.addToFormLayout(fieldSpecificLayout, "MapValueFromParent", row, 0)

        # self.addToFormLayout(fieldSpecificLayout, "MapColumnName", row, 2)

        # #List property configuration
        # row += 1
        # self.addToFormLayout(fieldSpecificLayout, "Separator", row, 0)

        # row += 1
        # self.addToFormLayout(fieldSpecificLayout, "Options", row, 0, 2)
        fieldSpecificLayout.setRowStretch(row, 1)
        fieldSpecificLayout.setColumnStretch(1, 2)
        
        # subFrameLayout.setRowStretch(subFrameLayout.rowCount(), 1)
        self.listview.model().layoutChanged.emit()

    def removeItem(self):
        animation = self.animate(True)
        animation.finished.connect(lambda: self.listview.model().removeItems([self.configuration_item]))

    def addToFormLayout(self, layout, column_name, row, column, rowSpan=1, colSpan=1):
        current_value = self.configuration_item.data(column_name, None)
        
        field_configuration = self.widget_data.get(column_name, None)
        if field_configuration:
            if current_value is None and "DefaultValue" in field_configuration.keys():
                current_value = field_configuration["DefaultValue"]
                self.configuration_item.setData(column_name, current_value)
                
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
            else:
                if field_editor.label:
                    field_editor.label.deleteLater()
                field_editor.label=None
            self.editors[column_name] = field_editor
            return field_editor
        return None
    
    def toggleFieldConfiguration(self, event_source):
        
        isCurrentItem = event_source == self.configuration_item
        self.subFrame.setVisible(isCurrentItem)
        self.isActive = isCurrentItem
        self.configuration_item.isActive = isCurrentItem
        if isCurrentItem:
            self.setProperty("ConfigurationEditor", "Active")
        else:
            self.setProperty("ConfigurationEditor", "ObjectModelItemWidget")
        self.refreshUi()
        # self.listview.model().layoutChanged.emit()

    def mousePressEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.configuration_editor.currentItemChanged.emit(self.configuration_item)
        QFrame.mousePressEvent(self, event)
    
    