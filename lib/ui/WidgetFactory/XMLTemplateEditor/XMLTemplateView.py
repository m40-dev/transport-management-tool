from PyQt6.QtCore import QObject, pyqtSignal, QTimer

#""" Required QT Libraries """
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QTreeWidget, QAbstractItemView, QTreeWidgetItemIterator, 
    QFileDialog
    )
from .ContextMenu import XMLObjectContextMenu
# XML Management
from .xml import *
from pathlib import Path
from .TreeWidgets import *

XML_PREVIEW_TIMER = 100

class XMLTemplateView(QObject):
    xml_structure_changed = pyqtSignal()

    def __init__(self, parent, application):
        super().__init__()
        self.parent = parent
        self.application = application
        self.XMLTemplateEditor = parent
        self.current_file = None
        self.xml_structure_widgets = []

        self.xml_preview_timer = QTimer(self)
        self.xml_preview_timer.setSingleShot(True)
        self.xml_preview_timer.timeout.connect(self.load_xml_preview)

        self.xml_structure_changed.connect(self.reload_xml_preview)

    def newTransportTemplate(self, file_path=None):
        if file_path:
            self.setCurrentXMLTemplate(file_path)
        self.transport_template = transport_template(self)
        self.reload_xml_structure()
        self.xml_structure_changed.emit()

    def openXMLTemplate(self, file_path=None):
        if file_path is None:
            dialog = QFileDialog(self, "Open existing template file")
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

            file_path = dialog.getOpenFileName(filter="*.xml")
            file_path = file_path[0]

        if file_path:
            self.transport_template.parse_xml_file(file_path)
            self.setCurrentXMLTemplate(file_path)

        self.application.ui.MainTabWidget.setCurrentWidget(self.XMLTemplateEditor)
        self.xml_structure_changed.emit()

    def saveXMLTemplate(self):
        if self.current_file is not None:
            # print(Path(self.current_file), Path(self.current_file).is_file())
            if Path(self.current_file).is_file():
                Path(self.current_file).parent.mkdir(parents=True, exist_ok=True)
                with open(self.current_file, 'w') as doc:
                    doc.write(self.transport_template.string)
                return self.current_file
            return self.saveXMLTemplateAs(self.current_file)
        return self.saveXMLTemplateAs(self.application.current_workdir)

    def saveXMLTemplateAs(self, initial_directory=None):
        dialog = QFileDialog(self, "Save As")
        dialog.setFileMode(QFileDialog.FileMode.AnyFile) 

        file_path = dialog.getSaveFileName(
            filter="*.xml", 
            directory=str(initial_directory))

        if file_path[0] != "":
            with open(file_path[0], 'w') as doc:
                doc.write(self.transport_template.string)
            self.setCurrentXMLTemplate(file_path[0])
            return file_path[0]
        return False

    def setCurrentXMLTemplate(self, file_path):            
        self.current_file = None
        if file_path:
            self.current_file = file_path
        self.XMLTemplateEditor.current_file_label.setText(str(file_path))

    """ XML Structure Management """
    def xmlContextMenuRequested(self, menuPosition):
        clickedItem = self.XMLTemplateEditor.XMLStructureTreeWidget.itemAt(menuPosition)
        contextMenu = XMLObjectContextMenu(
            parent=self, 
            source_widget_item=clickedItem)
        
        contextMenu.list_related_objects.connect(lambda: self.list_related_objects(
            source_widget_item = clickedItem, 
            override = True))
        contextMenu.load_object_from_database.connect(
            lambda: self.load_objects_from_database(source_widget_item=clickedItem))
        
        contextMenu.save_relation_preset.connect(
            lambda: self.XMLTemplateEditor.DatabaseRelations.save_relation_preset(source_widget_item=clickedItem))
        
        contextMenu.add_transport_task.connect(self.add_transport_task)
        contextMenu.edit_sql_script.connect(self.edit_sql_script)
        contextMenu.add_sql_script.connect(self.add_sql_script)

        if len(contextMenu.menu_items) > 0:
            menu_target = self.XMLTemplateEditor.XMLStructureTreeWidget.mapToGlobal(menuPosition)
            contextMenu.popup(menu_target)

    def reload_xml_preview(self):
        self.xml_preview_timer.start(XML_PREVIEW_TIMER)

    def load_xml_preview(self):
        self.XMLTemplateEditor.XMLEditorWidget.setText(self.transport_template.string)

    def xml_structure_move_event(self, event):
        move_accept = True
        source_widget_item = event.source().currentItem()

        QTreeWidget.dragMoveEvent(self.XMLTemplateEditor.XMLStructureTreeWidget, event)

        dropItem = self.XMLTemplateEditor.XMLStructureTreeWidget.itemAt(event.position().toPoint())
        dropIndicator = self.XMLTemplateEditor.XMLStructureTreeWidget.dropIndicatorPosition()
        
        if dropItem is not None:
            self.XMLTemplateEditor.XMLStructureTreeWidget.setDropIndicatorShown(True)

        if dropIndicator == QAbstractItemView.DropIndicatorPosition.OnItem:
            if isinstance(dropItem, TE_ObjectContainer_TreeWidgetItem):
                move_accept = False

            if isinstance(dropItem, TE_Table_TreeWidgetItem):
                move_accept = False
            
            if isinstance(dropItem, TE_ObjectContainerData_TreeWidgetItem):
                move_accept = False

            if (isinstance(dropItem, TE_TransportTask_TreeWidgetItem) 
                and isinstance(source_widget_item, TE_TransportTask_TreeWidgetItem)):
                move_accept = False

        if dropIndicator == QAbstractItemView.DropIndicatorPosition.BelowItem:
            if isinstance(dropItem, TE_TransportTask_TreeWidgetItem):
                move_accept = False

        if not move_accept:
            event.ignore()

        QTreeWidget.dragMoveEvent(self.XMLTemplateEditor.XMLStructureTreeWidget, event)

    def xml_structure_drop_event(self, event):
        event.setDropAction(Qt.DropAction.MoveAction)
        QTreeWidget.dropEvent(self.XMLTemplateEditor.XMLStructureTreeWidget, event)
        # event.accept()
        self.reset_xml_order()
    
    def reset_xml_order(self):
        self.transport_template.clear_xml_tasks()
        iterator = QTreeWidgetItemIterator(self.XMLTemplateEditor.XMLStructureTreeWidget, QTreeWidgetItemIterator.IteratorFlag.Selectable)
        current_task_data = None
        while iterator.value():
            
            item = iterator.value()
            iterator += 1
            if isinstance(item, TE_TransportTask_TreeWidgetItem) and item.xml_object is not None:
                item.xml_object.delete_child_items()
                current_task_data = item.xml_object.data
                self.transport_template.tasks_root.append(item.xml_object.data)
                continue
            
            if (isinstance(item, TemplateEditorTreeWidgetItem) 
                and isinstance(item.xml_object, transport_template_custom_object)):
                container_xml = item.xml_object
                item.xml_object = container_xml
                if container_xml is not None:
                    if container_xml.description is not None and current_task_data is not None:
                        current_task_data.append(container_xml.description)
                    current_task_data.append(container_xml.data)
            
        self.xml_structure_changed.emit()

    def reload_xml_structure(self):
        """ reload structure according to the xml structure data """
        self.XMLTemplateEditor.XMLStructureTreeWidget.clear()
        self.xml_structure_widgets = []
        task_treewidget_item = None
        for task in self.transport_template.tasks:
            if task.task_class == "VI.Transport.ObjectTransport, VI.Transport":
                task_treewidget_item = TE_ObjectTransportTask_TreeWidgetItem(
                    self.XMLTemplateEditor,
                    self.application, 
                    object_data=None, 
                    xml_object=task)
                self.xml_structure_widgets.append(task_treewidget_item)
                for task_container_xml in task.task_containers:
                    container_element = object_container(
                        self, 
                        source_element=task_container_xml)
                    
                    object_container_widget = TE_ObjectContainer_TreeWidgetItem(
                        self.XMLTemplateEditor,
                        self.application, 
                        object_data=None, 
                        xml_object=container_element)
                    
                    task_treewidget_item.addChild(object_container_widget)
                    self.xml_structure_widgets.append(object_container_widget)

            if task.task_class == "VI.Transport.SQLTransport, VI.Transport":
                task_treewidget_item = TE_SQLTransportTask_TreeWidgetItem(
                    self.XMLTemplateEditor, 
                    object_data=None, 
                    xml_object=task)
                self.xml_structure_widgets.append(task_treewidget_item)
                for task_container_xml in task.task_containers:
                    container_element = sql_script_container(
                        self,
                        source_element=task_container_xml)
                    
                    if container_element.script_type != "PreImport":
                        object_container_widget = TE_SQLScriptContainer_TreeWidgetItem(
                            self.XMLTemplateEditor,
                            self.application,
                            object_data=None, 
                            xml_object=container_element)
                        task_treewidget_item.addChild(object_container_widget)
                        self.xml_structure_widgets.append(object_container_widget)

            if task_treewidget_item is None:
                task_treewidget_item = TE_TransportTask_TreeWidgetItem(
                    self.XMLTemplateEditor, 
                    self.application, 
                    object_data=None, 
                    xml_object=task)
                self.xml_structure_widgets.append(task_treewidget_item)

            if task_treewidget_item:
                self.XMLTemplateEditor.XMLStructureTreeWidget.addTopLevelItem(task_treewidget_item)
                task_treewidget_item.setExpanded(True)

    """ SQL Script tasks handling """
    def add_sql_script(self, source_widget_item, script_type):
        if isinstance(source_widget_item, TE_SQLTransportTask_TreeWidgetItem):
            source_widget_item.add_script(script_type)
            self.xml_structure_changed.emit()

    def edit_sql_script(self, source_widget_item):
        dialog = DialogScreens.ScriptEditorDialog(self, source_widget_item.script)
        if dialog.exec():
            source_widget_item.set_script(dialog.script)
            self.xml_structure_changed.emit()

    def add_transport_task(self, task_type):
        """ Create XML Node """

        task = self.transport_template.add_transport_task(task_type)
        task_item = None

        if task_type == "VI.Transport.ObjectTransport, VI.Transport":
            task_item = TE_ObjectTransportTask_TreeWidgetItem(self.XMLTemplateEditor, self.application, task, task)
        elif task_type == "VI.Transport.SQLTransport, VI.Transport":
            task_item = TE_SQLTransportTask_TreeWidgetItem(self.XMLTemplateEditor, self.application, task, task)
        else:
            task_item = TE_TransportTask_TreeWidgetItem(self.XMLTemplateEditor, self.application, task, task)

        self.XMLTemplateEditor.XMLStructureTreeWidget.addTopLevelItem(task_item)
        self.xml_structure_widgets.append(task_item)

        self.xml_structure_changed.emit()
        return task_item
    
    """ Object Loading and Listing  """
    def list_related_objects(self, source_widget_item, override=False):
        tree_widget = self.XMLTemplateEditor.XMLStructureTreeWidget
        for element in tree_widget.selectedItems():
            if isinstance(element, TE_ObjectContainer_TreeWidgetItem):
                element.list_related_objects(True)
        
        if len(tree_widget.selectedItems()) == 0:
            source_widget_item.list_related_objects(True)

    def load_objects_from_database(self, source_widget_item):
        tree_widget = self.XMLTemplateEditor.XMLStructureTreeWidget
        for element in tree_widget.selectedItems():
            if isinstance(element, TE_ObjectContainer_TreeWidgetItem):
                element.load_from_database()
        
        if len(tree_widget.selectedItems()) == 0:
            source_widget_item.load_from_database()