
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, Qt
from ..ConfigurationSectionEditor import ConfigurationSectionEditor
from lib.data.DataModels.Settings.ObjectConfigurationModel import ObjectConfigurationModel
from .ObjectModelEditorViewDelegate import ObjectModelEditorViewDelegate
from lib.ui.WidgetFactory import FormEditorDialog

class ObjectModelConfigurationEditor(ConfigurationSectionEditor):

    def __init__(self, application, section_name, section_source):
        super().__init__(application=application, section_name=section_name, section_source=section_source)

        # print(self._section_source.section_data)    
        self.setupEditorUi()

        #Main Object Model configuration view
        model_data = ObjectConfigurationModel(
            application=application, 
            configuration_data=section_source, 
            parent_widget=self.ObjectConfigurationListView)

        model_data.dataChanged.connect(self.configurationDataChanged)
        ConfigurationViewDelegate = ObjectModelEditorViewDelegate(
            model_data=model_data, 
            parent_widget=self.ObjectConfigurationListView,
            application=self.application, 
            configuration_editor=self)

        self.ObjectConfigurationListView.setModel(model_data)
        self.ObjectConfigurationListView.setItemDelegate(ConfigurationViewDelegate)
        
        # Pre-Configured widgets that can be used for the form  
        # config_model_data = ObjectConfigurationModel(
        #     application=application, 
        #     configuration_data=section_source, 
        #     parent_widget=self.ObjectConfigurationListView)
        # self.SourceConfigurationView.setModel(config_model_data)

    def configurationDataChanged(self):
        editor_data = self.ObjectConfigurationListView.model().exportModelData()
        self.ProgramConfiguration.updateProgramConfiguration({self._section_source.SectionName: editor_data}, sort_items=False)
        self._section_source.ConfigurationParameters = editor_data


    def setupEditorUi(self):
        self.ObjectConfigurationListView = QtWidgets.QListView(self)
        self.ObjectConfigurationListView.dragMoveEvent = self.ConfigurationViewDragMoveEvent
        # self.ObjectConfigurationListView.setHeaderHidden(True)
        self.ObjectConfigurationListView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.ObjectConfigurationListView.setDragEnabled(True)
        self.ObjectConfigurationListView.setAcceptDrops(True)
        self.ObjectConfigurationListView.setDropIndicatorShown(True)
        self.ObjectConfigurationListView.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragDrop)
        self.ObjectConfigurationListView.setAlternatingRowColors(False)
        self.ObjectConfigurationListView.setViewportMargins(2,2,2,2)
        self.ObjectConfigurationListView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.ObjectConfigurationListView.setWordWrap(True)
        self.ObjectConfigurationListView.setProperty("ConfigurationEditor", "ObjectModelListView")

        self.SourceConfigurationView = QtWidgets.QListView(self)
        self.SourceConfigurationView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.SourceConfigurationView.setDragEnabled(True)

        self.TestButton = QtWidgets.QPushButton("Test Configuration")
        self.TestButton.clicked.connect(self.TestConfiguration)
        
        ConfigurationViewSplitter = QtWidgets.QSplitter(Qt.Orientation.Horizontal)
        ConfigurationViewSplitter.addWidget(self.ObjectConfigurationListView)
        ConfigurationViewSplitter.addWidget(self.SourceConfigurationView)

        ConfigurationViewSplitter.setSizes([round(self.width()/2), round(self.width()/2)])

        #add widgets to layout

        self.editor_layout.addWidget(ConfigurationViewSplitter, 0, 0, 2, 1)
        self.layout.addWidget(self.TestButton, 1, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.editor_layout.setRowStretch(0, 10)

    def TestConfiguration(self):
        editor_data = self.ObjectConfigurationListView.model().exportModelData()
        preview = FormEditorDialog(
            application=self.application, 
            configuration_class=self._section_source.SectionName,
            dialog_name="Form Configuration Test",
            form_configuration=editor_data)
        if preview.exec():
            self.configurationDataChanged()

    def ConfigurationViewDragMoveEvent(self, event):
        move_accept = False
        source_index = event.source().currentIndex()
        source_item = source_index.internalPointer()

        QtWidgets.QListView.dragMoveEvent(self.ObjectConfigurationListView, event)
        
        drop_index = self.ObjectConfigurationListView.indexAt(event.position().toPoint())
        drop_item = drop_index.internalPointer()

        dropIndicator = self.ObjectConfigurationListView.dropIndicatorPosition()

        if drop_item:
            self.ObjectConfigurationListView.setDropIndicatorShown(True)
        else:
            move_accept = True

        if dropIndicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.OnItem:
            move_accept = False

        if dropIndicator in [QtWidgets.QAbstractItemView.DropIndicatorPosition.BelowItem, QtWidgets.QAbstractItemView.DropIndicatorPosition.AboveItem]:
            move_accept = True

        if event.mimeData().hasFormat("application/vnd.jsondataitem") and move_accept:
            event.acceptProposedAction()
        else:
            event.ignore()

    def selectedItems(self):
        selected_items = []
        if not self.ObjectConfigurationListView.selectionModel():
            return selected_items

        selected_indexes = self.ObjectConfigurationListView.selectionModel().selectedRows()
        if len(selected_indexes) > 0:
            for index in selected_indexes:
                if not index.isValid():
                    continue
                item = index.internalPointer()
                if item and item not in selected_items:
                    selected_items.append(item)
        return selected_items