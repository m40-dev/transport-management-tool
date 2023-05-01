from PyQt6.QtWidgets import QWidget, QGridLayout, QTreeView, QAbstractItemView
from PyQt6.QtCore import Qt
from lib.data.DataModels import TaskExecutionModel
from .ExecutionPlannerDelegate import ExecutionPlannerDelegate

class ExecutionPlannerWidget(QWidget):
    def __init__(self, parent):
        super(ExecutionPlannerWidget, self).__init__()

        self.parent = parent
        self.application = parent

        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.treeview = QTreeView()

        self.layout.addWidget(self.treeview, 0, 0, 1, 1)

        data = [
            {
                "Name": "Group 1",
                "objectclass": "TaskGroup",
                "Description": "This Group have a description which might help organize things around. This Group have a description which might help organize things around.",
                "Tasks": [
                        {
                            "TaskName": "Task 1 Name",
                            "Order": 30,
                            "TaskType": "Transport/Schema/SQL/FeatureUpdate",
                            "DefinitionFile": "xml_template_filename.xml",
                            "ExportFile": "target_filename.zip",
                            "ExportFileHash": "",
                            "State": "Development",
                            "CompilerOption": "None/Full/NoWeb",
                            "Environment": "Any",
                            "AutoUpdate": "False",
                            "TestScript": ""
                        },
                        {
                            "TaskName": "Task 2 Name",
                            "Order": 40,
                            "TaskType": "Transport/Schema/SQL/FeatureUpdate",
                            "DefinitionFile": "xml_template_filename.xml",
                            "ExportFile": "target_filename.zip",
                            "ExportFileHash": "",
                            "State": "Development",
                            "CompilerOption": "None/Full/NoWeb",
                            "Environment": "Any",
                            "AutoUpdate": "False",
                            "TestScript": ""
                        }
                ]
            },
            {
                "Name": "Group 2",
                "objectclass": "TaskGroup",
                "Tasks": [
                        {
                            "Name": "Task 3",
                            "Type": "Import",
                            "objectclass": "TaskItem",
                            "Description": "Import task 3 Description"
                        },
                    {
                            "Name": "Task 4",
                            "objectclass": "TaskItem",
                            "Type": "Export",
                            "Description": "Export task 4 Description"
                        }
                ]
            }
        ]

        self.model_data = TaskExecutionModel(data)
        self.treeview.setModel(self.model_data)

        custom_item_delegate = ExecutionPlannerDelegate(self.model_data, parent=self.treeview)
        self.treeview.setItemDelegate(custom_item_delegate)

        self.treeview.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.treeview.setDragEnabled(True)
        self.treeview.setAcceptDrops(True)
        self.treeview.setDropIndicatorShown(True)
        self.treeview.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.treeview.dragMoveEvent = self.dragMoveEvent
        
        # self.treeview.setUniformRowHeights(True)
        self.treeview.setAlternatingRowColors(True)
        # self.treeview.setProperty("QTreeView::itemSpacing", 10)
        # self.treeview.setSortingEnabled(True)
        self.treeview.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        view_header = self.treeview.header()
        view_header.setStretchLastSection(True)

        # section_width = round(self.treeview.viewport().width() / view_header.count()) * 1.5
        # for i in range(0, view_header.count()):
        #     self.treeview.setColumnWidth(i, section_width)
    def changeData(self, col, row):
        print("data changed in ", col, row)
    def dragMoveEvent(self, event):
        move_accept = False
        source_index = event.source().currentIndex()
        source_item = source_index.internalPointer()

        QTreeView.dragMoveEvent(self.treeview, event)
        
        drop_index = self.treeview.indexAt(event.position().toPoint())
        drop_item = drop_index.internalPointer()

        dropIndicator = self.treeview.dropIndicatorPosition()

        # print("Drop Event:", drop_index, drop_item, source_index, source_item)

        if drop_item:
            self.treeview.setDropIndicatorShown(True)

        if dropIndicator == QAbstractItemView.DropIndicatorPosition.OnItem:

            if drop_item._task_class != source_item._task_class:
                move_accept = True
            
            if drop_item and source_item:
                #allow group nesting
                if source_item._task_class == "TaskGroup" and drop_item._task_class == "TaskGroup":
                    move_accept = True

        if dropIndicator in [QAbstractItemView.DropIndicatorPosition.BelowItem, QAbstractItemView.DropIndicatorPosition.AboveItem]:
            if drop_item._task_class == source_item._task_class:
                move_accept = True

        if drop_item is None:
            # no target item - drop at top level
            if source_item._task_class == "TaskGroup":
                move_accept = True

        if event.mimeData().hasFormat("application/vnd.jsondataitem") and move_accept:
            event.acceptProposedAction()
        else:
            event.ignore()


