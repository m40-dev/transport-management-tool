from PyQt6.QtWidgets import (QGridLayout, QStyledItemDelegate, QStyle, QToolButton, QFrame, QLabel, 
QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy, QLineEdit, QComboBox, QApplication, QGroupBox, QStyle, QWidget)
from PyQt6.QtCore import Qt, QRect, QRectF, pyqtSignal, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QSize, QMimeData, QPoint
from PyQt6.QtGui import QPalette, QPen, QPainterPath,QDrag, QColor, QBrush, QPainter, QStyleHints


from lib.ui.WidgetFactory.CustomViewDelegate import CustomDelegateWidget

class DefaultConfigurationWidget(CustomDelegateWidget):

    def __init__(self, parent_view, application, model_item, parent_module):
        super().__init__(parent_view=parent_view, application=application, model_item=model_item, parent_module=parent_module)

        self.setupUi()

    def setupUi(self):
        self.setProperty("ConfigurationEditor", "ObjectModelSampleWidget")
        self.frame.setProperty("ConfigurationEditor", "ObjectModelWidgetFrame")

        handleBar = QLabel()
        handleBar.setText("::")
        # handleBar.setProperty("ConfigurationEditor", "Handle")

        label = QLabel()
        label.setWordWrap(True)
        # description = QLabel()
        # description.setWordWrap(True)

        label.setProperty("CustomWidget", "ItemLabel")
        # description.setProperty("CustomWidget", "ItemDescription")

        label.setText(self.model_item.display)
        # description.setText(self.model_item.description)
        label.setToolTip(f"<i>{self.model_item.description}</i>")

        self.layout.addWidget(handleBar, 0, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(label, 0, 1, 1, 1)
        self.layout.setColumnStretch(1, 2)
