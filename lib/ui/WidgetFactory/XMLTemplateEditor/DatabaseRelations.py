# from PyQt6 import QtCore, QtWidgets

from PyQt6.QtCore import Qt, QMetaObject, QCoreApplication, pyqtSignal

#""" Required QT Libraries """
from PyQt6 import QtWidgets

from lib.data.DataModels.XMTemplateEditor import ObjectRelationsDataModel, RelationDataItem
from .ContextMenu import RelationContextMenu
XML_PREVIEW_TIMER = 100

class DatabaseRelations(QtWidgets.QWidget):
    relationSettingsChanged = pyqtSignal(object)
    relationResetRequested = pyqtSignal(object, int)


    def __init__(self, parent, application):
        super().__init__()

        self.application = application
        self.XMLTemplateEditor = parent
        self.current_index = None
        self.current_item = None
        self.setupUi()

        # Connect Signals
        self.ShowAllColumnsCheckBox.stateChanged.connect(self.onRelationFilterChanged)
        self.DeselectAllToolButton.clicked.connect(self.deselectAllRelations)
        self.ResetRelationsToolButton.clicked.connect(self.resetallRelations)
        self.ApplyPresetToolButton.clicked.connect(self.applyRelationPreset)
    
    def deselectAllRelations(self):
        # deselect all relations of the selected source object items
        self.relationResetRequested.emit(self.current_item, 0)

        # reset the relations model view to refresh the changes
        self.relation_data_model.layoutChanged.emit()
    
    def resetallRelations(self):
        # deselect all relations of the selected source object items
        self.relationResetRequested.emit(self.current_item, 1)

        # reset the relations model view to refresh the changes
        self.relation_data_model.layoutChanged.emit()

    def loadRelationData(self, source_index):
        source_object = None
        if source_index and source_index.isValid():
            source_object = source_index.internalPointer()
            self.current_item = source_object

        if not source_object:
            self.current_item = None
            self.current_index = None
            relation_data = {}
            self.relation_data_model.reloadModelData(relation_data, filter_state=self.getRelationsViewFilterState())
            self.loadRelationPresets()
            return False

        self.loadRelationPresets()

        relation_data = source_object.object_relations

        self.current_index = source_index
        self.current_item = source_object
        self.relation_data_model.reloadModelData(relation_data, filter_state=self.getRelationsViewFilterState())
        # self.RelationsViewTreeView.resizeColumnToContents(0)
        
    def deleteSelectedItems(self):
        if not self.RelationsViewTreeView.hasFocus():
            return False
        selected_indexes = self.RelationsViewTreeView.selectionModel().selectedRows()
        for index in selected_indexes:
            self.relation_data_model.remove_item(index)

        model_data = self.relation_data_model.getCurrentModelData()
        if self.current_item:
            self.current_item.object_relations = model_data
            self.relationSettingsChanged.emit(self.current_item)

    def relationContextMenuRequested(self, menuPosition):
        clickedIndex = self.RelationsViewTreeView.indexAt(menuPosition)
        contextMenu = RelationContextMenu(
            parent=self, 
            source_index=clickedIndex)
        contextMenu.onFollowTableRelation.connect(self.extendTableRelations)
        menu_target = self.RelationsViewTreeView.mapToGlobal(menuPosition)
        contextMenu.popup(menu_target)

    def getRelationsViewFilterState(self):
        return not self.ShowAllColumnsCheckBox.isChecked()

    def onRelationFilterChanged(self, state):
        FilterTurnedOn = (state == 0)
        self.RelationsViewTreeView.model().setFilter(FilterTurnedOn)

    def extendTableRelations(self, source_index):
        if source_index and not source_index.isValid():
            return False
        target_table = None
        source_item = source_index.internalPointer()
        
        if isinstance(source_item, RelationDataItem):
            target_table = source_item.follow_table
        
        if not target_table:
            return False

        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()

        table_relations = self.application.db.get_table_extension(target_table)
        if table_relations and len(table_relations) > 0:
            self.relation_data_model.extendTableRelations(source_index, table_relations)
            if self.current_item:
                for table_name, extended_relations in table_relations.items():
                    if table_name not in self.current_item.object_relations.keys():
                        self.current_item.object_relations.update(table_relations)
                    else:
                        # update existing table relations with NEW entries only
                        existing_relations = self.current_item.object_relations[table_name]
                        self.current_item.object_relations[table_name] = self.application.db.extend_table_relations(existing_relations, extended_relations)
        self.RelationsViewTreeView.resizeColumnToContents(0)

    def loadRelationPresets(self):
        self.RelationPresetsComboBox.clear()
        if not self.current_item:
            return False

        relation_presets = self.application.relation_presets
        table_name = self.current_item.table_name
        if relation_presets and table_name:
            table_presets = relation_presets.get(table_name, None)
            if table_presets is not None:
                for preset_name, preset_data in table_presets.items():
                    if isinstance(preset_data, dict) and "name" in preset_data.keys():
                        if preset_data["name"] != preset_name:
                            preset_name = preset_data["name"]

                    self.RelationPresetsComboBox.addItem(preset_name)
    
    def applyRelationPreset(self):
        preset_name = self.RelationPresetsComboBox.currentText()
        preset_data = None
        preset_table = None

        relation_presets = self.application.relation_presets

        for table_name, relations in relation_presets.items():
            preset_data = relations.get(preset_name, None)
            if preset_data is not None:
                preset_table = table_name
                break

        self.XMLTemplateEditor.relationPresetApplyRequested(preset_table, preset_data)
        self.loadRelationData(self.current_index)

    def relationStatusChanged(self, index=None, column_name=None, value=None):
        self.relationSettingsChanged.emit(self.current_item)
            
    def setupUi(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.SelectedObjectRelationsGroupBox = QtWidgets.QGroupBox(self)
        self.layout.addWidget(self.SelectedObjectRelationsGroupBox, 0, 0, 1, 1)
        self.SelectedObjectRelationsGroupBox.setObjectName("SelectedObjectRelationsGroupBox")
        self.GroupBoxLayout = QtWidgets.QGridLayout(self.SelectedObjectRelationsGroupBox)
        self.GroupBoxLayout.setObjectName("GroupBoxLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 3, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.RelationPresetsLabel = QtWidgets.QLabel(self.SelectedObjectRelationsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RelationPresetsLabel.sizePolicy().hasHeightForWidth())
        self.RelationPresetsLabel.setSizePolicy(sizePolicy)
        self.RelationPresetsLabel.setObjectName("RelationPresetsLabel")
        self.horizontalLayout.addWidget(self.RelationPresetsLabel)
        self.RelationPresetsComboBox = QtWidgets.QComboBox(self.SelectedObjectRelationsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RelationPresetsComboBox.sizePolicy().hasHeightForWidth())
        self.RelationPresetsComboBox.setSizePolicy(sizePolicy)
        self.RelationPresetsComboBox.setObjectName("RelationPresetsComboBox")
        self.horizontalLayout.addWidget(self.RelationPresetsComboBox)
        self.ApplyPresetToolButton = QtWidgets.QToolButton(self.SelectedObjectRelationsGroupBox)
        self.ApplyPresetToolButton.setObjectName("ApplyPresetToolButton")
        self.horizontalLayout.addWidget(self.ApplyPresetToolButton)
        
        self.optionsLayout = QtWidgets.QGridLayout()
        self.optionsLayout.setSpacing(2)
        self.optionsLayout.setObjectName("optionsLayout")

        self.ShowAllColumnsCheckBox = QtWidgets.QCheckBox(self.SelectedObjectRelationsGroupBox)
        self.ShowAllColumnsCheckBox.setObjectName("ShowAllColumnsCheckBox")
        
        self.AutoListObjectsFromDatabaseCheckBox = QtWidgets.QCheckBox(self.SelectedObjectRelationsGroupBox)
        self.AutoListObjectsFromDatabaseCheckBox.setObjectName("AutoListObjectsFromDatabaseCheckBox")
        
        self.AutoLoadCheckBox = QtWidgets.QCheckBox(self.SelectedObjectRelationsGroupBox)
        self.AutoLoadCheckBox.setObjectName("AutoLoadCheckBox")

        self.ResetRelationsToolButton = QtWidgets.QToolButton(self.SelectedObjectRelationsGroupBox)
        self.ResetRelationsToolButton.setObjectName("ResetRelationsToolButton")

        self.DeselectAllToolButton = QtWidgets.QToolButton(self.SelectedObjectRelationsGroupBox)
        self.DeselectAllToolButton.setObjectName("DeselectAllToolButton")

        self.optionsLayout.addWidget(self.AutoListObjectsFromDatabaseCheckBox, 0, 0, 1, 1)
        self.optionsLayout.addWidget(self.AutoLoadCheckBox, 1, 0, 1, 1)
        self.optionsLayout.addWidget(self.ShowAllColumnsCheckBox, 2, 0, 1, 1)

        self.optionsLayout.setColumnStretch(1, 10)

        buttonsLayout = QtWidgets.QHBoxLayout()
        buttonsLayout.setContentsMargins(-1, 3, -1, -1)
        buttonsLayout.addWidget(self.DeselectAllToolButton)
        buttonsLayout.addWidget(self.ResetRelationsToolButton)
        buttonsLayout.addStretch(3)

        self.RelationsViewTreeView = QtWidgets.QTreeView(self.SelectedObjectRelationsGroupBox)
        self.RelationsViewTreeView.setObjectName("RelationsViewTreeView")
        self.RelationsViewTreeView.setSortingEnabled(False)
        self.RelationsViewTreeView.setWordWrap(True)
        self.RelationsViewTreeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # self.RelationsViewTreeView.setHeaderHidden(True)
        self.RelationsViewTreeView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.RelationsViewTreeView.setDragEnabled(False)
        self.RelationsViewTreeView.setAcceptDrops(False)
        self.RelationsViewTreeView.customContextMenuRequested.connect(self.relationContextMenuRequested)
        self.RelationsViewTreeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        
        self.GroupBoxLayout.addLayout(self.optionsLayout, 0, 0, 1, 1)
        self.GroupBoxLayout.addLayout(buttonsLayout, 1, 0, 1, 1)
        self.GroupBoxLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.GroupBoxLayout.addWidget(self.RelationsViewTreeView, 3, 0, 1, 1)

        # Configure data model
        self.relation_data_model = ObjectRelationsDataModel(application=self.application, parent_widget=self.RelationsViewTreeView)
        self.RelationsViewTreeView.setModel(self.relation_data_model)
        self.relation_data_model.dataChanged.connect(self.relationStatusChanged)
        self.RelationsViewTreeView.header().setStretchLastSection(False)
        self.RelationsViewTreeView.header().resizeSection(0, round(self.application.width()*0.12))
        self.RelationsViewTreeView.header().resizeSection(1, 30)
        self.RelationsViewTreeView.header().resizeSection(2, 30)
        self.RelationsViewTreeView.header().resizeSection(3, 30)
        
        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)
        
    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        self.SelectedObjectRelationsGroupBox.setTitle(_translate("Form", "Object Relations"))
        self.RelationPresetsLabel.setText(_translate("Form", "Relation Presets"))
        self.ApplyPresetToolButton.setText(_translate("Form", "Apply"))
        self.ShowAllColumnsCheckBox.setText(_translate("Form", "Show All Columns"))
        self.AutoListObjectsFromDatabaseCheckBox.setText(_translate("Form", "Auto List Selected Objects from database"))
        self.DeselectAllToolButton.setText(_translate("Form", "Deselect All Relations"))
        self.ResetRelationsToolButton.setText(_translate("Form", "Reset To Initial State"))
        self.AutoLoadCheckBox.setText(_translate("Form", "Auto Load Matching Objects from database"))
        # self.RelationsViewTreeView.setSortingEnabled(True)