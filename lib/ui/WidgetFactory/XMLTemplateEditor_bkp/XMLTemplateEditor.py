from PyQt6 import QtCore, QtWidgets
from ..CodeEditors import xml_editor
from .TreeWidgets import *

from .XMLTemplateView import XMLTemplateView
from .DatabaseRelations import DatabaseRelations

XML_PREVIEW_TIMER = 100

class XMLTemplateEditor(QtWidgets.QWidget):

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.current_file = None
        self.xml_structure_widgets = []

        self.setupUi()
        self.XMLTemplateView = XMLTemplateView(self, application)
        self.DatabaseRelations = DatabaseRelations(self, application)

        self.FindObjectButton.clicked.connect(self.queryDatabaseObjects)
        self.TableComboBox.currentTextChanged.connect(self.load_db_objects)
        self.AddSelectedObjectsWithRelationsButton.clicked.connect(self.select_object_for_transport)
        self.SearchResultsListWidget.itemClicked.connect(self.select_source_object)
        self.XMLStructureTreeWidget.itemClicked.connect(self.select_source_object)
        self.RelationsViewTreeWidget.itemChanged.connect(self.handle_data_change)
        self.XMLStructureTreeWidget.itemChanged.connect(self.handle_data_change)
        self.XMLStructureTreeWidget.dragMoveEvent = self.XMLTemplateView.xml_structure_move_event
        self.XMLStructureTreeWidget.dropEvent = self.XMLTemplateView.xml_structure_drop_event
        
        self.DeselectAllToolButton.clicked.connect(self.DatabaseRelations.deselect_all_relations)
        self.AddAsSingleObjectsButton.clicked.connect(
            lambda: self.select_object_for_transport(add_without_relations=True))
        self.ApplyPresetToolButton.clicked.connect(self.DatabaseRelations.apply_table_relation_preset)

        """ Context Menu """
        self.RelationsViewTreeWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.XMLStructureTreeWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.RelationsViewTreeWidget.customContextMenuRequested.connect(self.DatabaseRelations.relationContextMenuRequested)
        self.XMLStructureTreeWidget.customContextMenuRequested.connect(self.XMLTemplateView.xmlContextMenuRequested)
        

    def refresh_ui(self):
        if self.application.db.is_connected:
            self.FindObjectButton.setEnabled(True)
            self.TableComboBox.setEnabled(True)

        self.TableComboBox.clear()
        for table_name in self.application.db.table_info.keys():
            self.TableComboBox.addItem(table_name)

        self.XMLEditorWidget.reconfigure_editor()

    def get_objectkey_table(self, input_string):
        table_name = None
        regex = r"<T>(.*?)</T>"
        if input_string is not None:
            match = re.search(regex, input_string)
            if match:
                table_name = match.group(1)
        return table_name

    def load_db_objects(self, table_name=None, data_rows=[]):
        self.SearchResultsListWidget.clear()

        if len(data_rows) == 0 and table_name: 
            query = f"select * from {table_name}"
            data_rows = self.application.db.run_db_query(query)

        for row in data_rows:
            w = TemplateEditorListWidgetItem(self, self.application, row, table_name=table_name)
            self.SearchResultsListWidget.addItem(w)

        self.DatabaseRelations.load_table_relation_presets(table_name)
    
    def queryDatabaseObjects(self):
        if not self.application.db.is_connected:
            return False
        
        filter = self.ObjectQueryTextEdit.toPlainText()
        data_rows = []

        if self.XObjectKeysFilterRadioButton.isChecked():
            filter_rows = filter.splitlines()
            for object_query in filter_rows:
                object_query = object_query.strip()
                table_name = self.get_objectkey_table(object_query)
                if table_name is not None:
                    query = f"select * from {table_name} where XObjectKey = '{object_query}'"
                    data_rows += self.application.db.run_db_query(query)

        if self.SelectedTableFilterRadioButton.isChecked() and self.TableComboBox.currentText().strip() != "":
            object_query = filter.strip()
            table_name = self.TableComboBox.currentText()
            if len(object_query) > 0:
                query = f"select * from {table_name} where {object_query}"
                data_rows += self.application.db.run_db_query(query)
            else:
                query = f"select * from {table_name}"
                data_rows += self.application.db.run_db_query(query)
        self.load_db_objects(data_rows=data_rows)

    """ Custom Widget Operations """
    def handle_data_change(self, changed_widget, column):       
        if isinstance(changed_widget, TemplateEditorTreeWidgetItem):
            changed_widget.handle_data_change(column)
        self.XMLTemplateView.xml_structure_changed.emit()

    def deleteSelectedItems(self):
        tree_widgets = [self.XMLStructureTreeWidget]
        for tree_widget in tree_widgets:
            self.remove_tree_widget_selected_node(tree_widget)
        
    def remove_tree_widget_selected_node(self, tree_widget):
        if tree_widget.hasFocus():
            for node_widget in tree_widget.selectedItems():
                if isinstance(node_widget, TemplateEditorTreeWidgetItem):
                    node_widget.deleteObject()
                
                if node_widget in self.xml_structure_widgets:
                    self.xml_structure_widgets.remove(node_widget)
                parent_node = node_widget.parent()
                
                if parent_node:
                    parent_node.removeChild(node_widget)
                else:
                    root = tree_widget.invisibleRootItem()
                    root.removeChild(node_widget)

            if tree_widget == self.XMLStructureTreeWidget:
                self.XMLTemplateView.reset_xml_order()
                self.XMLTemplateView.xml_structure_changed.emit()

    def clear_widgets(self):
        self.TableComboBox.clear()
        self.TableFilter.clear()

    def select_source_object(self, source_widget_item):
        if isinstance(source_widget_item, TemplateEditorListWidgetItem):
            self.last_widget_clicked = source_widget_item.listWidget()
        
        if isinstance(source_widget_item, TE_ObjectContainer_TreeWidgetItem):
            self.last_widget_clicked = source_widget_item.treeWidget()

        if isinstance(source_widget_item, TE_ObjectContainer_TreeWidgetItem) or isinstance(source_widget_item, TemplateEditorListWidgetItem):
            relations = source_widget_item.object_relations
            self.RelationsViewTreeWidget.clear()

            if relations is not None:
                self.DatabaseRelations.load_table_relations(relations, source_widget_item)  

            if isinstance(source_widget_item, TE_ObjectContainer_TreeWidgetItem):
                self.XMLEditorWidget.find_text(source_widget_item.search_text)
            
            self.DatabaseRelations.load_table_relation_presets(source_widget_item.table_name)
    
    def select_object_for_transport(self, add_without_relations=False):
        selected_source_widget_items = self.SearchResultsListWidget.selectedItems()
        if selected_source_widget_items is not None:
            selected_target_widgets = self.XMLStructureTreeWidget.selectedItems()
            task_item = None
            if len(selected_target_widgets) == 0:
                """ Create UI Node """
                task_item = self.XMLTemplateView.add_transport_task("VI.Transport.ObjectTransport, VI.Transport")
            else:
                """ Find Parent Node """
                for widget in selected_target_widgets:
                    while task_item is None:
                        if widget.parent() is None:
                            task_item = widget
                        widget = widget.parent()
                    break

            for source_widget_item in selected_source_widget_items:
                """ Add all selected objects to selected Task Container """
                if isinstance(source_widget_item, TemplateEditorListWidgetItem):
                    pk_columns_dict = {}
                    for pk_column in source_widget_item.pk_columns:
                        if pk_column is not None and pk_column not in pk_columns_dict.keys():
                            pk_columns_dict[pk_column] = source_widget_item.get_value(pk_column)

                    container_element = task_item.xml_object.add_container(base_table=source_widget_item.table_name, display_name=source_widget_item.display_name, delete_residual_objects=str(int(self.DeleteResidualCheckBox.isChecked())), pk_columns=pk_columns_dict, relations=source_widget_item.object_relations)

                    object_container = TE_ObjectContainer_TreeWidgetItem(self, self.application, object_data=source_widget_item.object_data, xml_object=container_element, source_widget_item=source_widget_item, table_name=source_widget_item.table_name)
                    
                    container_element.relations = object_container.object_relations

                    task_item.addChild(object_container)

                    self.XMLTemplateView.xml_structure_widgets.append(object_container)

                    if add_without_relations:
                        object_container.set_all_relations_state(0)
                    
                    task_item.setExpanded(True)

        self.XMLTemplateView.xml_structure_changed.emit()

    def setupUi(self):
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.TemplateEditorSplitter_Left = QtWidgets.QSplitter(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TemplateEditorSplitter_Left.sizePolicy().hasHeightForWidth())
        self.TemplateEditorSplitter_Left.setSizePolicy(sizePolicy)
        self.TemplateEditorSplitter_Left.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.TemplateEditorSplitter_Left.setObjectName("TemplateEditorSplitter_Left")
        self.TemplateEditorSplitter_Relations = QtWidgets.QSplitter(self.TemplateEditorSplitter_Left)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TemplateEditorSplitter_Relations.sizePolicy().hasHeightForWidth())
        self.TemplateEditorSplitter_Relations.setSizePolicy(sizePolicy)
        self.TemplateEditorSplitter_Relations.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.TemplateEditorSplitter_Relations.setObjectName("TemplateEditorSplitter_Relations")
        self.TemplateEditorSplitter_Search = QtWidgets.QSplitter(self.TemplateEditorSplitter_Relations)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TemplateEditorSplitter_Search.sizePolicy().hasHeightForWidth())
        self.TemplateEditorSplitter_Search.setSizePolicy(sizePolicy)
        self.TemplateEditorSplitter_Search.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.TemplateEditorSplitter_Search.setObjectName("TemplateEditorSplitter_Search")
        self.SearchGroupBox = QtWidgets.QGroupBox(self.TemplateEditorSplitter_Search)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SearchGroupBox.sizePolicy().hasHeightForWidth())
        self.SearchGroupBox.setSizePolicy(sizePolicy)
        self.SearchGroupBox.setObjectName("SearchGroupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.SearchGroupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.TableComboBox = QtWidgets.QComboBox(self.SearchGroupBox)
        self.TableComboBox.setObjectName("TableComboBox")
        self.verticalLayout_2.addWidget(self.TableComboBox)
        self.ObjectQueryTextEdit = QtWidgets.QTextEdit(self.SearchGroupBox)
        self.ObjectQueryTextEdit.setTabChangesFocus(False)
        self.ObjectQueryTextEdit.setAcceptRichText(False)
        self.ObjectQueryTextEdit.setObjectName("ObjectQueryTextEdit")
        self.verticalLayout_2.addWidget(self.ObjectQueryTextEdit)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 2, -1, 2)
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.XObjectKeysFilterRadioButton = QtWidgets.QRadioButton(self.SearchGroupBox)
        self.XObjectKeysFilterRadioButton.setChecked(True)
        self.XObjectKeysFilterRadioButton.setObjectName("XObjectKeysFilterRadioButton")
        self.horizontalLayout_2.addWidget(self.XObjectKeysFilterRadioButton)
        self.SelectedTableFilterRadioButton = QtWidgets.QRadioButton(self.SearchGroupBox)
        self.SelectedTableFilterRadioButton.setEnabled(True)
        self.SelectedTableFilterRadioButton.setObjectName("SelectedTableFilterRadioButton")
        self.horizontalLayout_2.addWidget(self.SelectedTableFilterRadioButton)
        self.FindObjectButton = QtWidgets.QToolButton(self.SearchGroupBox)
        self.FindObjectButton.setObjectName("FindObjectButton")
        self.horizontalLayout_2.addWidget(self.FindObjectButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.SearchResultsGroupBox = QtWidgets.QGroupBox(self.TemplateEditorSplitter_Search)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SearchResultsGroupBox.sizePolicy().hasHeightForWidth())
        self.SearchResultsGroupBox.setSizePolicy(sizePolicy)
        self.SearchResultsGroupBox.setObjectName("SearchResultsGroupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.SearchResultsGroupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.SearchResultsListWidget = QtWidgets.QListWidget(self.SearchResultsGroupBox)
        self.SearchResultsListWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragOnly)
        self.SearchResultsListWidget.setDefaultDropAction(QtCore.Qt.DropAction.IgnoreAction)
        self.SearchResultsListWidget.setAlternatingRowColors(True)
        self.SearchResultsListWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.SearchResultsListWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.SearchResultsListWidget.setMovement(QtWidgets.QListView.Movement.Free)
        self.SearchResultsListWidget.setProperty("isWrapping", False)
        self.SearchResultsListWidget.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.SearchResultsListWidget.setWordWrap(True)
        self.SearchResultsListWidget.setItemAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.SearchResultsListWidget.setObjectName("SearchResultsListWidget")
        self.verticalLayout_3.addWidget(self.SearchResultsListWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.AddSelectedObjectsWithRelationsButton = QtWidgets.QToolButton(self.SearchResultsGroupBox)
        self.AddSelectedObjectsWithRelationsButton.setObjectName("AddSelectedObjectsWithRelationsButton")
        self.horizontalLayout_5.addWidget(self.AddSelectedObjectsWithRelationsButton)
        self.AddAsSingleObjectsButton = QtWidgets.QToolButton(self.SearchResultsGroupBox)
        self.AddAsSingleObjectsButton.setObjectName("AddAsSingleObjectsButton")
        self.horizontalLayout_5.addWidget(self.AddAsSingleObjectsButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.SelectedObjectRelationsGroupBox = QtWidgets.QGroupBox(self.TemplateEditorSplitter_Relations)
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
        self.TemplateEditorSplitter_Right = QtWidgets.QSplitter(self.TemplateEditorSplitter_Left)
        self.TemplateEditorSplitter_Right.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.TemplateEditorSplitter_Right.setObjectName("TemplateEditorSplitter_Right")
        self.XMLStructureTreeWidget = QtWidgets.QTreeWidget(self.TemplateEditorSplitter_Right)
        self.XMLStructureTreeWidget.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.XMLStructureTreeWidget.setProperty("showDropIndicator", True)
        self.XMLStructureTreeWidget.setDragEnabled(True)
        self.XMLStructureTreeWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.XMLStructureTreeWidget.setAlternatingRowColors(True)
        self.XMLStructureTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.XMLStructureTreeWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.XMLStructureTreeWidget.setTextElideMode(QtCore.Qt.TextElideMode.ElideLeft)
        self.XMLStructureTreeWidget.setIndentation(25)
        self.XMLStructureTreeWidget.setRootIsDecorated(True)
        self.XMLStructureTreeWidget.setUniformRowHeights(True)
        self.XMLStructureTreeWidget.setAnimated(True)
        self.XMLStructureTreeWidget.setAllColumnsShowFocus(True)
        self.XMLStructureTreeWidget.setWordWrap(True)
        self.XMLStructureTreeWidget.setColumnCount(2)
        self.XMLStructureTreeWidget.setObjectName("XMLStructureTreeWidget")
        self.XMLStructureTreeWidget.headerItem().setText(0, "1")
        self.XMLStructureTreeWidget.headerItem().setText(1, "2")
        self.XMLStructureTreeWidget.header().setVisible(False)
        self.XMLStructureTreeWidget.header().setCascadingSectionResizes(False)
        self.XMLStructureTreeWidget.header().setDefaultSectionSize(39)
        self.XMLStructureTreeWidget.header().setHighlightSections(True)
        self.XMLStructureTreeWidget.header().setStretchLastSection(False)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.TemplateEditorSplitter_Right)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.XMLEditorLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.XMLEditorLayout.setContentsMargins(0, 0, 0, 0)
        self.XMLEditorLayout.setSpacing(0)
        self.XMLEditorLayout.setObjectName("XMLEditorLayout")
        self.gridLayout.addWidget(self.TemplateEditorSplitter_Left, 0, 0, 1, 1)
        
        """ Additional UI Configurations """
        self.XMLEditorWidget = xml_editor(self.application)
        self.current_file_label = QtWidgets.QLabel(self)
        self.current_file_label.setProperty("Widget", "FilePathLabel")
        self.current_file_label.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse|QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard)
        self.current_file_label.setWordWrap(True)
        self.XMLEditorLayout.insertWidget(0, self.current_file_label)
        self.XMLEditorLayout.insertWidget(1, self.XMLEditorWidget)

        self.TemplateEditorSplitter_Search.setSizes(
            [round(self.height()*0.1), round(self.height()*0.3)])
        self.TemplateEditorSplitter_Relations.setSizes(
            [round(self.height()*0.2), round(self.height()*0.2)])

        self.TemplateEditorSplitter_Left.setSizes(
            [1, round(self.width()*0.8)])
        self.TemplateEditorSplitter_Right.setSizes(
            [round(self.width()*0.4), round(self.width()*0.6)])

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

        self.XMLStructureTreeWidget.setHeaderHidden(False)
        self.XMLStructureTreeWidget.setHeaderLabels(
            ['Transport Structure', 'Task Options'])
        self.XMLStructureTreeWidget.setColumnWidth(0, 500)    
        self.XMLStructureTreeWidget.setColumnWidth(1, 200)    
        self.XMLStructureTreeWidget.setWordWrap(True)
        self.FindObjectButton.setEnabled(False)
        self.TableComboBox.setEnabled(False)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        self.SearchGroupBox.setTitle(_translate("Form", "Search"))
        self.TableComboBox.setPlaceholderText(_translate("Form", "Select From Table"))
        self.ObjectQueryTextEdit.setPlaceholderText(_translate("Form", "Search Database Objects"))
        self.XObjectKeysFilterRadioButton.setText(_translate("Form", "List of XObjectKeys"))
        self.SelectedTableFilterRadioButton.setText(_translate("Form", "Selected Table Filter"))
        self.FindObjectButton.setText(_translate("Form", "Find Objects"))
        self.SearchResultsGroupBox.setTitle(_translate("Form", "Search Results"))
        self.SearchResultsListWidget.setSortingEnabled(True)
        self.AddSelectedObjectsWithRelationsButton.setText(_translate("Form", "Add With Selected Relations"))
        self.AddAsSingleObjectsButton.setText(_translate("Form", "Add Without Relations"))
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
        self.RelationsViewTreeWidget.setSortingEnabled(False)
        self.XMLStructureTreeWidget.setSortingEnabled(False)
