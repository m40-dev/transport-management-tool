from PyQt6 import QtCore, QtWidgets
from .XMLTemplateEditorWidget import XMLTemplateEditorWidget
from ..DialogScreens import DatePickerDialog, MsgBox
from .DatabaseRelations import DatabaseRelations
from lib.data.DataModels.XMTemplateEditor import ObjectDataListModel, XMLDataItem, ObjectDataItem
from .ContextMenu import ObjectDataItemContextMenu
from copy import deepcopy
from datetime import datetime

XML_PREVIEW_TIMER = 100
SEARCH_FILTER_OPTIONS = {
    "TableQuery" : "Select from Database Table",
    "ChangeLabelQuery": "Select by Change Label",
    "XObjectKeyQuery": "Find Objects by XObjectKey",
    "GlobalSearch":  "System Wide Object Search"
    }

class XMLTemplateEditor(QtWidgets.QWidget):
    refreshUi = QtCore.pyqtSignal()
    current_file_changed = QtCore.pyqtSignal(str)
    tableSelectionRequested = QtCore.pyqtSignal(str)
    tabNameChanged = QtCore.pyqtSignal(object)
    
    def __init__(self, application):
        super().__init__()
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self.query_option = "TableQuery"
        self.query_filters = {}
    
        self.setupUi()
        self.current_file_changed.connect(self.selectXMLTemplateTab)

        #Connect Signals

        # Database Relations Handling
        self.TableComboBox.currentIndexChanged.connect(self.queryDatabaseObjects)
        self.FilterComboBox.currentIndexChanged.connect(self.searchFilterConfigurationChanged)
        self.ListClosedLabelsCheckBox.stateChanged.connect(self.reloadChangeLabels)
        self.ChangeLabelComboBox.currentIndexChanged.connect(self.listChangeLabelObjects)
        self.tableSelectionRequested.connect(self.onTableQueryRequested)
        self.DatabaseRelations.relationSettingsChanged.connect(self.relationSettingsChanged)
        self.DatabaseRelations.relationResetRequested.connect(self.resetRelationStates)
        self.tabNameChanged.connect(self.renameTabWidget)
        # self.XMLTemplateEditorTabWidget.tabBar().installEventFilter(self)

        # Database Objects listing
        self.FindObjectButton.clicked.connect(self.queryDatabaseObjects)
        self.searchFilterConfigurationChanged()

    def searchFilterConfigurationChanged(self, current_index=None):
        if current_index is None:
            current_index = self.FilterComboBox.currentIndex()

        option = self.FilterComboBox.itemData(current_index)
        
        self.query_option = option

        self.TableComboBox.setVisible(option in ["TableQuery"])
        self.ObjectQueryTextEdit.setVisible(option in ["TableQuery", "XObjectKeyQuery"])
        self.ObjectQueryTextEdit.setText(self.query_filters.get(self.query_option, ""))
        self.ChangeLabelComboBox.setVisible(option in ["ChangeLabelQuery"])
        self.ListClosedLabelsCheckBox.setVisible(option in ["ChangeLabelQuery"])

        self.ChangesDateCheckbox.setVisible(option in ["GlobalSearch"])
        self.ChangesDateLabel.setVisible(option in ["GlobalSearch"])
        self.ChangesDateQuery.setVisible(option in ["GlobalSearch"])
        self.DatePickerButton.setVisible(option in ["GlobalSearch"])

        self.ChangesDateLabel.setEnabled(self.ChangesDateCheckbox.isChecked())
        self.ChangesDateQuery.setEnabled(self.ChangesDateCheckbox.isChecked())
        self.DatePickerButton.setEnabled(self.ChangesDateCheckbox.isChecked())
        
        self.UserChangesCheckbox.setVisible(option in ["GlobalSearch"])
        self.UserChangesQuery.setVisible(option in ["GlobalSearch"])
        self.UserChangesQuery.setEnabled(self.UserChangesCheckbox.isChecked())

        self.IncludePartialResultsLabel.setVisible(option in ["GlobalSearch"])
        self.IncludePartialResultsCheckbox.setVisible(option in ["GlobalSearch"])


        # Option Dependent Configurations 
        if option in ["TableQuery"]:
            self.ObjectQueryTextEdit.setPlaceholderText("Provide additional SQL where clause here..")
        
        if option in ["XObjectKeyQuery"]:
            self.ObjectQueryTextEdit.setPlaceholderText("Provide list of XObjectKeys here..")

    def onTableQueryRequested(self, table_name):
        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()

        if self.query_option != "TableQuery":
            target_index = self.FilterComboBox.findData("TableQuery")
            self.FilterComboBox.setCurrentIndex(target_index)
            # self.ObjectQueryTextEdit.clear()
            
        if table_name not in self.TableComboBox.currentText():
            table_index = self.TableComboBox.findData(table_name)
            self.TableComboBox.setCurrentIndex(table_index)

        self.queryDatabaseObjects()
        

    def newTransportTemplate(self, file_path=None):
        tabWidget = XMLTemplateEditorWidget(self, self.application, file_path)
        index = self.XMLTemplateEditorTabWidget.addTab(tabWidget, tabWidget.display)
        self.application.ui.MainTabWidget.setCurrentWidget(self)
        self.XMLTemplateEditorTabWidget.setCurrentWidget(tabWidget)
        return index

    def openXMLTemplate(self, file_path=None):
        if file_path is None:
            dialog = QtWidgets.QFileDialog(self.application, "Open existing template file")
            dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)

            file_path = dialog.getOpenFileName(filter="*.xml")
            file_path = file_path[0]

        if file_path and self.setCurrentXMLTemplate(file_path):
            self.application.ui.MainTabWidget.setCurrentWidget(self)
    
    def onTabWidgetClose(self, tab_index):
        tab_widget = self.XMLTemplateEditorTabWidget.widget(tab_index)
        if tab_widget.onWidgetClose():
            self.XMLTemplateEditorTabWidget.removeTab(tab_index)
            del tab_widget
        
    def selectXMLTemplateTab(self, file_path):
        for index in range(0, self.XMLTemplateEditorTabWidget.count()):
            tab_widget = self.XMLTemplateEditorTabWidget.widget(index)
            # print(tab_widget, "search for tab with file path:", file_path, "found:", tab_widget.current_file)
            if file_path and tab_widget.current_file and file_path.lower() == tab_widget.current_file.lower():
                # print("existing tab widget found", tab_widget.current_file)
                self.XMLTemplateEditorTabWidget.setCurrentWidget(tab_widget)
                # tab_widget.refreshXMLPreview()
                tab_widget.reloadXMLFile()
                self.application.ui.MainTabWidget.setCurrentWidget(self)
                return True

    def setCurrentXMLTemplate(self, file_path):
        if self.XMLTemplateEditorTabWidget.count() == 0:
            # No tabs are opened
            self.newTransportTemplate(file_path=file_path)
            return True
        
        if not self.selectXMLTemplateTab(file_path=file_path):
            self.newTransportTemplate(file_path=file_path)

    def renameTabWidget(self, tab_widget):
        # print("rename tab widget", tab_widget.display)
        index = self.XMLTemplateEditorTabWidget.indexOf(tab_widget)
        self.XMLTemplateEditorTabWidget.setTabText(index, tab_widget.display)

    def saveXMLTemplate(self):
        current_tab = self.XMLTemplateEditorTabWidget.currentWidget()
        if current_tab:
            current_tab.saveXMLTemplate()

    def saveXMLTemplateAs(self, initial_directory=None):
        current_tab = self.XMLTemplateEditorTabWidget.currentWidget()
        if current_tab:
            current_tab.saveXMLTemplateAs(initial_directory)

    def queryDatabaseObjects(self, index=None):
        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()
        
        object_filter = self.ObjectQueryTextEdit.toPlainText()

        if self.query_option == "XObjectKeyQuery":
            filter_rows = object_filter.splitlines()
            query_data = self.application.db.get_objects_by_xobjectkey(filter_rows)
            self.SearchResultsTreeView.model().sort_children_by_name = False
            self.SearchResultsTreeView.model().reloadModelData(query_data)
        
        if self.query_option == "TableQuery":
            table_name = self.TableComboBox.itemData(self.TableComboBox.currentIndex())

            if table_name and len(table_name) > 0 and table_name in self.application.db.table_info.keys():
                self.listTableObjects(table_name=table_name)
        
        if self.query_option == "ChangeLabelQuery":
            self.listChangeLabelObjects()

        if self.query_option == "GlobalSearch":
            min_date = None
            system_users = None
            include_partial_results = self.IncludePartialResultsCheckbox.isChecked()
            if not self.ChangesDateQuery.isEnabled() and not self.UserChangesQuery.isEnabled():

                MsgBox(
                    application=self.application,
                    window_title="Operation Cancelled",
                    message="Global Search operation cancelled,\nplease provide at least one search condition and run query again.",
                    window_mode=MsgBox.INFO
                )
                return

            if self.ChangesDateQuery.isEnabled():
                min_date = self.ChangesDateQuery.date()
            
            if self.UserChangesQuery.isEnabled():
                system_users = self.UserChangesQuery.text()

            query_data = self.application.db.run_global_query(min_date, system_users, include_partial_results)

            self.SearchResultsTreeView.model().sort_children_by_name = False
            self.SearchResultsTreeView.model().reloadModelData(query_data)

        self.DatabaseQueryTabWidget.setCurrentWidget(self.SearchResultsGroupBox)

    def listTableObjects(self, table_name=None, data_rows=[]):
        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()

        if len(data_rows) == 0 and table_name: 
            # print(f"list table objects from table: {table_name}")
            # get single object to determine its data
            query = f"select top 1 * from {table_name}"
            data_rows = self.application.db.run_db_query(query)
            # query full table data if any record exists
            if len(data_rows) > 0:
                table_columns = self.application.db.get_object_columns(data_rows[0])
                sort_clause = ""
                where_clause = self.ObjectQueryTextEdit.toPlainText().strip()

                for index in range(0, len(table_columns)):
                    table_columns[index] = table_columns[index].lower()
                
                # add sort clause where possible, some tables do not have xdate fields
                if "xdateinserted" in table_columns and "xdateupdated" in table_columns:
                    sort_clause = "order by xdateupdated desc, xdateinserted desc"
                if len(where_clause) > 0:
                    query = f"select * from {table_name} where {where_clause} {sort_clause}"
                else:
                    query = f"select * from {table_name} {sort_clause}"

                data_rows = self.application.db.run_db_query(query)
        
        self.SearchResultsTreeView.model().reloadModelData(data_rows)

    def SearchResultsListDragMoveEvent(self, event):
        event.ignore()

    def resetRelationStates(self, source_item, state):
        if self.XMLTemplateEditorTabWidget.count() == 0:
            return True
        if source_item:
            source_item.resetRelationStates(state)
        
        for selected_item in self.selectedItems():
            if isinstance(selected_item, XMLDataItem):
                selected_item.resetRelationStates(state)
        # refresh XML preview
        self.XMLTemplateEditorTabWidget.currentWidget().xmlStructureChanged.emit()

    def switchObjectConfigurationTabs(self, source_index=None):
        """ Switch between Search results view and database relations view according to last object that was selected """
        source_item = None
        if source_index and source_index.isValid():
            source_item = source_index.internalPointer()
            if isinstance(source_item, XMLDataItem) and source_item.xml_object_class == "Transport_Object":
                self.DatabaseQueryTabWidget.setCurrentWidget(self.DatabaseRelations)
                return
        #Fallback to search results view
        self.DatabaseQueryTabWidget.setCurrentWidget(self.SearchResultsGroupBox)


    def reloadDatabaseRelations(self, source_index):
        self.DatabaseRelations.loadRelationData(source_index)

    def refresh_ui(self):
        self.setStyleSheet(self.application.ProgramConfiguration.styleSheet())
        self.refreshUi.emit()

    def reloadView(self):
        self.TableComboBox.clear()
        self.TableComboBox.addItem("")
        if self.application.db and self.application.db.is_connected:
            self.FilterComboBox.setEnabled(True)
            self.FindObjectButton.setEnabled(True)
            self.TableComboBox.setEnabled(True)
            self.ChangeLabelComboBox.setEnabled(True)
            self.ListClosedLabelsCheckBox.setEnabled(True)
            self.ObjectQueryTextEdit.setEnabled(True)

            for table_name, table_data in self.application.db.table_info.items():
                table_display = f"{table_name} ({table_data.DisplayName})" 
                self.TableComboBox.addItem(table_display, table_name)
                
            self.reloadChangeLabels()

    def reloadChangeLabels(self):
        self.ChangeLabelComboBox.clear()
        self.ChangeLabelComboBox.addItem("")
        label_states = self.ListClosedLabelsCheckBox.isChecked()
        change_labels = self.application.db.get_change_labels(label_states)
        for data_row in change_labels:
            display_name = self.application.db.get_object_display_name("DialogTag", data_row)
            self.ChangeLabelComboBox.addItem(display_name, data_row.UID_DialogTag)
            # print(display_name, data_row.UID_DialogTag)
        self.ChangeLabelComboBox.model().sort(0)

    def listChangeLabelObjects(self, current_index=None):
        if current_index is None:
            current_index = self.ChangeLabelComboBox.currentIndex()

        selected_label_uid = self.ChangeLabelComboBox.itemData(current_index)

        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()
        
        # data_rows = []

        label_data = self.application.db.get_objects_by_change_label(selected_label_uid)
        # for table_name, label_data_rows in label_data.items():
        #     data_rows += label_data_rows

        self.SearchResultsTreeView.model().tableNameInDisplay = True
        self.SearchResultsTreeView.model().reloadModelData(label_data)

    def relationSettingsChanged(self, source_item):
        if self.XMLTemplateEditorTabWidget.count() == 0:
            return True
        # remap the source_item object relations to trigger all right setters
        if source_item:
            source_item.object_relations = source_item.object_relations

        # reset relation configuration for the other selected objects of the same class 
        for item in self.selectedItems():
            if isinstance(item, XMLDataItem) and item.xml_object_class == "Transport_Object" and item.table_name == source_item.table_name:
                item.object_relations = source_item.object_relations
        # refresh XML preview
        self.XMLTemplateEditorTabWidget.currentWidget().xmlStructureChanged.emit()
    
    def selectedItems(self):
        current_tab = self.XMLTemplateEditorTabWidget.currentWidget()
        if current_tab:
            return current_tab.selectedItems()
        return []

    def deleteSelectedItems(self):
        if self.XMLTemplateEditorTabWidget.count() == 0:
            return False

        self.XMLTemplateEditorTabWidget.currentWidget().deleteSelectedItems()
        self.DatabaseRelations.deleteSelectedItems()

    def relationPresetApplyRequested(self, preset_table, preset_data):
        if self.XMLTemplateEditorTabWidget.count() == 0:
            return False

        if preset_table and preset_data:
            selected_items = self.selectedItems()
            if len(selected_items) > 0:
                preset_name = preset_data["name"]
                question = MsgBox(self.application, 
                        message=f"Are you sure to apply selected relation preset? <br/> (<b>{preset_name}</b>) <br/t> Existing relations for selected objects of the same class (<b>{preset_table}</b>) will be overwritten.",
                        window_mode=MsgBox.QUESTION)
        
                if not question.accepted:
                    return
            
            for item in selected_items:
                if isinstance(item, XMLDataItem) and item.xml_object_class == "Transport_Object" and item.table_name == preset_table:
                    preset_data_relations = deepcopy(preset_data["table_relations"])
                    item.object_relations = preset_data_relations

        self.XMLTemplateEditorTabWidget.currentWidget().xmlStructureChanged.emit()

    def foldXMLPreview(self):
        if self.XMLTemplateEditorTabWidget.count() == 0:
            return False

        current_tab = self.XMLTemplateEditorTabWidget.currentWidget()
        if current_tab:
            current_tab.XMLPreviewBrowser.foldByLevel()

    def expandXMLPreview(self):
        if self.XMLTemplateEditorTabWidget.count() == 0:
            return False

        current_tab = self.XMLTemplateEditorTabWidget.currentWidget()
        if current_tab:
            current_tab.XMLPreviewBrowser.expandByLevel()

    def onDatePickerInputRequested(self, target):
        target_x = self.application.x() + self.DatePickerButton.x() + 100
        target_y = self.application.y() + self.DatePickerButton.y() - 40
        
        date_picker = DatePickerDialog(application=self.application)
        date_picker.setCurrentDate(target.date())
        date_picker.move(target_x, target_y)
        if date_picker.exec():
            if date_picker.accepted and date_picker.selectedDate():
                target.setDate(date_picker.selectedDate())

    def onQueryWhereClauseTextChange(self):
        self.query_filters[self.query_option] = self.ObjectQueryTextEdit.toPlainText()

    def onSearchResultsContextMenuRequested(self, menuPosition):
        clickedIndex = self.SearchResultsTreeView.indexAt(menuPosition)
        clickedItem = clickedIndex.internalPointer()
        if isinstance(clickedItem, ObjectDataItem):
            contextMenu = ObjectDataItemContextMenu(
                parent=self.application, 
                source_index=clickedIndex)
            contextMenu.onQueryTableData.connect(self.queryTaskData)
            contextMenu.onCollapseTreeStructure.connect(lambda source_index: self.toggleTreeStructure(True, source_index))
            contextMenu.onExpandTreeStructure.connect(lambda source_index: self.toggleTreeStructure(False, source_index))

            if len(contextMenu.menu_items) > 0:
                menu_target = self.SearchResultsTreeView.mapToGlobal(menuPosition)
                contextMenu.popup(menu_target)

    def queryTaskData(self, source_index):
        if source_index.isValid():
            source_item = source_index.internalPointer()
            if isinstance(source_item, (XMLDataItem, ObjectDataItem)):
                self.tableSelectionRequested.emit(source_item.table_name)

    def toggleTreeStructure(self, collapse_tree, source_index):
        selected_indexes = self.SearchResultsTreeView.selectedIndexes()
        for index in selected_indexes:
            if collapse_tree:
                self.SearchResultsTreeView.collapse(index)
            else:
                self.SearchResultsTreeView.expandRecursively(index)

    def setupUi(self):
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(1)
        self.gridLayout.setObjectName("gridLayout")
        
        self.TemplateEditorSplitter_Left = QtWidgets.QSplitter(self)
        self.gridLayout.addWidget(self.TemplateEditorSplitter_Left, 0, 0, 1, 1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        
        self.TemplateEditorSplitter_Left.setSizePolicy(sizePolicy)
        self.TemplateEditorSplitter_Left.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.TemplateEditorSplitter_Left.setObjectName("TemplateEditorSplitter_Left")
        self.TemplateEditorSplitter_Search = QtWidgets.QSplitter(self.TemplateEditorSplitter_Left)
        self.TemplateEditorSplitter_Search.setSizePolicy(sizePolicy)
        self.TemplateEditorSplitter_Search.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.TemplateEditorSplitter_Search.setObjectName("TemplateEditorSplitter_Search")

        # Search GroupBox Widgets Preparation
        self.SearchGroupBox = QtWidgets.QGroupBox(self.TemplateEditorSplitter_Search)
        self.SearchGroupBox.setSizePolicy(sizePolicy)
        self.SearchGroupBox.setObjectName("SearchGroupBox")
        self.SearchGroupBoxLayout = QtWidgets.QGridLayout(self.SearchGroupBox)
        self.SearchGroupBoxLayout.setObjectName("SearchGroupBoxLayout")
        self.FilterComboBox = QtWidgets.QComboBox(self.SearchGroupBox)
        
        for option_key, display_name in SEARCH_FILTER_OPTIONS.items():
            self.FilterComboBox.addItem(display_name, option_key)

        # self.TableComboBox = QtWidgets.QComboBox(self.SearchGroupBox)
        self.TableComboBox = ExtendedComboBox(self.SearchGroupBox)
        self.TableComboBox.setObjectName("TableComboBox")
        self.ObjectQueryTextEdit = QtWidgets.QTextEdit(self.SearchGroupBox)
        self.ObjectQueryTextEdit.setTabChangesFocus(False)
        self.ObjectQueryTextEdit.setAcceptRichText(False)
        self.ObjectQueryTextEdit.setObjectName("ObjectQueryTextEdit")
        self.ObjectQueryTextEdit.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        self.ObjectQueryTextEdit.textChanged.connect(self.onQueryWhereClauseTextChange)
        
        self.FindObjectButton = QtWidgets.QToolButton(self.SearchGroupBox)
        self.FindObjectButton.setObjectName("FindObjectButton")

        start_icon = self.ProgramConfiguration.getIcon("RunQuery")
        if start_icon:
            self.FindObjectButton.setText("")
            self.FindObjectButton.setToolTip("<i>Run Query..</i>")
            self.FindObjectButton.setIcon(start_icon)
            self.FindObjectButton.setIconSize(QtCore.QSize(20, 20))
            self.FindObjectButton.setProperty("Widget", "CustomToolButton")

        self.ChangeLabelComboBox = ExtendedComboBox()
        self.ChangeLabelComboBox.setPlaceholderText("Select Objects by Change Label")
        self.ListClosedLabelsCheckBox = QtWidgets.QCheckBox("Show All\nLabels")
       
        self.ChangesDateCheckbox = QtWidgets.QCheckBox()
        self.ChangesDateCheckbox.setChecked(True)
        self.ChangesDateCheckbox.stateChanged.connect(lambda: self.searchFilterConfigurationChanged(None))
        self.ChangesDateLabel = QtWidgets.QLabel()
        self.ChangesDateQuery = QtWidgets.QDateEdit()
        self.ChangesDateQuery.setDate(datetime.today())

        self.UserChangesCheckbox = QtWidgets.QCheckBox()
        self.UserChangesCheckbox.stateChanged.connect(lambda: self.searchFilterConfigurationChanged(None))

        self.UserChangesQuery = QtWidgets.QLineEdit()

        self.DatePickerButton = QtWidgets.QToolButton()
        self.DatePickerButton.clicked.connect(lambda: self.onDatePickerInputRequested(target=self.ChangesDateQuery))

        datepicker_icon = self.ProgramConfiguration.getIcon("DatePicker")
        if datepicker_icon:
            self.DatePickerButton.setText("")
            self.DatePickerButton.setToolTip("<i>Select From Calendar..</i>")
            self.DatePickerButton.setIcon(datepicker_icon)
            self.DatePickerButton.setIconSize(QtCore.QSize(20, 20))
            self.DatePickerButton.setProperty("Widget", "CustomToolButton")

        self.IncludePartialResultsCheckbox = QtWidgets.QCheckBox()
        self.IncludePartialResultsLabel = QtWidgets.QLabel()
        
        #Search GroupBox Layout Configuration
        self.SearchGroupBoxLayout.addWidget(self.FilterComboBox, 0, 0, 1, 4)
        self.SearchGroupBoxLayout.addWidget(self.TableComboBox, 1, 0, 1, 4)
        self.SearchGroupBoxLayout.addWidget(self.ChangeLabelComboBox, 2, 0, 1, 3)
        self.SearchGroupBoxLayout.addWidget(self.ListClosedLabelsCheckBox, 2, 3, 1, 1, QtCore.Qt.AlignmentFlag.AlignRight)
        self.SearchGroupBoxLayout.addWidget(self.ObjectQueryTextEdit, 2, 0, 5, 4)
        
        self.SearchGroupBoxLayout.addWidget(self.ChangesDateCheckbox, 3, 0, 1, 1)
        self.SearchGroupBoxLayout.addWidget(self.ChangesDateLabel, 3, 1, 1, 1)
        self.SearchGroupBoxLayout.addWidget(self.ChangesDateQuery, 3, 2, 1, 1)
        self.SearchGroupBoxLayout.addWidget(self.DatePickerButton, 3, 3, 1, 1)

        self.SearchGroupBoxLayout.addWidget(self.UserChangesCheckbox, 4, 0, 1, 1)
        self.SearchGroupBoxLayout.addWidget(self.UserChangesQuery, 4, 1, 1, 3)

        self.SearchGroupBoxLayout.addWidget(self.IncludePartialResultsCheckbox, 5, 0, 1, 1)
        self.SearchGroupBoxLayout.addWidget(self.IncludePartialResultsLabel, 5, 1, 1, 1)

        self.SearchGroupBoxLayout.addWidget(self.FindObjectButton, 6, 3, 1, 1, QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignRight)
    
        self.SearchGroupBoxLayout.setColumnStretch(1, 2)
        self.SearchGroupBoxLayout.setColumnStretch(2, 2)
        self.SearchGroupBoxLayout.setRowStretch(6, 2)
        self.SearchGroupBoxLayout.setContentsMargins(10,20,10,10)

        #Deactivate widgets where connection is required
        self.FilterComboBox.setEnabled(False)
        self.FindObjectButton.setEnabled(False)
        self.TableComboBox.setEnabled(False)
        self.ChangeLabelComboBox.setEnabled(False)
        self.ListClosedLabelsCheckBox.setEnabled(False)
        self.ObjectQueryTextEdit.setEnabled(False)

        self.SearchResultsGroupBox = QtWidgets.QGroupBox(self)
        self.SearchResultsGroupBox.setObjectName("SearchResultsGroupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.SearchResultsGroupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.SearchResultsTreeView = QtWidgets.QTreeView(self.SearchResultsGroupBox)
        self.SearchResultsTreeView.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragOnly)
        self.SearchResultsTreeView.setDefaultDropAction(QtCore.Qt.DropAction.IgnoreAction)
        self.SearchResultsTreeView.setAlternatingRowColors(True)
        self.SearchResultsTreeView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.SearchResultsTreeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)

        self.SearchResultsTreeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.SearchResultsTreeView.customContextMenuRequested.connect(self.onSearchResultsContextMenuRequested)

        # self.SearchResultsTreeView.setMovement(QtWidgets.QListView.Movement.Free)
        self.SearchResultsTreeView.setProperty("isWrapping", False)
        # self.SearchResultsTreeView.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.SearchResultsTreeView.setWordWrap(True)
        # self.SearchResultsTreeView.setItemAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.SearchResultsTreeView.setObjectName("SearchResultsTreeView")
        self.SearchResultsTreeView.dragMoveEvent = self.SearchResultsListDragMoveEvent
        self.SearchResultsTreeView.header().setVisible(False)
        
        self.verticalLayout_3.addWidget(self.SearchResultsTreeView)

        #Search Result list
        data_model = ObjectDataListModel(application=self.application, parent_widget=self.SearchResultsTreeView)
        self.SearchResultsTreeView.setModel(data_model)

        # Database Relations Widget
        self.DatabaseRelations = DatabaseRelations(self, self.application)
        
        # Results Management Tabwidget
        self.DatabaseQueryTabWidget = QtWidgets.QTabWidget(self.TemplateEditorSplitter_Search)
        self.DatabaseQueryTabWidget.setMovable(True)

        # self.DatabaseQueryTabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)

        self.DatabaseQueryTabWidget.setProperty("CustomTabWidget", "DatabaseQueryTabWidget")
        self.DatabaseQueryTabWidget.tabBar().setProperty("CustomTabWidget", "DatabaseQueryTabWidget")
        self.DatabaseQueryTabWidget.setObjectName("DatabaseQueryTabWidget")
        self.DatabaseQueryTabWidget.tabBar().setObjectName("DatabaseQueryTabWidget")

        # Configure Tabs
        self.DatabaseQueryTabWidget.addTab(self.SearchResultsGroupBox, "Search Results")
        self.DatabaseQueryTabWidget.addTab(self.DatabaseRelations, "Object Configuration")

        # self.TemplateEditorSplitter_Relations.addWidget(self.DatabaseRelations)
        self.DatabaseQueryTabWidget.setCurrentWidget(self.SearchResultsGroupBox)

        # XML Editor TabWidget
        self.XMLTemplateEditorTabWidget = QtWidgets.QTabWidget(self.TemplateEditorSplitter_Left)
        self.XMLTemplateEditorTabWidget.setTabsClosable(True)
        self.XMLTemplateEditorTabWidget.tabCloseRequested.connect(self.onTabWidgetClose)
        self.XMLTemplateEditorTabWidget.setMovable(True)
        self.XMLTemplateEditorTabWidget.setObjectName("XMLTemplateEditorTabWidget")
        self.XMLTemplateEditorTabWidget.tabBar().setObjectName("XMLTemplateEditorTabWidget")

        self.TemplateEditorSplitter_Search.setSizes(
            [round(self.application.height()*0.2), round(self.application.height()*0.8)]
            )
        
        self.TemplateEditorSplitter_Left.setSizes(
            [round(self.application.width()*0.2), round(self.application.width()*0.8)]
            )

        self.retranslateUi(self)

        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        self.SearchGroupBox.setTitle(_translate("Form", "Database Search Configuration"))
        self.TableComboBox.setPlaceholderText(_translate("Form", "Filter Database Tables here..."))
        self.ObjectQueryTextEdit.setPlaceholderText(_translate("Form", "Search Database Objects"))
        self.FindObjectButton.setText(_translate("Form", "Find Objects"))
        self.ChangesDateLabel.setText(_translate("Form", "Find new or changed objects since:"))
        self.UserChangesQuery.setPlaceholderText(_translate("Form", "Find only objects created or changed by system user.."))
        self.SearchResultsGroupBox.setTitle(_translate("Form", "Database Search Results"))
        self.IncludePartialResultsLabel.setText(_translate("Form", "Include Partial Results"))
        self.IncludePartialResultsLabel.setToolTip("Applies the query conditions also to tables\nwhich have only one type of field type available in schema (xUser, xDate).")

from PyQt6.QtWidgets import QComboBox, QCompleter
from PyQt6.QtCore import Qt, QSortFilterProxyModel

class ExtendedComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        # self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.view().installEventFilter(self)

    def eventFilter(self, source_object, event):
        # print(source_object, event)
        if event.type() == QtCore.QEvent.Type.KeyPress:
            
            self.setEnabled(False)
            self.setEnabled(True)

            self.lineEdit().clear()
            self.lineEdit().setFocus()

            self.on_completer_activated(event.text())
            self.lineEdit().event(event)
            return True
            
        return super().eventFilter(source_object, event)
        
    def setPlaceholderText(self, text):
        self.lineEdit().setPlaceholderText(text)

    # on selection of an item from the completer, select the corresponding item from combobox 
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            # self.currentIndexChanged.emit(index)


    # on model change, update the models of the filter and completer as well 
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)


    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)  