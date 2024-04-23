from PyQt6 import QtCore, QtWidgets, QtGui
from .ExecutionPlanner import ExecutionPlannerWidget
from ...WidgetFactory import MsgBox
from pathlib import Path
import json
from lib.data.DataModels import PackageDefinitionModel
from .PackageViewDelegate import PackageViewDelegate
from .ContextMenu import PackageDefinitionMenu
from ..DialogScreens.MultiObjectEditorForm import MultiObjectEditorForm
from timeit import default_timer as timer
from time import sleep
from datetime import timedelta

FILTER_EXEC_TIMER = 650

class PackageManager(QtWidgets.QWidget):
    uiRefreshRequested = QtCore.pyqtSignal()
    
    def __init__(self, application):
        super().__init__()
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self.current_workdir = None
        self.WorkdirLoader = None
        self.setupUi()
        self.setupViewDelegate()

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
        self.PackageViewTreeView.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.SearchPackageLineEdit.textChanged.connect(self.queryPackages)

        self.PackageManagerSplitter.setSizes(
            [round(self.application.width()*0.3), round(self.application.width()*0.7)])

        # Context Menu
        self.PackageViewTreeView.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.PackageViewTreeView.customContextMenuRequested.connect(self.contextMenuRequested)

        # self.FindPackageButton.clicked.connect(self.queryPackages)
        self.AddPackageButton.clicked.connect(self.addPackageDefinition)

        # Execution Planner Tabs
        self.ExecutionPlannerTabWidget.setTabsClosable(True)
        self.ExecutionPlannerTabWidget.tabCloseRequested.connect(self.closeExecutionPlan)

        # Filter Delay Timer
        self.queryPackagesTimer = QtCore.QTimer(self)
        self.queryPackagesTimer.setSingleShot(True)
        self.queryPackagesTimer.timeout.connect(self.queryPackages)

    def refresh_ui(self):
        self.setStyleSheet(self.ProgramConfiguration.styleSheet())
        self.uiRefreshRequested.emit()

    # def showEvent(self, event):
    #     self.animate()
    
    # def hideEvent(self, event):
    #     self.animate(reverse=True)

    # def animate(self, reverse=False):
    #     # animate startup
        
    #     effect = QtWidgets.QGraphicsOpacityEffect(self)
    #     self.setGraphicsEffect(effect)

    #     animation = QtCore.QPropertyAnimation(self)

    #     animation.setPropertyName(bytes("opacity", "utf-8"))
    #     animation.setTargetObject(effect)
    #     animation.setDuration(250)
    #     animation.setStartValue(0)
    #     animation.setEndValue(1)

    #     if reverse:
    #         animation.setStartValue(1)
    #         animation.setEndValue(0)
    #         animation.setDuration(200)
        
    #     animation.setEasingCurve(QtCore.QEasingCurve.Type.OutInCubic)
    #     animation.start(QtCore.QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    #     animation.finished.connect(lambda: self.setGraphicsEffect(None))

    """ Workdir and File Operations """
    def changeWorkingDirectory(self):
        dialog = QtWidgets.QFileDialog(self, "Transport Manager - Select Working Directory")
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)

        file_path = dialog.getExistingDirectory(options=QtWidgets.QFileDialog.Option.ReadOnly)
        if file_path != "":
            self.loadWorkingDirectory(file_path)
            return True
        return False
    
    def loadWorkingDirectory(self, workdir=None):
        if workdir is None and self.current_workdir is not None:
            workdir = self.current_workdir
        
        if workdir is None:
            return False
        
        self.setupWorkingDirectory(workdir)
        # self.application.ui.MainTabWidget.setCurrentWidget(self)

    def setupWorkingDirectory(self, workdir):
        self.current_workdir = workdir
        self.application.current_workdir = workdir
        # Check existing worker status
        if self.WorkdirLoader:
            # print("worker existing, clearing queue", self.WorkdirLoader.isRunning)
            #if it exists, clear definitions queue manually so it shuts down
            self.WorkdirLoader.definitions = {}
        
        # Clear model data
        self.setupModelData(
            data={},
            application=self.application,
            treeview=self.PackageViewTreeView,
            package_manager=self)

        # Create new worker for the workdir
        self.WorkdirLoader = PMWorker(
            application=self.application,
            treeview=self.PackageViewTreeView,
            package_manager=self,
            workdir = workdir
        )

        # Connect output signals
        self.WorkdirLoader.dataLoaded.connect(self.appendModelData)
        self.WorkdirLoader.workdirLoaded.connect(self.onWorkdirFilesLoaded)

        # Move worker to new thread
        workdirLoaderThread = QtCore.QThread(self)
        self.WorkdirLoader.moveToThread(workdirLoaderThread)
        
        # Connect operational signals
        workdirLoaderThread.started.connect(self.WorkdirLoader.loadWorkingDirectory)
        self.WorkdirLoader.finished.connect(workdirLoaderThread.quit)
        self.WorkdirLoader.finished.connect(self.WorkdirLoader.deleteLater)
        workdirLoaderThread.finished.connect(workdirLoaderThread.deleteLater)

        # Start worker thread
        workdirLoaderThread.start()

    def onWorkdirFilesLoaded(self, loaded_definitions, skipped_definitions, mandatory_columns):
        # Show the summary of skipped data files
        # print("definitions loaded:",len(loaded_definitions), "definitions skipped:", len(skipped_definitions), "mandatory columns checked:", mandatory_columns )
        if len(skipped_definitions)>0:
            definition_list = "\r\n\t".join(skipped_definitions)
            file_count = len(skipped_definitions)
            MsgBox(application=self.application, 
                window_title="Workdir Loading Errors",
                message="Some JSON definition files were ignored due to <b>missing mandatory data.</b><br>If this file should be ignored, please configure the filters in program configuration.", 
                detailed_message=f"<b>Mandatory columns checked:</b> <i>{mandatory_columns}</i>.\r\n<b>Skipped Entries:</b> <i>{file_count}</i>.\r\n<b>Skipped files (workdir relative):</b>\r\n\t{definition_list}")
        
        self.application.statusBarUpdated.emit("Workspace initialization completed.")

    def setupViewDelegate(self):
        # print("Setup Model data finished")
        # start_time = timer()
        data_model = self.PackageViewTreeView.model()
        if not data_model:
            data_model =  PackageDefinitionModel(
                application=self.application,
                parent_widget=self.PackageViewTreeView, 
                data={})

        packageViewDelegate = PackageViewDelegate(
            model_data=data_model, 
            application=self.application, 
            parent_view=self.PackageViewTreeView,
            parent_module=self)

        self.PackageViewTreeView.setItemDelegate(packageViewDelegate)
        # end_time = timer()
        # run_time = end_time - start_time
        # print(f"delegate setup time: {run_time}")

    def setupModelData(self, data, application, treeview, package_manager):
        # start_time = timer()
        data_model =  PackageDefinitionModel(
            application=application,
            parent_widget=treeview, 
            data=data)

        treeview.setModel(data_model)
        
        # end_time = timer()
        # run_time = end_time - start_time
        # print(f"model setup time: {run_time}")
        # self.setupFinished()

    def appendModelData(self, definition_data):
        # start_time = timer()
        data_model = self.PackageViewTreeView.model()
        data_model.appendModelData(definition_data)
        data_model.layoutChanged.emit()
        # end_time = timer()
        # run_time = end_time - start_time
        # print(f"model update time: {run_time}")

    def addExecutionPlan(self):
        tabwidget = ExecutionPlannerWidget(self, self.application)
        tabwidget.plannerNameChanged.connect(self.setPlannerName)
        self.uiRefreshRequested.connect(tabwidget.refresh_ui)
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
        contextMenu.editXMLTemplate.connect(self.onEditXMLTemplates)
        contextMenu.savePackageDefinition.connect(self.savePackageDefinition)
        contextMenu.collapseTree.connect(lambda source_index: self.toggleTreeStructure(True, source_index))
        contextMenu.expandTree.connect(lambda source_index: self.toggleTreeStructure(False, source_index))
        contextMenu.editSelectedItems.connect(self.onEditSelectedItems)
        contextMenu.sortChildItems.connect(self.onSortChildItems)
        contextMenu.reapplyTemplates.connect(self.onReapplyTemplates)
        contextMenu.deleteSelectedItems.connect(self.onDeleteSelectedItems)

        if len(contextMenu.menu_items) > 0:
            contextMenu.popup(menu_target)

    def addPackageDefinition(self):
        if not self.current_workdir:
            MsgBox(
                application=self.application, 
                window_title="Working Directory not set",
                message="Working Directory is not configured.\n\nPlease configure working directory location first to create any package definition.\n\nWithout working directory, program will not be able to generate the paths and save the files.")
            if not self.changeWorkingDirectory():
                return False
        
        form_data = self.application.getObjectData("PackageManager_PackageDefinition", "Add Package Definition")
        if form_data:
            treeview_model = self.PackageViewTreeView.model()
            if treeview_model:
                treeview_model.insert_item("PackageManager_PackageDefinition", form_data)

    def onEditXMLTemplates(self, source_index):
        self.editXMLTemplate(source_index)
        for selected_index in self.PackageViewTreeView.selectedIndexes():
            if selected_index != source_index and selected_index.isValid():
                selected_item = selected_index.internalPointer()
                if selected_item.task_class == "PackageManager_TaskDefinition" and selected_item.is_transport:
                    self.editXMLTemplate(selected_index)

    def onEditSelectedItems(self, source_index):
        if not source_index.isValid():
            return False
        selected_items = self.selectedItems()
        if len(selected_items) == 0:
            return False

        source_item = source_index.internalPointer()
        form_data = MultiObjectEditorForm(self.application, source_item.task_class)
        if form_data.exec():
            selected_columns = form_data.selectedColumns()
            if len(selected_columns) > 0:
                form_data = self.application.getObjectData(source_item.task_class, "Edit Selected Items", source_index, selected_columns)
                if form_data:
                    for selected_row in selected_items:
                        if selected_row.task_class == source_item.task_class:
                            selected_row.update_data(form_data)

    def onReapplyTemplates(self, source_index):
        source_item = None
        if source_index.isValid():
            source_item = source_index.internalPointer()
            if source_item:
                source_item.configureSourceColumns()

        selected_items = self.selectedItems()
        if len(selected_items) > 0:
            for selected_item in selected_items:
                selected_item.configureSourceColumns()

    def editPackageDefinition(self, source_index):
        # print("Edit Package Definition", source_index)
        if not source_index.isValid():
            return False

        form_data = self.application.getObjectData("PackageManager_PackageDefinition", "Edit Package Definition", source_index)
        if form_data:
            source_item = source_index.internalPointer()
            source_item.update_data(form_data)
            # source_item.configureSourceColumns()

    def savePackageDefinition(self, source_index, save_single=False):
        if not self.current_workdir:
            MsgBox(
                application=self.application,
                window_title="Working Directory not set",
                message="Working directory is not set. Please configure the work location first.")
            return False

        source_item = None
        selected_items = self.selectedItems()
        if len(selected_items) > 1 and not save_single:
            package_count = len([x for x in selected_items if x.task_class == 'PackageManager_PackageDefinition'])
            question = MsgBox(self.application, 
                message=f"Do you want to save all of the selected Packages? <br/> ({package_count} package definition(s) selected) <br/> Existing files will be overwritten.",
                window_mode=MsgBox.QUESTION)
        
            if question.accepted:
                for selected_item in selected_items:
                    if selected_item.task_class == "PackageManager_PackageDefinition":
                        selected_item.save()
        
        
        if source_index.isValid() and save_single:
            source_item = source_index.internalPointer()
            if source_item.task_class == "PackageManager_PackageDefinition":
                question = MsgBox(self.application, 
                        message=f"Are you sure to save the selected Package? <br/> ({source_item.display}) <br/> Existing file will be overwritten.",
                        window_mode=MsgBox.QUESTION)
        
                if question.accepted:
                    source_item.save()

                if save_single:
                    return
        
    def onSortChildItems(self, source_index):
        if not source_index.isValid():
            return False

        source_item = None
        if source_index.isValid():
            source_item = source_index.internalPointer()
            if source_item.task_class == "PackageManager_PackageDefinition":
                source_item.sortChildItems()

        selected_items = self.selectedItems()
        if len(selected_items) > 0:
            for selected_item in selected_items:
                if selected_item.task_class == "PackageManager_PackageDefinition" and selected_item != source_item:
                    selected_item.sortChildItems()

    def addTaskDefinition(self, source_index):
        # print("add task definition for", source_index)
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
            # source_item.configureSourceColumns()

    def editXMLTemplate(self, source_item):
        source_item = source_item.internalPointer()
        file_path = source_item.get_file_path()
        if not file_path.is_file():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.touch()
        self.application.XMLTemplateEditor.openXMLTemplate(str(file_path))

    def toggleTreeStructure(self, collapse_tree, source_index):
        selected_indexes = self.PackageViewTreeView.selectedIndexes()
        for index in selected_indexes:
            if collapse_tree:
                self.PackageViewTreeView.collapse(index)
            else:
                self.PackageViewTreeView.expandRecursively(index)

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

    def onDeleteSelectedItems(self, source_index):
        source_item=None
        if source_index.isValid():
            source_item = source_index.internalPointer()

        self.deletePackageDefinitions(source_item)

    def deletePackageDefinitions(self, definition_item=None):
        item_count = len(self.PackageViewTreeView.selectedIndexes())
        
        if item_count == 0 and definition_item is None:
            return True
        
        if item_count == 1 and definition_item:
            return self.deletePackageDefinition(definition_item)

        question = MsgBox(self.application, 
                        message=f"Do you want to delete all selected items? ({item_count} item(s))",
                        window_mode=MsgBox.QUESTION)
        
        if question.accepted:
            for item_index in self.PackageViewTreeView.selectedIndexes():
                item = item_index.internalPointer()
                self.deletePackageDefinition(item, False)
        return True

    def deletePackageDefinition(self, definition_item, confirm_deletion=True):
        files_to_delete = {}
        deletion_confirmed = not confirm_deletion
        if self.current_workdir:
            # attempt file operations only if the workdir is set
            files_to_delete = definition_item.get_all_files(recursive=True)
            if len(files_to_delete) > 0:
                export_data = "\n".join(map(str, files_to_delete))
                # export_data = json.dumps(files_to_delete, indent=4, separators=(',',':'))
                if confirm_deletion:
                    detailed_message = f"Data lookup returned following files related to the selected object:\n{export_data}"
                    question = MsgBox(self.application, 
                        window_title="Confirm Deletion",
                        message=f"Are you sure to delete item {definition_item.display}, its child items, and all related data files?", 
                        detailed_message=detailed_message, 
                        window_mode=MsgBox.QUESTION)

                    if not question.accepted:
                        return

                    deletion_confirmed = question.accepted

                if deletion_confirmed:
                    #delete data files
                    for file_path in files_to_delete:
                        self.deleteFile(file_path)
                    #remove item from model
                    self.PackageViewTreeView.model().remove_item(definition_item)
        else:
            #remove item from model
            self.PackageViewTreeView.model().remove_item(definition_item)
        

    def deleteFile(self, file_path):
        # print("file to delete", file_path)
        file_path = Path(str(file_path))
        if file_path.is_file():
            file_path.unlink()
            parent_directory = file_path.parent
            self.deleteDirectory(parent_directory)

    def deleteDirectory(self, directory_path):
        # print("check if directory can be deleted:", directory_path)
        if not self.current_workdir:
            # do not delete anything if there is no working directory
            return False

        workdir_path = Path(str(self.current_workdir))
        if directory_path.absolute() <= workdir_path.absolute():
            # never go beyond the working directory
            # print("do not cross the working directory, breaking")
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

    def selectedItems(self):
        selected_items = []
        if not self.PackageViewTreeView.selectionModel():
            return selected_items

        selected_indexes = self.PackageViewTreeView.selectionModel().selectedRows()
        if len(selected_indexes) > 0:
            for index in selected_indexes:
                if not index.isValid():
                    continue
                item = index.internalPointer()
                if item and item not in selected_items:
                    selected_items.append(item)
        return selected_items

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
        # self.FindPackageButton = QtWidgets.QToolButton(self.verticalLayoutWidget_5)
        # self.FindPackageButton.setObjectName("FindPackageButton")
        # self.horizontalLayout_4.addWidget(self.FindPackageButton)
        self.AddPackageButton = QtWidgets.QToolButton(self.verticalLayoutWidget_5)
        self.AddPackageButton.setObjectName("AddPackageButton")
        
        add_object_icon = self.ProgramConfiguration.getIcon("AddObject")
        if add_object_icon:
            self.AddPackageButton.setText("")
            self.AddPackageButton.setToolTip("<i>Add New Object..</i>")
            self.AddPackageButton.setIcon(add_object_icon)
            self.AddPackageButton.setProperty("PackageManager", "PackageManagerIcon")
            self.AddPackageButton.setIconSize(QtCore.QSize(20,20))

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
        self.PackageViewTreeView.setProperty("PackageManager", "PackageManagerTreeView")
        self.verticalLayout_5.addWidget(self.PackageViewTreeView)
        self.ExecutionPlannerTabWidget = QtWidgets.QTabWidget(self.PackageManagerSplitter)
        self.ExecutionPlannerTabWidget.setTabsClosable(False)
        self.ExecutionPlannerTabWidget.setMovable(True)
        self.ExecutionPlannerTabWidget.setObjectName("ExecutionPlannerTabWidget")
        self.ExecutionPlannerTabWidget.tabBar().setObjectName("ExecutionPlannerTabWidget")
        self.gridLayout.addWidget(self.PackageManagerSplitter, 0, 0, 1, 1)

        self.retranslateUi(self)
        self.ExecutionPlannerTabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.SearchPackageLineEdit.setToolTip(_translate("Form", "Search Transport Package"))
        self.SearchPackageLineEdit.setPlaceholderText(_translate("Form", "Search Transport Package"))
        # self.FindPackageButton.setText(_translate("Form", "Find"))
        self.AddPackageButton.setText(_translate("Form", "Add"))

class PMWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    dataChanged = QtCore.pyqtSignal(object)
    dataLoaded = QtCore.pyqtSignal(object)
    workdirLoaded = QtCore.pyqtSignal(list, list, list)

    def __init__(self, application, treeview, package_manager, definitions=None, workdir=None):
        super(PMWorker, self).__init__()
        self.workdir = workdir
        self.definitions = definitions
        self.application = application
        self.treeview = treeview
        self.package_manager = package_manager
        self.dataChanged.connect(self.modelDataChanged)
        self.isRunning = True
            
    def modelDataChanged(self, data):
        self.definitions = data
        # self.processQueue()

    def processQueue(self):
        while len(self.definitions) > 0:
            processQueueSize = self.application.ProgramConfiguration.getConfigurationValue("Package Manager", "ProcessQueueSize")
            if not processQueueSize or processQueueSize < 0:
                processQueueSize = 5
            # print("worker thread is running, processing the queue", len(self.definitions), "Process step:", processQueueSize)
            for i in range(0, processQueueSize):
                self.loadSingleDefinition()
            sleep(0.1)
        self.finished.emit()
        # self.application.statusBarUpdated.emit(f"All Definition files loaded")

    def loadSingleDefinition(self):
        if self.definitions and len(self.definitions) > 0:
            self.dataLoaded.emit(self.definitions[0])
            self.definitions.remove(self.definitions[0])
        
    def loadWorkingDirectory(self):
        workdir = self.workdir
        start_time = timer()
        sort_attribute = ""
        package_definition_config = self.application.getConfigurationParameters("PackageManager_PackageDefinition")
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
                    if column_configuration.get("IsMandatory", False) == True:
                        mandatory_columns.append(column)
        sort_attribute = sort_attribute.strip()
        
        workdir_path = Path(workdir).absolute()
        definitions = []
        skipped_definitions = []
        whitelist_directories = self.application.getConfigurationValue("Package Manager", "WorkdirDirectoryWhitelist")
        blacklist_directories = self.application.getConfigurationValue("Package Manager", "WorkdirDirectoryBlacklist")
        excluded_files = self.application.getConfigurationValue("Package Manager", "ExcludedFiles")
        definition_config = self.application.getConfigurationKey("PackageManager_PackageDefinition", "DefinitionFile")
        files_list = list(Path(workdir).rglob( '*.json' ))
        
        i = 1
        for file_path in files_list:
            self.application.statusBarUpdated.emit(f"loading workspace file {i} out of {len(files_list)}")
            i += 1
            # sleep(0.1)
            if file_path.is_file():
                feature_definition_location = file_path.relative_to(workdir_path)
                accept = True
                if whitelist_directories:
                    accept = False
                    for directory in whitelist_directories:
                        # print(f"checking whitelist, {str(feature_definition_location)} compared with whitelist directory: {directory}", str(feature_definition_location).lower().startswith(directory.lower()))
                        test_path = Path(directory)
                        if str(feature_definition_location).lower().startswith(str(test_path).lower()):
                            accept = True

                if excluded_files and accept:
                    for excluded_file_path in excluded_files:
                        test_path = Path(excluded_file_path)
                        if str(test_path) == str(feature_definition_location):
                            accept = False
                
                if blacklist_directories and accept:
                    if blacklist_directories:
                        for directory in blacklist_directories:
                            test_path = Path(directory)
                            if str(feature_definition_location).lower().startswith(str(test_path).lower()):
                                accept = False
                if not accept:
                    # program configuration excluded the file, continue
                    continue
                
                #file went through the whitelist/blacklist configurations
                json_content = self.application.load_file(file_path.absolute())
                package_definition = None
                try:
                    package_definition = json.loads(json_content)
                except json.JSONDecodeError:
                    accept = False
                    skipped_definitions.append(str(feature_definition_location))
                
                # file is still ok to be used
                # print(package_definition, str(feature_definition_location))
                if package_definition and isinstance(package_definition, dict):
                    #keep relative path by default
                    package_definition["DefinitionFile"] = str(feature_definition_location)

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
                
                if accept and isinstance(package_definition, dict) and len(package_definition) > 0:
                    if len(sort_attribute) > 0 and sort_attribute not in package_definition.keys():
                        package_definition[sort_attribute] = -1

                    definitions.append(package_definition)
                else:
                    skipped_definitions.append(str(feature_definition_location))
        
        if len(sort_attribute) > 0:
            definitions = sorted(
                    definitions, 
                    key=lambda d: (d.get(sort_attribute, ""))
                    )
        end_time = timer()
        run_time = timedelta(seconds=end_time - start_time)
        # print(f"workdir reading time: {run_time}")
        self.application.statusBarUpdated.emit(f"workspace files loading time: {run_time}, starting definition files processing...")
        # print("task definitions loaded", len(definitions), definitions)
        # sleep(2)
        self.definitions = definitions
        self.workdirLoaded.emit(definitions, skipped_definitions, mandatory_columns)
        self.processQueue()

    