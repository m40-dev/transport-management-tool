from PyQt6 import QtCore, QtWidgets
from .ExecutionPlanner import ExecutionPlannerWidget
from ...WidgetFactory import MsgBox
from pathlib import Path
import json
from lib.data.DataModels import PackageDefinitionModel
from .PackageViewDelegate import PackageViewDelegate
from .ContextMenu import PackageDefinitionMenu

FILTER_EXEC_TIMER = 650

class PackageManager(QtWidgets.QWidget):

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.object_configuration = self.application.object_configuration
        self.program_configuration = self.application.program_configuration
        self.current_workdir = None

        self.setupUi()

        # Package Tree View and Navigation
        self.PackageViewTreeView.dragMoveEvent = self.PackageViewDragMoveEvent
        self.PackageViewTreeView.setHeaderHidden(True)
        self.PackageViewTreeView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.PackageViewTreeView.setDragEnabled(True)
        self.PackageViewTreeView.setAcceptDrops(True)
        self.PackageViewTreeView.setUniformRowHeights(False)
        self.PackageViewTreeView.setDropIndicatorShown(True)
        self.PackageViewTreeView.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragDrop)
        self.PackageViewTreeView.setAlternatingRowColors(False)
        self.PackageViewTreeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

        self.PackageManagerSplitter.setSizes(
            [round(self.application.width()*0.3), round(self.application.width()*0.7)])

        # Context Menu
        self.PackageViewTreeView.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.PackageViewTreeView.customContextMenuRequested.connect(self.contextMenuRequested)

        self.FindPackageButton.clicked.connect(self.queryPackages)
        self.AddPackageButton.clicked.connect(self.addPackageDefinition)

        # Execution Planner Tabs
        self.ExecutionPlannerTabWidget.setTabsClosable(True)
        self.ExecutionPlannerTabWidget.tabCloseRequested.connect(self.closeExecutionPlan)

        # Filter Delay Timer
        self.queryPackagesTimer = QtCore.QTimer(self)
        self.queryPackagesTimer.setSingleShot(True)
        self.queryPackagesTimer.timeout.connect(self.queryPackages)

    """ Workdir and File Operations """
    def changeWorkingDirectory(self):
        dialog = QtWidgets.QFileDialog(self, "Transport Manager - Select Working Directory")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)

        file_path = dialog.getExistingDirectory(options=QtWidgets.QFileDialog.Option.ReadOnly)
        if file_path != "":
            self.current_workdir = file_path
            self.application.current_workdir = file_path
            self.loadWorkingDirectory(file_path)
            return True
        return False
    
    def loadWorkingDirectory(self, workdir=None):
        if workdir is None and self.current_workdir is not None:
            workdir = self.current_workdir
        
        if workdir is None:
            return False
        
        self.setupWorkingDirectory(workdir)
        self.application.ui.MainTabWidget.setCurrentWidget(self)

    def setupWorkingDirectory(self, workdir):
        sort_attribute = ""
        package_definition_config = self.object_configuration.get("PackageManager_PackageDefinition")
        mandatory_columns = []
        if package_definition_config:
            for column, column_configuration in package_definition_config.items():
                if column_configuration.get("FieldRole", None) == "SortOrder":
                    sort_attribute = column
                    break
            
            if len(sort_attribute.strip()) == 0:
                for column, column_configuration in package_definition_config.items():
                    if column_configuration.get("FieldRole", None) == "DisplayRole":
                        sort_attribute = column
                        break

            for column, column_configuration in package_definition_config.items():
                    if column_configuration.get("IsMandatory", None) == "True":
                        mandatory_columns.append(column)
        sort_attribute = sort_attribute.strip()
        
        workdir_path = Path(workdir).absolute()
        definitions = []
        skipped_definitions = []
        package_manager_configuration = self.program_configuration.get("Package Manager")
        whitelist_directories = package_manager_configuration.get("WorkdirDirectoryWhitelist", None)

        for file_path in Path(workdir).rglob( '*.json' ):
            if file_path.is_file():
                feature_definition_location = file_path.relative_to(workdir_path)
                accept = True

                if package_manager_configuration and accept:
                    if whitelist_directories:
                        accept = False
                        for directory in whitelist_directories:
                            # print(f"checking whitelist, {str(feature_definition_location)} compared with whitelist directory: {directory}", str(feature_definition_location).lower().startswith(directory.lower()))
                            if str(feature_definition_location).lower().startswith(directory.lower()):
                                accept = True

                    excluded_files = package_manager_configuration.get("ExcludedFiles", None)
                    if excluded_files and feature_definition_location.name in excluded_files:
                        accept = False
                    
                    if accept:
                        blacklist_directories = package_manager_configuration.get("WorkdirDirectoryBlacklist", None)
                        for directory in blacklist_directories:
                            if str(feature_definition_location).startswith(directory):
                                accept = False
                    if not accept:
                        # program configuration excluded the file, continue
                        continue
                
                #file went through the whitelist/blacklist configurations
                json_content = self.application.load_file(file_path.absolute())
                package_definition = json.loads(json_content)
                
                #keep relative path by default
                package_definition["DefinitionFile"] = str(feature_definition_location)

                definition_config = self.object_configuration.get_column_configuration("PackageManager_PackageDefinition", "DefinitionFile")
                if definition_config and definition_config.get("FileSelectionMode", "") == "FileName":
                    #keep just the file name, location to be calculated dynamically
                    package_definition["DefinitionFile"] = str(feature_definition_location.name)
                # check the mandatory fields of the object to determine if file matches the definition

                # check the definition file mandatory columns
                for column_name in mandatory_columns:
                    if column_name not in package_definition.keys():
                        #skip entry with missing mandatory definition data
                        accept = False
                        break

                if accept and len(sort_attribute) > 0 and sort_attribute not in package_definition.keys():
                    package_definition[sort_attribute] = -1
                
                if accept:
                    definitions.append(package_definition)
                else:
                    skipped_definitions.append(str(package_definition))
        
        if len(sort_attribute) > 0:
            definitions = sorted(
                    definitions, 
                    key=lambda d: (d[sort_attribute])
                    )

        data_model =  PackageDefinitionModel(
            application=self.application,
            parent_widget=self.PackageViewTreeView, 
            data=definitions)
        
        packageViewDelegate = PackageViewDelegate(
            model_data=data_model, 
            application=self.application, 
            parent_widget=self.PackageViewTreeView,
            package_manager=self)

        self.PackageViewTreeView.setItemDelegate(packageViewDelegate)
        self.PackageViewTreeView.setModel(data_model)

        self.SearchPackageLineEdit.textChanged.connect(self.queryPackages)
        
        # Show the summary of skipped data files
        if len(skipped_definitions)>0:
            definition_list = "\r\n".join(skipped_definitions)
            file_count = len(skipped_definitions)
            MsgBox(self.application, "Some JSON definition files were ignored due to missing mandatory data.\r\nIf this file should be ignored, please configure the filters in program configuration.", 
                f"Mandatory columns: {mandatory_columns}.\r\nSkipped Entries: {file_count}, skipped data:\r\n{definition_list}")

    def addExecutionPlan(self):
        tabwidget = ExecutionPlannerWidget(self, self.application)
        tabwidget.plannerNameChanged.connect(self.setPlannerName)
        self.ExecutionPlannerTabWidget.addTab(tabwidget, "New Execution Plan...")

    def setPlannerName(self, planner_widget):
        index = self.ExecutionPlannerTabWidget.indexOf(planner_widget)
        planner_name = planner_widget.name
        self.ExecutionPlannerTabWidget.setTabText(index, planner_name)

    def closeExecutionPlan(self, index):
        tab_widget = self.ExecutionPlannerTabWidget.widget(index)
        tab_widget.parent = None
        tab_widget.deleteLater()
        self.ExecutionPlannerTabWidget.removeTab(index)

    """ Package Definition Management """
    def contextMenuRequested(self, menuPosition):
        clickedIndex = self.PackageViewTreeView.indexAt(menuPosition)
        contextMenu = PackageDefinitionMenu(self, clickedIndex)
       
        menu_target = self.PackageViewTreeView.mapToGlobal(menuPosition)

        contextMenu.addPackageDefinition.connect(self.addPackageDefinition)
        contextMenu.editPackageDefinition.connect(self.editPackageDefinition)
        contextMenu.addTaskDefinition.connect(self.addTaskDefinition)
        contextMenu.editTaskDefinition.connect(self.editTaskDefinition)
        contextMenu.editXMLTemplate.connect(self.editXMLTemplate)
        contextMenu.savePackageDefinition.connect(self.savePackageDefinition)
        contextMenu.collapseAll.connect(self.collapseAll)
        contextMenu.expandAll.connect(self.expandAll)

        if len(contextMenu.menu_items) > 0:
            contextMenu.popup(menu_target)

    def addPackageDefinition(self):
        if not self.current_workdir:
            MsgBox(self.application, "Working Directory is not configured.\n\nPlease configure working directory location first to create any package definition.\n\nWithout working directory, program will not be able to generate the paths and save the files.")
            if not self.changeWorkingDirectory():
                return False
        
        form_data = self.application.getObjectData("PackageManager_PackageDefinition", "Add Package Definition")
        if form_data:
            treeview_model = self.PackageViewTreeView.model()
            if treeview_model:
                treeview_model.insert_item("PackageManager_PackageDefinition", form_data)

    def editPackageDefinition(self, source_index):
        print("Edit Package Definition", source_index)
        if not source_index.isValid():
            return False

        form_data = self.application.getObjectData("PackageManager_PackageDefinition", "Edit Package Definition", source_index)
        if form_data:
            source_item = source_index.internalPointer()
            source_item.update_data(form_data)

    def savePackageDefinition(self, source_index, save_single=False):
        if not self.current_workdir:
            MsgBox(self.application, "Working directory is not set. Please configure the work location first.")
            return False

        if len(self.PackageViewTreeView.selectedIndexes()) > 0 and not save_single:
            for item_index in self.PackageViewTreeView.selectedIndexes():
                package_definition = item_index.internalPointer()
                package_definition.save()
        else:
            if source_index.isValid():
                package_definition = source_index.internalPointer()
                package_definition.save()

    def addTaskDefinition(self, source_index):
        print("add task definition for", source_index)
        if not source_index.isValid():
            return False

        form_data = self.application.getObjectData("PackageManager_TaskDefinition", "Add Task Definition")
        if form_data:
            treeview_model = self.PackageViewTreeView.model()
            if treeview_model:
                treeview_model.insert_item("PackageManager_TaskDefinition", form_data, source_index)
    
    def editTaskDefinition(self, source_index):
        if not source_index.isValid():
            return False

        form_data = self.application.getObjectData("PackageManager_TaskDefinition", "Edit Task Definition", source_index)
        if form_data:
            source_item = source_index.internalPointer()
            source_item.update_data(form_data)

    def editXMLTemplate(self, source_item):
        source_item = source_item.internalPointer()
        file_path = source_item.get_file_path()
        if not file_path.is_file():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
        self.application.XMLTemplateEditor.openXMLTemplate(str(file_path))

    def collapseAll(self):
        self.PackageViewTreeView.collapseAll()

    def expandAll(self):
        self.PackageViewTreeView.expandAll()

    def queryPackages(self, text=None):
        if text:
            self.queryPackagesTimer.start(FILTER_EXEC_TIMER)
            return False
        #filter from the other signals
        filter_text = self.SearchPackageLineEdit.text()
        data_model = self.PackageViewTreeView.model()
        if data_model:
            data_model.setFilterString(filter_text)

    def deleteSelectedItems(self):
        if self.PackageViewTreeView.hasFocus():
            return self.deletePackageDefinitions()
        
        #remove active execution planner items
        self.ExecutionPlannerTabWidget.currentWidget().deleteSelectedItems()

    def deletePackageDefinitions(self):

        question = MsgBox(self.application, 
                        message=f"Do you want to delete selected items? ({len(self.PackageViewTreeView.selectedIndexes())} item(s))",
                        window_mode=MsgBox.QUESTION)
        if question.accepted:
            files_to_delete = {}
            for item_index in self.PackageViewTreeView.selectedIndexes():
                item = item_index.internalPointer()
                if self.current_workdir:
                    # attempt file operations only if the workdir is set
                    files_to_delete = item.get_all_files(recursive=True)
                    if len(files_to_delete) > 0:
                        export_data = "\n".join(map(str, files_to_delete))
                        # export_data = json.dumps(files_to_delete, indent=4, separators=(',',':'))
                        detailed_message = f"Data lookup returned following files related to the selected object:\n{export_data}"
                        question = MsgBox(self.application, 
                            message=f"Existing system files detected for item {item.display} or its child items, do you also want to delete these data files?", 
                            detailed_message=detailed_message, 
                            window_mode=MsgBox.QUESTION)
                        if question.accepted:
                            #delete data files
                            for file_path in files_to_delete:
                                self.deleteFile(file_path)
                #remove item from model
                item_index.model().remove_item(item)
        return True

    def deleteFile(self, file_path):
        print("file to delete", file_path)
        file_path = Path(str(file_path))
        if file_path.is_file():
            file_path.unlink()
            parent_directory = file_path.parent
            self.deleteDirectory(parent_directory)

    def deleteDirectory(self, directory_path):
        print("check if directory can be deleted:", directory_path)
        if not self.current_workdir:
            # do not delete anything if there is no working directory
            return False

        workdir_path = Path(str(self.current_workdir))
        if directory_path.absolute() <= workdir_path.absolute():
            # never go beyond the working directory
            print("do not cross the working directory, breaking")
            return False

        if len(list(directory_path.rglob('*'))) == 0:
            # print("delete empty directory:", directory_path)
            directory_path.rmdir()
            if directory_path.parent:
                self.deleteDirectory(directory_path.parent)

    def PackageViewDragMoveEvent(self, event):
        move_accept = False
        source_index = event.source().currentIndex()
        source_item = source_index.internalPointer()

        QtWidgets.QTreeView.dragMoveEvent(self.PackageViewTreeView, event)
        
        drop_index = self.PackageViewTreeView.indexAt(event.position().toPoint())
        drop_item = drop_index.internalPointer()

        dropIndicator = self.PackageViewTreeView.dropIndicatorPosition()

        if drop_item:
            self.PackageViewTreeView.setDropIndicatorShown(True)

        if dropIndicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.OnItem:

            if drop_item._task_class != source_item._task_class:
                move_accept = True
            
            if drop_item and source_item:
                #do not allow package nesting
                if source_item._task_class == "PackageManager_PackageDefinition" and drop_item._task_class == "PackageManager_TaskDefinition":
                    move_accept = False

        if dropIndicator in [QtWidgets.QAbstractItemView.DropIndicatorPosition.BelowItem, QtWidgets.QAbstractItemView.DropIndicatorPosition.AboveItem]:
            if drop_item._task_class == source_item._task_class:
                move_accept = True

        if drop_item is None:
            # no target item - drop at top level
            if source_item._task_class == "PackageManager_PackageDefinition":
                move_accept = True

        if event.mimeData().hasFormat("application/vnd.jsondataitem") and move_accept:
            event.acceptProposedAction()
        else:
            event.ignore()

    def setupUi(self):
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.PackageManagerSplitter = QtWidgets.QSplitter(self)
        self.PackageManagerSplitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.PackageManagerSplitter.setObjectName("PackageManagerSplitter")
        self.verticalLayoutWidget_5 = QtWidgets.QWidget(self.PackageManagerSplitter)
        self.verticalLayoutWidget_5.setObjectName("verticalLayoutWidget_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.SearchPackageLineEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget_5)
        self.SearchPackageLineEdit.setToolTipDuration(1)
        self.SearchPackageLineEdit.setObjectName("SearchPackageLineEdit")
        self.horizontalLayout_4.addWidget(self.SearchPackageLineEdit)
        self.FindPackageButton = QtWidgets.QToolButton(self.verticalLayoutWidget_5)
        self.FindPackageButton.setObjectName("FindPackageButton")
        self.horizontalLayout_4.addWidget(self.FindPackageButton)
        self.AddPackageButton = QtWidgets.QToolButton(self.verticalLayoutWidget_5)
        self.AddPackageButton.setObjectName("AddPackageButton")
        self.horizontalLayout_4.addWidget(self.AddPackageButton)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.PackageViewTreeView = QtWidgets.QTreeView(self.verticalLayoutWidget_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PackageViewTreeView.sizePolicy().hasHeightForWidth())
        self.PackageViewTreeView.setSizePolicy(sizePolicy)
        self.PackageViewTreeView.setAlternatingRowColors(True)
        self.PackageViewTreeView.setWordWrap(True)
        self.PackageViewTreeView.setObjectName("PackageViewTreeView")
        self.PackageViewTreeView.header().setDefaultSectionSize(39)
        self.verticalLayout_5.addWidget(self.PackageViewTreeView)
        self.ExecutionPlannerTabWidget = QtWidgets.QTabWidget(self.PackageManagerSplitter)
        self.ExecutionPlannerTabWidget.setTabsClosable(False)
        self.ExecutionPlannerTabWidget.setMovable(True)
        self.ExecutionPlannerTabWidget.setObjectName("ExecutionPlannerTabWidget")
        self.gridLayout.addWidget(self.PackageManagerSplitter, 0, 0, 1, 1)

        self.retranslateUi(self)
        self.ExecutionPlannerTabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.SearchPackageLineEdit.setToolTip(_translate("Form", "Search Transport Package"))
        self.SearchPackageLineEdit.setPlaceholderText(_translate("Form", "Search Transport Package"))
        self.FindPackageButton.setText(_translate("Form", "Find"))
        self.AddPackageButton.setText(_translate("Form", "Add"))
