
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, Qt
from ..ConfigurationSectionEditor import ConfigurationSectionEditor
from lib.data.DataModels.Settings.ObjectConfigurationModel import ObjectConfigurationModel
from .ObjectModelEditorViewDelegate import ObjectModelConfigurationWidget
# from .DefaultItemViewDelegate import DefaultItemViewDelegate
from .DefaultItemViewDelegate import DefaultConfigurationWidget
from lib.ui.WidgetFactory.CustomViewDelegate import CustomViewDelegate

from lib.ui.WidgetFactory import FormEditorDialog, MsgBox

class ObjectModelConfigurationEditor(ConfigurationSectionEditor):
    currentItemChanged = pyqtSignal(object)

    def __init__(self, application, section_name, section_source):
        super().__init__(application=application, section_name=section_name, section_source=section_source)

        # print(self._section_source.section_data)    
        self.setupEditorUi()

        #Main Object Model configuration view
        model_data = ObjectConfigurationModel(
            application=application,
            section_name=section_name,
            configuration_data=section_source.ConfigurationParameters, 
            parent_widget=self.ObjectModelConfigurationView)

        # model_data.dataChanged.connect(self.configurationDataChanged)
        
        ConfigurationViewDelegate = CustomViewDelegate(
            model_data=model_data, 
            parent_view=self.ObjectModelConfigurationView,
            application=self.application, 
            parent_module=self)
        ConfigurationViewDelegate.setCustomWidgetClass(ObjectModelConfigurationWidget)
        
        self.ObjectModelConfigurationView.setModel(model_data)
        self.ObjectModelConfigurationView.setItemDelegate(ConfigurationViewDelegate)
        
        # Pre-Configured widgets that can be used for the form  

        default_config_model_data = ObjectConfigurationModel(
            application=application, 
            section_name=section_name,
            configuration_data=section_source.DefaultConfigurationItems, 
            parent_widget=self.DefaultConfigurationView)
        self.DefaultConfigurationView.setModel(default_config_model_data)
        
        # DefaultViewDelegate = DefaultItemViewDelegate(
        #     model_data=default_config_model_data, 
        #     parent_widget=self.DefaultConfigurationView,
        #     application=self.application, 
        #     configuration_editor=self)

        DefaultViewDelegate = CustomViewDelegate(
            model_data=default_config_model_data, 
            parent_view=self.DefaultConfigurationView,
            application=self.application, 
            parent_module=self)

        DefaultViewDelegate.setCustomWidgetClass(DefaultConfigurationWidget)
        
        self.DefaultConfigurationView.setItemDelegate(DefaultViewDelegate)

        configuration_section = self.ProgramConfiguration.getConfigurationSection("ObjectModelConfiguration")
        config_sample_data = configuration_section.get("ConfigurationSamples", {})

        configuration_samples_model = ObjectConfigurationModel(
            application=application, 
            section_name=section_name,
            configuration_data=config_sample_data, 
            parent_widget=self.ConfigurationSamplesView)
        
        self.ConfigurationSamplesView.setModel(configuration_samples_model)

        SamplesViewDelegate = CustomViewDelegate(
            model_data=configuration_samples_model, 
            parent_view=self.ConfigurationSamplesView,
            application=self.application, 
            parent_module=self)
        SamplesViewDelegate.setCustomWidgetClass(DefaultConfigurationWidget)
        
        self.ConfigurationSamplesView.setItemDelegate(SamplesViewDelegate)

    def configurationDataChanged(self):
        editor_data = self.ObjectModelConfigurationView.model().exportModelData()
        self.ProgramConfiguration.updateProgramConfiguration({self._section_source.SectionName: editor_data}, sort_items=False)
        self._section_source.ConfigurationParameters = editor_data

    def TestConfiguration(self):
        editor_data = self.ObjectModelConfigurationView.model().exportModelData()
        preview = FormEditorDialog(
            application=self.application, 
            configuration_class=self._section_source.SectionName,
            dialog_name="Form Configuration Test",
            form_configuration=editor_data)
        if preview.exec():
            pass
     
    def ApplyConfiguration(self):
        self.configurationDataChanged()
        self.ProgramConfiguration.saveConfiguration(self.section_source.TargetConfigurationFile)

        # info = QtWidgets.QMessageBox(
        #     QtWidgets.QMessageBox.Icon.Information, 
        #     "Configuration Applied", 
        #     "Object model configuration applied.")
        # info.exec()

        MsgBox(
            application=self.application,
            window_mode=MsgBox.INFO,
            window_title="Configuration Saved",
            message="Program Configuration saved."
        ).exec()

    def setupEditorUi(self):
        self.ObjectModelConfigurationView = QtWidgets.QListView(self)
        self.ObjectModelConfigurationView.dragMoveEvent = self.ConfigurationViewDragMoveEvent
        self.ObjectModelConfigurationView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.ObjectModelConfigurationView.setDragEnabled(True)
        self.ObjectModelConfigurationView.setAcceptDrops(True)
        self.ObjectModelConfigurationView.setDropIndicatorShown(True)
        self.ObjectModelConfigurationView.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragDrop)
        self.ObjectModelConfigurationView.setAlternatingRowColors(False)
        self.ObjectModelConfigurationView.setViewportMargins(2,2,2,2)
        self.ObjectModelConfigurationView.setWordWrap(True)
        self.ObjectModelConfigurationView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.ObjectModelConfigurationView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ObjectModelConfigurationView.setProperty("ConfigurationEditor", "ObjectModelListView")

        TestButton = QtWidgets.QToolButton(self)
        TestButton.setText("Test Configuration")

        TestButton.clicked.connect(self.TestConfiguration)

        ApplyButton = QtWidgets.QToolButton(self)
        ApplyButton.setText("Apply and Save")
        ApplyButton.clicked.connect(self.ApplyConfiguration)


        view_Label = QtWidgets.QLabel("Object Data Fields Configuration")
        view_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        view_Label.setProperty("ConfigurationEditor", "ListViewHeader")
        configuration_view = QtWidgets.QWidget(self)
        configuration_layout = QtWidgets.QVBoxLayout(configuration_view)
        configuration_layout.setSpacing(2)
        configuration_layout.setContentsMargins(1,1,1,1)

        configuration_layout.addWidget(view_Label)
        configuration_layout.addWidget(self.ObjectModelConfigurationView)

        mandatory_fields_Label = QtWidgets.QLabel("Default Fields for this class")
        mandatory_fields_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mandatory_fields_Label.setProperty("ConfigurationEditor", "ListViewHeader")
        
        default_configuration_view = QtWidgets.QWidget(self)
        default_configuration_layout = QtWidgets.QVBoxLayout(default_configuration_view)
        default_configuration_layout.setSpacing(2)
        default_configuration_layout.setContentsMargins(1,1,1,1)

        default_configuration_layout.addWidget(mandatory_fields_Label)

        self.DefaultConfigurationView = QtWidgets.QListView(self)
        self.DefaultConfigurationView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.DefaultConfigurationView.setDragEnabled(True)
        self.DefaultConfigurationView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.DefaultConfigurationView.setAlternatingRowColors(False)
        self.DefaultConfigurationView.setViewportMargins(2,2,2,2)
        # self.DefaultConfigurationView.setWordWrap(True)
        self.DefaultConfigurationView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.DefaultConfigurationView.setProperty("ConfigurationEditor", "ObjectModelListView")

        default_configuration_layout.addWidget(self.DefaultConfigurationView)

        configuration_prebuilds_label = QtWidgets.QLabel("Object Model Standard Fields")
        configuration_prebuilds_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        configuration_prebuilds_label.setProperty("ConfigurationEditor", "ListViewHeader")

        default_configuration_layout.addWidget(configuration_prebuilds_label)

        self.ConfigurationSamplesView = QtWidgets.QListView(self)
        self.ConfigurationSamplesView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.ConfigurationSamplesView.setDragEnabled(True)
        self.ConfigurationSamplesView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.ConfigurationSamplesView.setAlternatingRowColors(False)
        self.ConfigurationSamplesView.setViewportMargins(2,2,2,2)
        # self.ConfigurationSamplesView.setWordWrap(True)
        self.ConfigurationSamplesView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ConfigurationSamplesView.setProperty("ConfigurationEditor", "ObjectModelListView")
        # self.ConfigurationSamplesView.setUniformItemSizes(False)


        default_configuration_layout.addWidget(self.ConfigurationSamplesView)
        
        ConfigurationViewSplitter = QtWidgets.QSplitter(Qt.Orientation.Horizontal)
        ConfigurationViewSplitter.addWidget(configuration_view)
        ConfigurationViewSplitter.addWidget(default_configuration_view)

        ConfigurationViewSplitter.setSizes([round(self.width()*0.6), round(self.width()*0.4)])

        #add widgets to layout

        self.editor_layout.addWidget(ConfigurationViewSplitter, 0, 0, 2, 1)
        self.layout.addWidget(TestButton, 1, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(ApplyButton, 1, 3, 1, 1, Qt.AlignmentFlag.AlignRight)
        self.layout.setColumnStretch(1, 10)
        self.editor_layout.setRowStretch(0, 10)

    def ConfigurationViewDragMoveEvent(self, event):
        move_accept = False
        source_index = event.source().currentIndex()
        source_item = source_index.internalPointer()

        QtWidgets.QListView.dragMoveEvent(self.ObjectModelConfigurationView, event)
        
        drop_index = self.ObjectModelConfigurationView.indexAt(event.position().toPoint())
        drop_item = drop_index.internalPointer()

        dropIndicator = self.ObjectModelConfigurationView.dropIndicatorPosition()

        if drop_item:
            self.ObjectModelConfigurationView.setDropIndicatorShown(True)
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
        if not self.ObjectModelConfigurationView.selectionModel():
            return selected_items

        selected_indexes = self.ObjectModelConfigurationView.selectionModel().selectedRows()
        if len(selected_indexes) > 0:
            for index in selected_indexes:
                if not index.isValid():
                    continue
                item = index.internalPointer()
                if item and item not in selected_items:
                    selected_items.append(item)
        return selected_items