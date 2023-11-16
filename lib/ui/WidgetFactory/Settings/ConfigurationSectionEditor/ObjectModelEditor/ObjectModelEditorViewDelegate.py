from PyQt6.QtWidgets import QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy, QLineEdit, QComboBox
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QSize
from PyQt6.QtGui import QPalette, QPen, QPainterPath

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
    
    # def sizeHint(self, option, index):
    #     return QSize(150, 50)

class ObjectModelConfigurationWidget(QFrame):

    def __init__(self, parent, configuration_item, application, configuration_editor):
        super().__init__(parent=parent)
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self.configuration_editor = configuration_editor
        self.configuration_item = configuration_item
        self.widget_data = self.ProgramConfiguration.getConfigurationParameters("ObjectModelConfigurationWidget")
        self.listview = parent
        self.parent = parent

        self.setProperty("ConfigurationEditor", "ObjectModelItemWidget")
        
        self.setupUi()

        """ Refresh state based on the model data """
        self.refreshUi()
        self.animate()

        self.configuration_item.data_changed.connect(self.refreshUi)

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
        
    def refreshUi(self):
        #UI refresh
        self.setStyleSheet(self.styleSheet())

        #Attributes refresh
        configuration_key = self.configuration_item.configuration_key

        self.entry_key.setText(configuration_key)
        self.listview.model().layoutChanged.emit()

    def updateConfigurationItem(self, column, value):
        self.configuration_item.setData(column, value)
        self.configuration_editor.configurationDataChanged()

    def setupUi(self):
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSpacing(1)

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        self.entry_key_label = QLabel("<b>Field Id:</b>")
        self.entry_key = QLineEdit(self)
        self.entry_key.textChanged.connect(
                lambda value, column="configuration_key": 
                self.updateConfigurationItem(column, value)
                )

        self.layout.addWidget(self.entry_key_label, 0, 0, 1, 1)
        self.layout.addWidget(self.entry_key, 0, 1, 1, 1)

        self.addToFormLayout("FieldType", 1, 0)
        self.addToFormLayout("FieldRole", 2, 0)
        self.addToFormLayout("DefaultValue", 3, 0)
        self.addToFormLayout("PlaceholderText", 4, 0)

        self.addToFormLayout("IsMandatory", 0, 2)
        self.addToFormLayout("ShowInEditor", 1, 2)
        self.addToFormLayout("ShowInTreeView", 2, 2)
        
        self.listview.model().layoutChanged.emit()
    
    def addToFormLayout(self, column_name, row, column):
        current_value = self.configuration_item.data(column_name, "")
        field_configuration = self.widget_data.get(column_name, None)
        if field_configuration:
            field_editor = FormEditorObject(
                application=self.application,
                column_name=column_name,
                column_configuration=field_configuration)
            
            if field_editor.editor:
                self.layout.addWidget(field_editor.label, row, column, 1, 1)
                # if field_editor.isMandatory:
                #     column+=1
                #     self.layout.addWidget(field_editor.MandatoryLabel, row, column)
                column+=1
                self.layout.addWidget(field_editor.editor, row, column, 1, 1)
                
                if current_value:
                    field_editor.set_editor_data(current_value)

                field_editor.dataChanged.connect(self.updateConfigurationItem)

                field_editor.label.setProperty("ConfigurationEditor", "PropertyLabel")
                field_editor.editor.setProperty("ConfigurationEditor", "PropertyEditor")
        

        

    