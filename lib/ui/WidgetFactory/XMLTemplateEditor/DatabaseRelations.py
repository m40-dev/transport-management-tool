# from PyQt6 import QtCore, QtWidgets

from PyQt6.QtCore import Qt, QMetaObject, QCoreApplication

#""" Required QT Libraries """
from PyQt6 import QtWidgets

XML_PREVIEW_TIMER = 100

class DatabaseRelations(QtWidgets.QWidget):

    def __init__(self, parent, application):
        super().__init__()

        self.application = application
        self.XMLTemplateEditor = parent
        self.setupUi()

    def load_table_relations(self, relations, source_widget_item, append_to_existing_widget=None):
        if append_to_existing_widget is None:
            self.XMLTemplateEditor.RelationsViewTreeWidget.clear()

        tree_widgets = {}
        if relations is None:
            return False
        
        for relation in relations:
            parent_table_name = relation["ParentTable"]
            child_table_name = relation["ChildTable"]

            ui_parent_table_name = child_table_name

            if parent_table_name == child_table_name and child_table_name != source_widget_item.table_name:
            # if parent_table_name == source_widget_item.table_name:
                ui_parent_table_name = parent_table_name

            if ui_parent_table_name == source_widget_item.table_name and append_to_existing_widget is not None:
                """ skip relations referenced to the base table of the object """
                continue
            
            child_widget = TE_RelationColumn_TreeWidgetItem(self.XMLTemplateEditor, self.application, relation, source_widget_item=source_widget_item)
            
            if append_to_existing_widget is not None and ui_parent_table_name == append_to_existing_widget.follow_table:
                if ui_parent_table_name not in tree_widgets.keys():
                    tree_widgets[ui_parent_table_name] = append_to_existing_widget

            if ui_parent_table_name not in tree_widgets.keys():
                table_info = ui_parent_table_name
                if self.application.db:
                    table_info = self.application.db.table_info.get(ui_parent_table_name, ui_parent_table_name)
                parent_widget = TE_Table_TreeWidgetItem(self.XMLTemplateEditor, self.application, table_info, source_widget_item=source_widget_item)
                tree_widgets[ui_parent_table_name] = parent_widget
            else:
                parent_widget = tree_widgets[ui_parent_table_name]

            """ Connect main application signals """
            self.XMLTemplateEditor.ShowAllColumnsCheckBox.stateChanged.connect(child_widget.show_relation)
            # self.SelectWithDatabaseModelCheckBox.stateChanged.connect(child_widget.select_relations_using_db_model)

            parent_widget.addChild(child_widget)
            # child_widget.show_relation(self.XMLTemplateEditor.ShowAllColumnsCheckBox.isChecked())

        for parent_widget in tree_widgets.values():
            if parent_widget.childCount() > 0:
                if isinstance(append_to_existing_widget, TemplateEditorTreeWidgetItem):
                    append_to_existing_widget.addChild(parent_widget)
                    continue
                self.XMLTemplateEditor.RelationsViewTreeWidget.addTopLevelItem(parent_widget)

        self.XMLTemplateEditor.RelationsViewTreeWidget.sortItems(0, Qt.SortOrder.AscendingOrder)

        self.XMLTemplateEditor.ShowAllColumnsCheckBox.stateChanged.emit(int(self.XMLTemplateEditor.ShowAllColumnsCheckBox.isChecked()))

        table_widget = tree_widgets.get(source_widget_item.table_name, None)

        if isinstance(table_widget, TE_Table_TreeWidgetItem):
            table_widget.setExpanded(True)

    """ Relations Management """
    def relationContextMenuRequested(self, menuPosition):
        clickedItem = self.XMLTemplateEditor.RelationsViewTreeWidget.itemAt(menuPosition)
        if clickedItem:
            contextMenu = RelationContextMenu(self, clickedItem)
            contextMenu.follow_table_relations.connect(self.follow_table_relation)
            menu_target = self.XMLTemplateEditor.RelationsViewTreeWidget.mapToGlobal(menuPosition)
            contextMenu.popup(menu_target)

    def get_table_initial_relations(self, table_name, extended_view=False):
        initial_relations = copy.deepcopy(self.application.db.table_relations.get(table_name, None))
        
        if initial_relations is None:
            return []
        get_extended_view = extended_view 
        if not get_extended_view:
            return initial_relations

        relation_tables = []

        for relation in initial_relations:
            child_table = relation.get("ChildTable", None)
            if child_table is not None:
                if child_table != table_name and child_table not in relation_tables:
                    relation_tables.append(child_table)
            
        for relation_table in relation_tables:
            new_table_relations = self.application.db.table_relations.get(relation_table, None)
            if new_table_relations is not None:
                initial_relations = self.extend_table_relations(initial_relations, new_table_relations)

        return initial_relations

    def deselect_all_relations(self):
        list_widgets = [self.XMLTemplateEditor.XMLStructureTreeWidget, self.XMLTemplateEditor.SearchResultsListWidget]
        select_element = None
        for selected_widget in list_widgets:
            if self.XMLTemplateEditor.last_widget_clicked == selected_widget:
                for element in selected_widget.selectedItems():
                    if isinstance(element, (TE_ObjectContainer_TreeWidgetItem, TemplateEditorListWidgetItem)):
                        element.set_all_relations_state(0)
                        select_element = element

        if select_element is not None:
            self.XMLTemplateEditor.select_source_object(select_element)

    def save_relation_preset(self, source_widget_item):
        relation_dialog = RelationPresetDialog(self.application)
        if isinstance(source_widget_item, TE_ObjectContainer_TreeWidgetItem):
            relation_dialog.relations = copy.deepcopy(source_widget_item.object_relations)

        if relation_dialog.exec():
            preset_dict = {relation_dialog.name: relation_dialog.preset_data}
            if source_widget_item.table_name not in self.relation_presets.keys():
                self.relation_presets[source_widget_item.table_name] = preset_dict

            if relation_dialog.name not in self.relation_presets[source_widget_item.table_name].keys():
                self.relation_presets[source_widget_item.table_name][relation_dialog.name] = relation_dialog.preset_data
            else:
                """ overwrite existing? """
                self.relation_presets[source_widget_item.table_name][relation_dialog.name] = relation_dialog.preset_data

        self.application.settings.setValue("relation_presets", self.relation_presets)

    def load_table_relation_presets(self, table_name):
        self.XMLTemplateEditor.RelationPresetsComboBox.clear()

        table_presets = self.relation_presets.get(table_name, None)
        if table_presets is not None:
            for preset_name, preset_data in table_presets.items():
                self.XMLTemplateEditor.RelationPresetsComboBox.addItem(preset_name)
    
    def apply_table_relation_preset(self):
        preset_name = self.XMLTemplateEditor.RelationPresetsComboBox.currentText()
        preset_data = None
        preset_table = None
        for table_name, relations in self.relation_presets.items():
            preset_data = relations.get(preset_name, None)
            if preset_data is not None:
                preset_table = table_name
                break
    
        if preset_data:
            if self.XMLTemplateEditor.last_widget_clicked == self.XMLTemplateEditor.XMLStructureTreeWidget:
                for element in self.XMLTemplateEditor.XMLStructureTreeWidget.selectedItems():
                    if isinstance(element, TE_ObjectContainer_TreeWidgetItem) and element.table_name == preset_table:
                        preset_data_relations = copy.deepcopy(preset_data["table_relations"])
                        element.set_object_relations(preset_data_relations)
                        self.XMLTemplateEditor.select_source_object(element)
            
            if self.XMLTemplateEditor.last_widget_clicked == self.XMLTemplateEditor.SearchResultsListWidget:
                for element in self.XMLTemplateEditor.SearchResultsListWidget.selectedItems():
                    if isinstance(element, TemplateEditorListWidgetItem) and element.table_name == preset_table:
                        preset_data_relations = copy.deepcopy(preset_data["table_relations"])
                        element.set_object_relations(preset_data_relations)
                        self.XMLTemplateEditor.select_source_object(element)

    def follow_table_relation(self, relation_widget):
        if relation_widget.follow_table:
            source_widget_item_relations = relation_widget.source_widget_item.object_relations
            new_relations = copy.deepcopy(self.application.db.table_relations.get(
                relation_widget.follow_table, 
                None))

            if new_relations is not None:
                merged_relations = self.extend_table_relations(
                    current_relations=source_widget_item_relations, 
                    new_relations=new_relations)
                
                relation_widget.source_widget_item.object_relations = merged_relations

                if isinstance(relation_widget.source_widget_item, 
                              TemplateEditorTreeWidgetItem):
                    relation_widget.source_widget_item.refresh()
                self.load_table_relations(
                    relations=new_relations, 
                    source_widget_item=relation_widget.source_widget_item, 
                    append_to_existing_widget=relation_widget)

    def extend_table_relations(self, current_relations, new_relations):
        current = current_relations

        new = new_relations
        if new is None:
            return current
        
        for relation in new:
            check = next((current_item for current_item in current 
                          if current_item["ParentTable"] == relation["ParentTable"] 
                          and current_item["ChildTable"] == relation["ChildTable"]), 
                          None)
            if check is None:
                current.append(relation)
            else:
                continue
        return current

    def setupUi(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.SelectedObjectRelationsGroupBox = QtWidgets.QGroupBox(self)
        self.layout.addWidget(self.SelectedObjectRelationsGroupBox, 0, 0, -1, -1)
        self.SelectedObjectRelationsGroupBox.setObjectName("SelectedObjectRelationsGroupBox")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.SelectedObjectRelationsGroupBox)
        self.gridLayout_4.setObjectName("gridLayout_4")
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
        self.gridLayout_4.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSpacing(2)
        self.formLayout.setObjectName("formLayout")
        self.SelectWithDatabaseModelCheckBox = QtWidgets.QCheckBox(self.SelectedObjectRelationsGroupBox)
        self.SelectWithDatabaseModelCheckBox.setChecked(True)
        self.SelectWithDatabaseModelCheckBox.setObjectName("SelectWithDatabaseModelCheckBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.SelectWithDatabaseModelCheckBox)
        self.DeleteResidualCheckBox = QtWidgets.QCheckBox(self.SelectedObjectRelationsGroupBox)
        self.DeleteResidualCheckBox.setToolTipDuration(3)
        self.DeleteResidualCheckBox.setObjectName("DeleteResidualCheckBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.DeleteResidualCheckBox)
        self.ShowAllColumnsCheckBox = QtWidgets.QCheckBox(self.SelectedObjectRelationsGroupBox)
        self.ShowAllColumnsCheckBox.setObjectName("ShowAllColumnsCheckBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.ShowAllColumnsCheckBox)
        self.AutoListObjectsFromDatabaseCheckBox = QtWidgets.QCheckBox(self.SelectedObjectRelationsGroupBox)
        self.AutoListObjectsFromDatabaseCheckBox.setObjectName("AutoListObjectsFromDatabaseCheckBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.AutoListObjectsFromDatabaseCheckBox)
        self.DeselectAllToolButton = QtWidgets.QToolButton(self.SelectedObjectRelationsGroupBox)
        self.DeselectAllToolButton.setObjectName("DeselectAllToolButton")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.DeselectAllToolButton)
        self.AutoLoadCheckBox = QtWidgets.QCheckBox(self.SelectedObjectRelationsGroupBox)
        self.AutoLoadCheckBox.setObjectName("AutoLoadCheckBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.AutoLoadCheckBox)
        self.gridLayout_4.addLayout(self.formLayout, 0, 0, 1, 1)
        self.RelationsViewTreeWidget = QtWidgets.QTreeWidget(self.SelectedObjectRelationsGroupBox)
        self.RelationsViewTreeWidget.setProperty("showDropIndicator", False)
        self.RelationsViewTreeWidget.setDragEnabled(False)
        self.RelationsViewTreeWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.NoDragDrop)
        self.RelationsViewTreeWidget.setAlternatingRowColors(True)
        self.RelationsViewTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.RelationsViewTreeWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.RelationsViewTreeWidget.setAutoExpandDelay(-1)
        self.RelationsViewTreeWidget.setAnimated(True)
        self.RelationsViewTreeWidget.setWordWrap(True)
        self.RelationsViewTreeWidget.setColumnCount(4)
        self.RelationsViewTreeWidget.setObjectName("RelationsViewTreeWidget")
        self.RelationsViewTreeWidget.headerItem().setText(0, "1")
        self.RelationsViewTreeWidget.headerItem().setText(1, "2")
        self.RelationsViewTreeWidget.headerItem().setText(2, "3")
        self.RelationsViewTreeWidget.headerItem().setText(3, "4")
        self.RelationsViewTreeWidget.header().setVisible(False)
        self.RelationsViewTreeWidget.header().setCascadingSectionResizes(True)
        self.RelationsViewTreeWidget.header().setMinimumSectionSize(5)
        self.RelationsViewTreeWidget.header().setSortIndicatorShown(True)
        self.RelationsViewTreeWidget.header().setStretchLastSection(False)
        self.gridLayout_4.addWidget(self.RelationsViewTreeWidget, 3, 0, 1, 1)

        self.RelationsViewTreeWidget.setHeaderHidden(False)
        self.RelationsViewTreeWidget.setHeaderLabels(
            ['Related Table(references)', 'FK', 'CR', 'SH'])
        self.RelationsViewTreeWidget.header().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.RelationsViewTreeWidget.header().setStretchLastSection(False)
        self.RelationsViewTreeWidget.setColumnCount(4)
        self.RelationsViewTreeWidget.setColumnWidth(1, 30)
        self.RelationsViewTreeWidget.setColumnWidth(2, 30)
        self.RelationsViewTreeWidget.setColumnWidth(3, 30)

        """ Saved relation presets data """
        self.relation_presets = self.application.settings.value("relation_presets")
        if self.relation_presets is None:
            self.relation_presets = {}
        
        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)
        
    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        self.SelectedObjectRelationsGroupBox.setTitle(_translate("Form", "Object Relations"))
        self.RelationPresetsLabel.setText(_translate("Form", "Relation Presets"))
        self.ApplyPresetToolButton.setText(_translate("Form", "Apply"))
        self.SelectWithDatabaseModelCheckBox.setText(_translate("Form", "Select using database model"))
        self.DeleteResidualCheckBox.setToolTip(_translate("Form", "Selects the transport instruction to delete residual objects which were not provided in the transport package."))
        self.DeleteResidualCheckBox.setText(_translate("Form", "Delete Residual Objects "))
        self.ShowAllColumnsCheckBox.setText(_translate("Form", "Show All Columns"))
        self.AutoListObjectsFromDatabaseCheckBox.setText(_translate("Form", "Auto List Selected Objects from database"))
        self.DeselectAllToolButton.setText(_translate("Form", "Deselect All Relations"))
        self.AutoLoadCheckBox.setText(_translate("Form", "Auto Load Matching Objects from database"))
        self.RelationsViewTreeWidget.setSortingEnabled(True)