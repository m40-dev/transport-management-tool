from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QWidget
from PyQt6.QtCore import QRect, QPoint, QSize
from PyQt6.QtGui import QPen, QPainter, QPaintDevice

from .CustomDelegateWidget import CustomDelegateWidget

class CustomViewDelegate(QStyledItemDelegate):

    def __init__(self, model_data, application, parent_view, parent_module=None):
        super().__init__(parent_view)

        self.model_data = model_data
        self.application = application
        self.parent_module = parent_module
        self.parent_view = parent_view
        self._custom_widget_class = CustomDelegateWidget

    def setCustomWidgetClass(self, customWidgetClass):
        self._custom_widget_class = customWidgetClass
        
    def createEditor(self, parent, option, index):
        if not index.isValid():
            return False
        # column_name = self.model_data.headerData(index.column())
        model_item = index.internalPointer()
        # print("create editor for column", column_name, item, item.task_class)
        if index.column() == 0:
            editor = self._custom_widget_class(
                parent_view=self.parent_view, 
                application=self.application, 
                model_item=model_item, 
                parent_module=self.parent_module)
            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        if not index.isValid():
            return False
        
        if index.column() == 0:
            viewport = self.parent_view.viewport()
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

        if index.column() == 0:
            widget = self.parent_view.indexWidget(index)
            if not widget:
                widget = self.createEditor(self.parent_view, option, index)
                self.setEditorData(widget, index)
                self.parent_view.setIndexWidget(index, widget)
                widget.setGeometry(option.rect)
            else:
                widget.setGeometry(option.rect)
            
            # Check if the item is selected
            if option.state & QStyle.StateFlag.State_Selected:
                widget.isSelected = True

                # divide by 2 to get just widget size (size offset includes both margins)
                widget_width_offset = (widget.rect().width() - widget.frame.rect().width()) / 2
                widget_height_offset = (widget.rect().height() - widget.frame.rect().height()) / 2

                target_x = round(option.rect.x() + widget_width_offset)
                target_y = round(option.rect.y() + widget_height_offset)

                target_rect = QRect(QPoint(target_x, target_y), widget.frame.size())

                selection_color = self.application.ProgramConfiguration.getColor("SelectedObjectColor")

                pen = QPen(selection_color)
                pen.setWidth(3)

                # painter = QPainter(self)
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