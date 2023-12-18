from PyQt6.QtWidgets import QGridLayout, QFrame, QGraphicsOpacityEffect, QSizePolicy, QTreeView
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QAbstractAnimation

class CustomDelegateWidget(QFrame):

    def __init__(self, parent_view, application, model_item, parent_module=None):
        super().__init__(parent=parent_view)

        # Main Properties
        self.parent = parent_view
        self.parent_view = parent_view
        self.application = application
        self.model_item = model_item
        self.parent_module = parent_module
        
        # Operational Properties
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self.isSelected = False

        # UI setup

        # Main layout is used for the overall widget setup in the parent_view 
        # including margins and other top-level styling options
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(1,1,1,1)
        self.main_layout.setSpacing(1)
        
        # Frame object is used to setup a box for the visible widget itself 
        # and paint the object selection in the CustomViewDelegate accordingly
        self.frame = QFrame(self)
        self.setProperty("CustomViewDelegate", "CustomDelegateWidget")
        self.frame.setProperty("CustomViewDelegate", "CustomDelegateWidgetFrame")

        self.main_layout.addWidget(self.frame, 0, 0)

        # This is the main layout inside the widget frame to build the custom widgets and controls of the final Custom Widget
        self.layout = QGridLayout(self.frame)
        self.layout.setContentsMargins(2, 2, 2, 2)
        
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        if isinstance(self.parent_view, QTreeView):
            self.parent_view.expanded.connect(self.expand_children)
            self.parent_view.collapsed.connect(self.collapse_children)

        # custom widget show animation
        self.animate()

    def animate(self, reverse=False):
        # animate startup
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        animation = QPropertyAnimation(self)
        animation.setPropertyName(bytes("opacity", "utf-8"))
        animation.setTargetObject(effect)
        animation.setDuration(250)
        animation.setStartValue(0)
        animation.setEndValue(1)

        if reverse:
            animation.setStartValue(1)
            animation.setEndValue(0)
            animation.setDuration(200)
        
        animation.setEasingCurve(QEasingCurve.Type.OutInCubic)
        animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def expand_children(self, index):
        if not index.isValid():
            return False
        expanded_item = index.internalPointer()

        if expanded_item != self.model_item.parent():
            return False
        self.animate()
        self.parent_view.model().layoutChanged.emit()
        
    def collapse_children(self, index):
        if not index.isValid():
            return False
        collapsed_item = index.internalPointer()

        if collapsed_item != self.model_item.parent():
            return False
        
        self.animate(reverse=True)
        self.parent_view.model().layoutChanged.emit()

    def sizeHint(self):
        preffered_size = super().minimumSizeHint()
        preffered_size.setHeight(preffered_size.height() * 1.2)
        return preffered_size