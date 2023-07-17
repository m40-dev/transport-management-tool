from PyQt6.QtCore import QObject, pyqtSignal

#""" Required QT Libraries """
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog
    )

# XML Management
from .xml_object_definitions import *
from pathlib import Path

XML_PREVIEW_TIMER = 100

class XMLTemplateView(QObject):
    xml_structure_changed = pyqtSignal()

    def __init__(self, parent, application):
        super().__init__()
        self.parent = parent
        self.application = application
        self.XMLTemplateEditor = parent

    def reload_xml_preview(self):
        self.xml_preview_timer.start(XML_PREVIEW_TIMER)

    def load_xml_preview(self):
        self.XMLTemplateEditor.XMLEditorWidget.setText(self.transport_template.string)
    
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