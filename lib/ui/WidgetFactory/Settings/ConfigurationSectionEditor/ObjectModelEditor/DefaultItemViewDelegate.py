from PyQt6.QtWidgets import (QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, 
QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy, QLineEdit, QComboBox, QApplication, QGroupBox, QStyle, QWidget)
from PyQt6.QtCore import Qt, QRect, QRectF, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QSize, QMimeData, QPoint
from PyQt6.QtGui import QPalette, QPen, QPainterPath,QDrag, QColor, QBrush, QPainter, QStyleHints


from lib.ui.WidgetFactory.DialogScreens.FormEditorDialog import FormEditorObject

class DefaultItemViewDelegate(QStyledItemDelegate):

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
            editor = DefaultConfigurationWidget(
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
                widget.isSelected = True

                target_x = option.rect.x() + ((widget.rect().width() - widget.frame.rect().width()) / 2)

                # divide by 2 to get just widget size (difference includes both margins)
                target_y = option.rect.y() + ((widget.rect().height() - widget.frame.rect().height()) / 2)
                # print(target_x, target_y)
                # target_rect = QRect(QPoint(target_x, target_y), widget.frame.size())
                target_rect = QRect(QPoint(target_x, target_y), widget.frame.size())

                selection_color = self.application.ProgramConfiguration.getColor("SelectedObjectColor")
                selection_color.setAlphaF(0.4)
                # # # Set the pen color to the selection color
                pen = QPen(selection_color)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.setBrush(selection_color)
                
                painter.drawRect(target_rect)
            else:
                widget.isSelected = False
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        if index.isValid():
            widget = self.parent().indexWidget(index)
            if widget and isinstance(widget, QWidget):
                return widget.sizeHint()
        return QSize(30, 30)

class DefaultConfigurationWidget(QFrame):

    def __init__(self, parent, configuration_item, application, configuration_editor):
        super().__init__(parent=parent)
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self.configuration_editor = configuration_editor
        self.configuration_item = configuration_item
        self.widget_data = self.ProgramConfiguration.getConfigurationParameters("ObjectModelConfiguration")
        self.listview = parent
        self.parent = parent
        self.isSelected = False
        # self.drag_start_position = None
        self.setAcceptDrops(True)

        self.setProperty("ConfigurationEditor", "ObjectModelSampleWidget")
        self.editors = {}
        self.setupUi()

        """ Refresh state based on the model data """
        self.refreshUi()
        self.animate()
        
        # self.listview.model().layoutChanged.emit()
        
    # def paintEvent(self, event):
    #     super().paintEvent(event)

    #     if self.isSelected:
    #         painter = QPainter(self)
    #         frame_geo = self.frame.geometry().getRect()
    #         widget_rect = QRect(frame_geo[0], frame_geo[1], frame_geo[2], frame_geo[3])
            
    #         selection_color = self.application.ProgramConfiguration.getColor("SelectedObjectColor")
    #         # Set the pen color to the selection color
    #         selection_color.setAlphaF(0.5)
    #         pen = QPen(selection_color)
    #         pen.setWidth(1)
    #         painter.setPen(pen)
    #         painter.setBrush(selection_color)

    #         # Set the border color of the item
    #         painter.drawRect(widget_rect)
        
    def animate(self, reverse=False):
        # animate startup
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        animation = QPropertyAnimation(self)
        animation.setPropertyName(bytes("opacity", "utf-8"))
        animation.setTargetObject(effect)
        animation.setDuration(300)
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

        if self.listview.model():
            self.listview.model().layoutChanged.emit()

    def setupUi(self):
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(1,1,1,1)
        self.main_layout.setSpacing(1)

        self.frame = QFrame()
        self.frame.setProperty("ConfigurationEditor", "ObjectModelWidgetFrame")

        self.main_layout.addWidget(self.frame, 0, 0)

        self.layout = QGridLayout(self.frame)
        self.layout.setContentsMargins(1,1,1,1)
        self.layout.setSpacing(1)

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        handleBar = QLabel()
        handleBar.setText("::")
        # handleBar.setProperty("ConfigurationEditor", "Handle")

        label = QLabel()
        label.setWordWrap(True)
        description = QLabel()
        description.setWordWrap(True)

        label.setProperty("ConfigurationEditor", "FieldLabel")
        description.setProperty("ConfigurationEditor", "FieldDescription")

        label.setText(self.configuration_item.display)
        description.setText(self.configuration_item.description)

        self.layout.addWidget(handleBar, 0, 0, 2, 1, Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(label, 0, 1, 1, 1)
        self.layout.addWidget(description, 1, 1, 1, 1)
        self.layout.setColumnStretch(1, 2)
        self.layout.setRowStretch(0, 0)
        self.layout.setRowStretch(1, 1)

        # Collapsed view
        
    def sizeHint(self):
        minimum_size = super().minimumSizeHint()
        minimum_size.setHeight(minimum_size.height()*1.3)

        return minimum_size