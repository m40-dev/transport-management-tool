from PyQt6 import QtCore, QtWidgets
from .XMLTemplateEditorWidget import XMLTemplateEditorWidget
from .DatabaseRelations import DatabaseRelations
from lib.data.DataModels.XMTemplateEditor import ObjectDataListModel, XMLDataItem
from copy import deepcopy

XML_PREVIEW_TIMER = 100
SEARCH_FILTER_OPTIONS = {
    "TableQuery" : "Select from Database Table",
    "ChangeLabel": "Select by Change Label",
    "XObjectKeyQuery": "Find Objects by XObjectKey"
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
    
        self.setupUi()
        self.current_file_changed.connect(self.selectXMLTemplateTab)

        #Connect Signals

        # Database Relations Handling
        self.TableComboBox.currentTextChanged.connect(self.queryDatabaseObjects)
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

        self.ChangeLabelComboBox.setVisible(option in ["ChangeLabel"])
        self.ListClosedLabelsCheckBox.setVisible(option in ["ChangeLabel"])

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
            self.ObjectQueryTextEdit.clear()
        
        if table_name != self.TableComboBox.currentText():
            self.TableComboBox.setCurrentText(table_name)
        else:
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

    def queryDatabaseObjects(self, table_name=None):
        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()
        
        object_filter = self.ObjectQueryTextEdit.toPlainText()
        data_rows = []

        if self.query_option == "XObjectKeyQuery":
            filter_rows = object_filter.splitlines()
            query_data = self.application.db.get_objects_by_xobjectkey(filter_rows)
            for table_name, object_data_rows in query_data.items():
                data_rows += object_data_rows
            
            self.listTableObjects(table_name=table_name, data_rows=data_rows)
        
        if self.query_option == "TableQuery" and self.TableComboBox.currentText().strip() != "":
            if not table_name:
                table_name = self.TableComboBox.currentText().strip()

            self.listTableObjects(table_name=table_name)

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

        # print(f"table data loaded, {table_name} - ({len(data_rows)})")
        self.SearchResultsListView.model().tableNameInDisplay = False
        self.SearchResultsListView.model().reloadModelData(data_rows)

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
        if self.application.db and self.application.db.is_connected:
            self.FilterComboBox.setEnabled(True)
            self.FindObjectButton.setEnabled(True)
            self.TableComboBox.setEnabled(True)
            self.ChangeLabelComboBox.setEnabled(True)
            self.ListClosedLabelsCheckBox.setEnabled(True)
            self.ObjectQueryTextEdit.setEnabled(True)

            for table_name in self.application.db.table_info.keys():
                self.TableComboBox.addItem(table_name)
            self.reloadChangeLabels()

    def reloadChangeLabels(self):
        self.ChangeLabelComboBox.clear()
        label_states = self.ListClosedLabelsCheckBox.isChecked()
        change_labels = self.application.db.get_change_labels(label_states)
        for data_row in change_labels:
            display_name = self.application.db.get_object_display_name("DialogTag", data_row)
            self.ChangeLabelComboBox.addItem(display_name, data_row.UID_DialogTag)
            # print(display_name, data_row.UID_DialogTag)
        self.ChangeLabelComboBox.model().sort(0)

    def listChangeLabelObjects(self, current_index):
        selected_label_uid = self.ChangeLabelComboBox.itemData(current_index)

        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()
        
        data_rows = []

        label_data = self.application.db.get_objects_by_change_label(selected_label_uid)
        for table_name, label_data_rows in label_data.items():
            data_rows += label_data_rows
        self.SearchResultsListView.model().tableNameInDisplay = True
        self.SearchResultsListView.model().reloadModelData(data_rows)

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

    def onDatabaseQueryConditionsChanged(self):
        print("database query control changed")

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
        
        # self.TemplateEditorSplitter_Relations = QtWidgets.QSplitter(self.TemplateEditorSplitter_Left)
        # self.TemplateEditorSplitter_Relations.setSizePolicy(sizePolicy)
        # self.TemplateEditorSplitter_Relations.setOrientation(QtCore.Qt.Orientation.Vertical)
        # self.TemplateEditorSplitter_Relations.setObjectName("TemplateEditorSplitter_Relations")
        
        self.TemplateEditorSplitter_Search = QtWidgets.QSplitter(self.TemplateEditorSplitter_Left)
        self.TemplateEditorSplitter_Search.setSizePolicy(sizePolicy)
        self.TemplateEditorSplitter_Search.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.TemplateEditorSplitter_Search.setObjectName("TemplateEditorSplitter_Search")

        # Search GroupBox Widgets Preparation
        
        # self.gridLayout.addWidget(search_dockWidget, 0, 0, 1, 1)
        self.SearchGroupBox = QtWidgets.QGroupBox(self.TemplateEditorSplitter_Search)
        self.SearchGroupBox.setSizePolicy(sizePolicy)
        self.SearchGroupBox.setObjectName("SearchGroupBox")

        self.SearchGroupBoxLayout = QtWidgets.QGridLayout(self.SearchGroupBox)
        self.SearchGroupBoxLayout.setObjectName("SearchGroupBoxLayout")

        self.FilterComboBox = QtWidgets.QComboBox(self.SearchGroupBox)
        
        for option_key, display_name in SEARCH_FILTER_OPTIONS.items():
            self.FilterComboBox.addItem(display_name, option_key)

        self.TableComboBox = QtWidgets.QComboBox(self.SearchGroupBox)
        self.TableComboBox.setObjectName("TableComboBox")
        self.ObjectQueryTextEdit = QtWidgets.QTextEdit(self.SearchGroupBox)
        self.ObjectQueryTextEdit.setTabChangesFocus(False)
        self.ObjectQueryTextEdit.setAcceptRichText(False)
        self.ObjectQueryTextEdit.setObjectName("ObjectQueryTextEdit")
        self.ObjectQueryTextEdit.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)

        self.FindObjectButton = QtWidgets.QToolButton(self.SearchGroupBox)
        self.FindObjectButton.setObjectName("FindObjectButton")

        start_icon = self.ProgramConfiguration.getIcon("RunQuery")
        if start_icon:
            self.FindObjectButton.setText("")
            self.FindObjectButton.setToolTip("<i>Run Query..</i>")
            self.FindObjectButton.setIcon(start_icon)
            self.FindObjectButton.setIconSize(QtCore.QSize(20, 20))
            self.FindObjectButton.setProperty("Widget", "CustomToolButton")

        self.ChangeLabelComboBox = QtWidgets.QComboBox()
        self.ChangeLabelComboBox.setPlaceholderText("Select Objects by Change Label")
        self.ListClosedLabelsCheckBox = QtWidgets.QCheckBox("Show All\nLabels")
        
        #Search GroupBox Layout Configuration

        self.SearchGroupBoxLayout.addWidget(self.FilterComboBox, 0, 0, 1, 3)
        self.SearchGroupBoxLayout.addWidget(self.TableComboBox, 1, 0, 1, 3)

        self.SearchGroupBoxLayout.addWidget(self.ChangeLabelComboBox, 2, 0, 1, 1)
        self.SearchGroupBoxLayout.addWidget(self.ListClosedLabelsCheckBox, 2, 1, 1, 2, QtCore.Qt.AlignmentFlag.AlignRight)
        self.SearchGroupBoxLayout.addWidget(self.ObjectQueryTextEdit, 3, 0, 1, 3)
        self.SearchGroupBoxLayout.addWidget(self.FindObjectButton, 3, 2, 1, 1, QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignBottom)

        self.SearchGroupBoxLayout.setColumnStretch(0, 2)
        self.SearchGroupBoxLayout.setRowStretch(3, 2)

        #Deactivate widgets where connection is required
        self.FilterComboBox.setEnabled(False)
        self.FindObjectButton.setEnabled(False)
        self.TableComboBox.setEnabled(False)
        self.ChangeLabelComboBox.setEnabled(False)
        self.ListClosedLabelsCheckBox.setEnabled(False)
        self.ObjectQueryTextEdit.setEnabled(False)

        self.SearchResultsGroupBox = QtWidgets.QGroupBox(self)

        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.SearchResultsGroupBox.sizePolicy().hasHeightForWidth())
        # self.SearchResultsGroupBox.setSizePolicy(sizePolicy)
        self.SearchResultsGroupBox.setObjectName("SearchResultsGroupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.SearchResultsGroupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.SearchResultsListView = QtWidgets.QListView(self.SearchResultsGroupBox)
        self.SearchResultsListView.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragOnly)
        self.SearchResultsListView.setDefaultDropAction(QtCore.Qt.DropAction.IgnoreAction)
        self.SearchResultsListView.setAlternatingRowColors(True)
        self.SearchResultsListView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.SearchResultsListView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        self.SearchResultsListView.setMovement(QtWidgets.QListView.Movement.Free)
        self.SearchResultsListView.setProperty("isWrapping", False)
        # self.SearchResultsListView.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.SearchResultsListView.setWordWrap(True)
        self.SearchResultsListView.setItemAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.SearchResultsListView.setObjectName("SearchResultsListView")
        self.SearchResultsListView.dragMoveEvent = self.SearchResultsListDragMoveEvent
        self.verticalLayout_3.addWidget(self.SearchResultsListView)

        #Search Result list
        data_model = ObjectDataListModel(application=self.application, parent_widget=self.SearchResultsListView)
        self.SearchResultsListView.setModel(data_model)

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
        self.DatabaseQueryTabWidget.addTab(self.DatabaseRelations, "Relations Configuration")
        self.DatabaseQueryTabWidget.addTab(self.SearchResultsGroupBox, "Search Results")

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
        self.SearchGroupBox.setTitle(_translate("Form", "Search"))
        self.TableComboBox.setPlaceholderText(_translate("Form", "Select From Table"))
        self.ObjectQueryTextEdit.setPlaceholderText(_translate("Form", "Search Database Objects"))
        # self.XObjectKeysFilterRadioButton.setText(_translate("Form", "List of XObjectKeys"))
        # self.SelectedTableFilterRadioButton.setText(_translate("Form", "Selected Table Filter"))
        self.FindObjectButton.setText(_translate("Form", "Find Objects"))
        self.SearchResultsGroupBox.setTitle(_translate("Form", "Search Results"))

