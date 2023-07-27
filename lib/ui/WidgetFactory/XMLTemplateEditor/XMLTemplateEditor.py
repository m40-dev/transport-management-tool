from PyQt6 import QtCore, QtWidgets
from .XMLTemplateEditorWidget import XMLTemplateEditorWidget
from .DatabaseRelations import DatabaseRelations
from pathlib import Path
XML_PREVIEW_TIMER = 100

class XMLTemplateEditor(QtWidgets.QWidget):
    refresh_xml_widget = QtCore.pyqtSignal()
    current_file_changed = QtCore.pyqtSignal(str)

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.setupUi()
        self.current_file_changed.connect(self.selectXMLTemplateTab)

        # Database Relations Handling
        self.DatabaseRelations = DatabaseRelations(self, self.application)

    def newTransportTemplate(self, file_path=None):
        tabWidget = XMLTemplateEditorWidget(self, self.application, file_path)
        tab_name = "New Template"
        if file_path:
            tab_name = Path(file_path).name
        index = self.XMLTemplateEditorTabWidget.addTab(tabWidget, tab_name)
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

    
    def selectXMLTemplateTab(self, file_path):
        for index in range(0, self.XMLTemplateEditorTabWidget.count()):
            tab_widget = self.XMLTemplateEditorTabWidget.widget(index)
            print(tab_widget, "search for tab with file path:", file_path, "found:", tab_widget.current_file)
            if file_path and tab_widget.current_file and file_path.lower() == tab_widget.current_file.lower():
                print("existing tab widget found", tab_widget.current_file)
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

    def saveXMLTemplate(self):
        current_tab = self.XMLTemplateEditorTabWidget.currentWidget()
        current_tab.saveXMLTemplate()

    def saveXMLTemplateAs(self, initial_directory=None):
        current_tab = self.XMLTemplateEditorTabWidget.currentWidget()
        current_tab.saveXMLTemplateAs(initial_directory)

    def refresh_ui(self):
        self.TableComboBox.clear()
        if self.application.db and self.application.db.is_connected:
            self.FindObjectButton.setEnabled(True)
            self.TableComboBox.setEnabled(True)
            for table_name in self.application.db.table_info.keys():
                self.TableComboBox.addItem(table_name)
        self.refresh_xml_widget.emit()

    def setupUi(self):
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.TemplateEditorSplitter_Left = QtWidgets.QSplitter(self)
        self.gridLayout.addWidget(self.TemplateEditorSplitter_Left, 0, 0, 1, 1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.TemplateEditorSplitter_Left.setSizePolicy(sizePolicy)
        self.TemplateEditorSplitter_Left.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.TemplateEditorSplitter_Left.setObjectName("TemplateEditorSplitter_Left")
        self.TemplateEditorSplitter_Relations = QtWidgets.QSplitter(self.TemplateEditorSplitter_Left)
        self.TemplateEditorSplitter_Relations.setSizePolicy(sizePolicy)
        self.TemplateEditorSplitter_Relations.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.TemplateEditorSplitter_Relations.setObjectName("TemplateEditorSplitter_Relations")
        self.TemplateEditorSplitter_Search = QtWidgets.QSplitter(self.TemplateEditorSplitter_Relations)
        self.TemplateEditorSplitter_Search.setSizePolicy(sizePolicy)
        self.TemplateEditorSplitter_Search.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.TemplateEditorSplitter_Search.setObjectName("TemplateEditorSplitter_Search")
        self.SearchGroupBox = QtWidgets.QGroupBox(self.TemplateEditorSplitter_Search)
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
        self.ObjectQueryTextEdit.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
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

        # Database Relations Widget
        self.DatabaseRelations = DatabaseRelations(self, self.application)
        self.TemplateEditorSplitter_Relations.addWidget(self.DatabaseRelations)

        # XML Editor TabWidget
        self.XMLTemplateEditorTabWidget = QtWidgets.QTabWidget(self.TemplateEditorSplitter_Left)
        self.XMLTemplateEditorTabWidget.setTabsClosable(True)

        self.TemplateEditorSplitter_Search.setSizes(
            [round(self.application.height()*0.1), round(self.application.height()*0.7)]
            )

        self.TemplateEditorSplitter_Relations.setSizes(
            [round(self.application.height()*0.7), round(self.application.height()*0.4)]
            )
        
        self.TemplateEditorSplitter_Left.setSizes(
            [round(self.application.width()*0.3), round(self.application.width()*0.7)]
            )

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

