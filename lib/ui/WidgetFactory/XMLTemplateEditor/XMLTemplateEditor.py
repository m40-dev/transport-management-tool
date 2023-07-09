from PyQt6 import QtCore, QtWidgets
from ..CodeEditors import xml_editor
from .TreeWidgets import *

#""" Required QT Libraries """
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QTreeWidget, QAbstractItemView, QTreeWidgetItemIterator, 
    QFileDialog
    )
from .ContextMenu import RelationContextMenu, XMLObjectContextMenu
# XML Management
from lib.xml.transport_template import transport_template
from lib.xml.transport_template_custom_object import transport_template_custom_object
from lib.xml.object_container import object_container
from lib.xml.sql_script_container import sql_script_container

XML_PREVIEW_TIMER = 100

class XMLTemplateEditor(QtWidgets.QWidget):
    xml_structure_changed = QtCore.pyqtSignal()

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.current_file = None
        self.xml_structure_widgets = []

        """ Saved relation presets data """
        self.relation_presets = self.application.settings.value("relation_presets")
        if self.relation_presets is None:
            self.relation_presets = {}

        self.setupUi()

        self.FindObjectButton.clicked.connect(self.find_objects)
        self.TableComboBox.currentTextChanged.connect(self.load_db_objects)
        self.AddSelectedObjectsWithRelationsButton.clicked.connect(self.select_object_for_transport)
        self.SearchResultsListWidget.itemClicked.connect(self.select_source_object)
        self.XMLStructureTreeWidget.itemClicked.connect(self.select_source_object)
        self.RelationsViewTreeWidget.itemChanged.connect(self.handle_data_change)
        self.XMLStructureTreeWidget.itemChanged.connect(self.handle_data_change)
        self.XMLStructureTreeWidget.dragMoveEvent = self.xml_structure_move_event
        self.XMLStructureTreeWidget.dropEvent = self.xml_structure_drop_event
        
        self.DeselectAllToolButton.clicked.connect(self.deselect_all_relations)
        self.AddAsSingleObjectsButton.clicked.connect(
            lambda: self.select_object_for_transport(add_without_relations=True))
        self.ApplyPresetToolButton.clicked.connect(self.apply_table_relation_preset)

        """ Context Menu """
        self.RelationsViewTreeWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.XMLStructureTreeWidget.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.RelationsViewTreeWidget.customContextMenuRequested.connect(self.relationContextMenuRequested)
        self.XMLStructureTreeWidget.customContextMenuRequested.connect(self.xmlContextMenuRequested)

        self.xml_structure_changed.connect(self.reload_xml_preview)
        self.xml_preview_timer = QtCore.QTimer(self)
        self.xml_preview_timer.setSingleShot(True)
        self.xml_preview_timer.timeout.connect(self.load_xml_preview)

        self.current_workdir = None
        self.current_file = None
        self.xml_structure_widgets = []
        self.relation_presets

    def refresh_ui(self):
        self.XMLEditorWidget.reconfigure_editor()

    def find_objects(self):
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

    """ Object Loading and Listing  """
    def list_related_objects(self, source_widget_item, override=False):
        tree_widget = self.XMLStructureTreeWidget
        for element in tree_widget.selectedItems():
            if isinstance(element, TE_ObjectContainer_TreeWidgetItem):
                element.list_related_objects(True)
        
        if len(tree_widget.selectedItems()) == 0:
            source_widget_item.list_related_objects(True)

    def load_objects_from_database(self, source_widget_item):
        tree_widget = self.XMLStructureTreeWidget
        for element in tree_widget.selectedItems():
            if isinstance(element, TE_ObjectContainer_TreeWidgetItem):
                element.load_from_database()
        
        if len(tree_widget.selectedItems()) == 0:
            source_widget_item.load_from_database()

    def load_db_objects(self, table_name=None, data_rows=[]):
        self.SearchResultsListWidget.clear()

        if len(data_rows) == 0 and table_name: 
            query = f"select * from {table_name}"
            data_rows = self.application.db.run_db_query(query)

        for row in data_rows:
            w = TemplateEditorListWidgetItem(self, self.application, row, table_name=table_name)
            self.SearchResultsListWidget.addItem(w)

        self.load_table_relation_presets(table_name)

    def get_objectkey_table(self, input_string):
        table_name = None
        regex = r"<T>(.*?)</T>"
        if input_string is not None:
            match = re.search(regex, input_string)
            if match:
                table_name = match.group(1)
        return table_name

    def load_table_relations(self, relations, source_widget_item, append_to_existing_widget=None):
        if append_to_existing_widget is None:
            self.RelationsViewTreeWidget.clear()

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
            
            child_widget = TE_RelationColumn_TreeWidgetItem(self, self.application, relation, source_widget_item=source_widget_item)
            
            if append_to_existing_widget is not None and ui_parent_table_name == append_to_existing_widget.follow_table:
                if ui_parent_table_name not in tree_widgets.keys():
                    tree_widgets[ui_parent_table_name] = append_to_existing_widget

            if ui_parent_table_name not in tree_widgets.keys():
                table_info = ui_parent_table_name
                if self.application.db:
                    table_info = self.application.db.table_info.get(ui_parent_table_name, ui_parent_table_name)
                parent_widget = TE_Table_TreeWidgetItem(self, self.application, table_info, source_widget_item=source_widget_item)
                tree_widgets[ui_parent_table_name] = parent_widget
            else:
                parent_widget = tree_widgets[ui_parent_table_name]
            

            """ Connect main application signals """
            self.ShowAllColumnsCheckBox.stateChanged.connect(child_widget.show_relation)
            # self.SelectWithDatabaseModelCheckBox.stateChanged.connect(child_widget.select_relations_using_db_model)

            parent_widget.addChild(child_widget)
            # child_widget.show_relation(self.ShowAllColumnsCheckBox.isChecked())

        for parent_widget in tree_widgets.values():
            if parent_widget.childCount() > 0:
                if isinstance(append_to_existing_widget, TemplateEditorTreeWidgetItem):
                    append_to_existing_widget.addChild(parent_widget)
                    continue
                self.RelationsViewTreeWidget.addTopLevelItem(parent_widget)

        self.RelationsViewTreeWidget.sortItems(0, Qt.SortOrder.AscendingOrder)

        self.ShowAllColumnsCheckBox.stateChanged.emit(int(self.ShowAllColumnsCheckBox.isChecked()))

        table_widget = tree_widgets.get(source_widget_item.table_name, None)

        if isinstance(table_widget, TE_Table_TreeWidgetItem):
            table_widget.setExpanded(True)
    
    def newTransportTemplate(self, file_path=None):
        if file_path:
            self.set_current_file(file_path)
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
            self.set_current_file(file_path)

        self.application.ui.MainTabWidget.setCurrentWidget(self)
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
        return self.saveXMLTemplateAs(self.current_workdir)

    def saveXMLTemplateAs(self, initial_directory=None):
        dialog = QFileDialog(self, "Save As")
        dialog.setFileMode(QFileDialog.FileMode.AnyFile) 

        file_path = dialog.getSaveFileName(
            filter="*.xml", 
            directory=str(initial_directory))

        if file_path[0] != "":
            with open(file_path[0], 'w') as doc:
                doc.write(self.transport_template.string)
            self.set_current_file(file_path[0])
            return file_path[0]
        return False

    def set_current_file(self, file_path):            
        self.current_file = None
        if file_path:
            self.current_file = file_path
        self.current_file_label.setText(str(file_path))

    """ Relations Management """
    def relationContextMenuRequested(self, menuPosition):
        clickedItem = self.RelationsViewTreeWidget.itemAt(menuPosition)
        if clickedItem:
            contextMenu = RelationContextMenu(self, clickedItem)
            contextMenu.follow_table_relations.connect(self.follow_table_relation)
            menu_target = self.RelationsViewTreeWidget.mapToGlobal(menuPosition)
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
        list_widgets = [self.XMLStructureTreeWidget, self.SearchResultsListWidget]
        select_element = None
        for selected_widget in list_widgets:
            if self.last_widget_clicked == selected_widget:
                for element in selected_widget.selectedItems():
                    if isinstance(element, (TE_ObjectContainer_TreeWidgetItem, TemplateEditorListWidgetItem)):
                        element.set_all_relations_state(0)
                        select_element = element

        if select_element is not None:
            self.select_source_object(select_element)

    def save_relation_preset(self, source_widget_item):
        relation_dialog = DialogScreens.RelationPresetDialog(self)
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

        self.settings.setValue("relation_presets", self.relation_presets)

    def load_table_relation_presets(self, table_name):
        self.RelationPresetsComboBox.clear()

        table_presets = self.relation_presets.get(table_name, None)
        if table_presets is not None:
            for preset_name, preset_data in table_presets.items():
                self.RelationPresetsComboBox.addItem(preset_name)
    
    def apply_table_relation_preset(self):
        preset_name = self.RelationPresetsComboBox.currentText()
        preset_data = None
        preset_table = None
        for table_name, relations in self.relation_presets.items():
            preset_data = relations.get(preset_name, None)
            if preset_data is not None:
                preset_table = table_name
                break
    
        if preset_data:
            if self.last_widget_clicked == self.XMLStructureTreeWidget:
                for element in self.XMLStructureTreeWidget.selectedItems():
                    if isinstance(element, TE_ObjectContainer_TreeWidgetItem) and element.table_name == preset_table:
                        preset_data_relations = copy.deepcopy(preset_data["table_relations"])
                        element.set_object_relations(preset_data_relations)
                        self.select_source_object(element)
            
            if self.last_widget_clicked == self.SearchResultsListWidget:
                for element in self.SearchResultsListWidget.selectedItems():
                    if isinstance(element, TemplateEditorListWidgetItem) and element.table_name == preset_table:
                        preset_data_relations = copy.deepcopy(preset_data["table_relations"])
                        element.set_object_relations(preset_data_relations)
                        self.select_source_object(element)

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

    """ XML Structure Management """
    def xmlContextMenuRequested(self, menuPosition):
        clickedItem = self.XMLStructureTreeWidget.itemAt(menuPosition)
        contextMenu = XMLObjectContextMenu(
            parent=self, 
            source_widget_item=clickedItem)
        
        contextMenu.list_related_objects.connect(lambda: self.list_related_objects(
            source_widget_item = clickedItem, 
            override = True))
        contextMenu.load_object_from_database.connect(
            lambda: self.load_objects_from_database(source_widget_item=clickedItem))
        
        contextMenu.save_relation_preset.connect(
            lambda: self.save_relation_preset(source_widget_item=clickedItem))
        
        contextMenu.add_transport_task.connect(self.add_transport_task)
        contextMenu.edit_sql_script.connect(self.edit_sql_script)
        contextMenu.add_sql_script.connect(self.add_sql_script)

        if len(contextMenu.menu_items) > 0:
            menu_target = self.XMLStructureTreeWidget.mapToGlobal(menuPosition)
            contextMenu.popup(menu_target)

    def reload_xml_preview(self):
        self.xml_preview_timer.start(XML_PREVIEW_TIMER)

    def load_xml_preview(self):
        self.XMLEditorWidget.setText(self.transport_template.string)

    def xml_structure_move_event(self, event):
        move_accept = True
        source_widget_item = event.source().currentItem()

        QTreeWidget.dragMoveEvent(self.XMLStructureTreeWidget, event)

        dropItem = self.XMLStructureTreeWidget.itemAt(event.position().toPoint())
        dropIndicator = self.XMLStructureTreeWidget.dropIndicatorPosition()
        
        if dropItem is not None:
            self.XMLStructureTreeWidget.setDropIndicatorShown(True)

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

        QTreeWidget.dragMoveEvent(self.XMLStructureTreeWidget, event)

    def xml_structure_drop_event(self, event):
        event.setDropAction(Qt.DropAction.MoveAction)
        QTreeWidget.dropEvent(self.XMLStructureTreeWidget, event)
        # event.accept()
        self.reset_xml_order()
    
    def reset_xml_order(self):
        self.transport_template.clear_xml_tasks()
        iterator = QTreeWidgetItemIterator(self.XMLStructureTreeWidget, QTreeWidgetItemIterator.IteratorFlag.Selectable)
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
        self.XMLStructureTreeWidget.clear()
        self.xml_structure_widgets = []
        task_treewidget_item = None
        for task in self.transport_template.tasks:
            if task.task_class == "VI.Transport.ObjectTransport, VI.Transport":
                task_treewidget_item = TE_ObjectTransportTask_TreeWidgetItem(
                    self,
                    self.application, 
                    object_data=None, 
                    xml_object=task)
                self.xml_structure_widgets.append(task_treewidget_item)
                for task_container_xml in task.task_containers:
                    container_element = object_container(
                        self, 
                        source_element=task_container_xml)
                    
                    object_container_widget = TE_ObjectContainer_TreeWidgetItem(
                        self,
                        self.application, 
                        object_data=None, 
                        xml_object=container_element)
                    
                    task_treewidget_item.addChild(object_container_widget)
                    self.xml_structure_widgets.append(object_container_widget)

            if task.task_class == "VI.Transport.SQLTransport, VI.Transport":
                task_treewidget_item = TE_SQLTransportTask_TreeWidgetItem(
                    self, 
                    object_data=None, 
                    xml_object=task)
                self.xml_structure_widgets.append(task_treewidget_item)
                for task_container_xml in task.task_containers:
                    container_element = sql_script_container(
                        self,
                        source_element=task_container_xml)
                    
                    if container_element.script_type != "PreImport":
                        object_container_widget = TE_SQLScriptContainer_TreeWidgetItem(
                            self,
                            self.application,
                            object_data=None, 
                            xml_object=container_element)
                        task_treewidget_item.addChild(object_container_widget)
                        self.xml_structure_widgets.append(object_container_widget)

            if task_treewidget_item is None:
                task_treewidget_item = TE_TransportTask_TreeWidgetItem(
                    self, self.application, object_data=None, xml_object=task)
                self.xml_structure_widgets.append(task_treewidget_item)

            if task_treewidget_item:
                self.XMLStructureTreeWidget.addTopLevelItem(task_treewidget_item)
                task_treewidget_item.setExpanded(True)

    """ Custom Widget Operations """

    def handle_data_change(self, changed_widget, column):       
        if isinstance(changed_widget, TemplateEditorTreeWidgetItem):
            changed_widget.handle_data_change(column)
        self.xml_structure_changed.emit()

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
                self.reset_xml_order()
                self.xml_structure_changed.emit()

    def clear_widgets(self):
        self.TableComboBox.clear()
        self.TableFilter.clear()

    def reload_ui(self):
        if self.application.db.is_connected:
            self.FindObjectButton.setEnabled(True)
            self.TableComboBox.setEnabled(True)

        self.TableComboBox.clear()
        for table_name in self.application.db.table_info.keys():
            self.TableComboBox.addItem(table_name)

    def select_source_object(self, source_widget_item):
        if isinstance(source_widget_item, TemplateEditorListWidgetItem):
            self.last_widget_clicked = source_widget_item.listWidget()
        
        if isinstance(source_widget_item, TE_ObjectContainer_TreeWidgetItem):
            self.last_widget_clicked = source_widget_item.treeWidget()

        if isinstance(source_widget_item, TE_ObjectContainer_TreeWidgetItem) or isinstance(source_widget_item, TemplateEditorListWidgetItem):
            relations = source_widget_item.object_relations
            self.RelationsViewTreeWidget.clear()

            if relations is not None:
                self.load_table_relations(relations, source_widget_item)  

            if isinstance(source_widget_item, TE_ObjectContainer_TreeWidgetItem):
                self.XMLEditorWidget.find_text(source_widget_item.search_text)
            
            self.load_table_relation_presets(source_widget_item.table_name)

    def add_transport_task(self, task_type):
        """ Create XML Node """

        task = self.transport_template.add_transport_task(task_type)
        task_item = None

        if task_type == "VI.Transport.ObjectTransport, VI.Transport":
            task_item = TE_ObjectTransportTask_TreeWidgetItem(self, self.application, task, task)
        elif task_type == "VI.Transport.SQLTransport, VI.Transport":
            task_item = TE_SQLTransportTask_TreeWidgetItem(self, self.application, task, task)
        else:
            task_item = TE_TransportTask_TreeWidgetItem(self, self.application, task, task)

        self.XMLStructureTreeWidget.addTopLevelItem(task_item)
        self.xml_structure_widgets.append(task_item)

        self.xml_structure_changed.emit()
        return task_item
    
    def select_object_for_transport(self, add_without_relations=False):
        selected_source_widget_items = self.SearchResultsListWidget.selectedItems()
        if selected_source_widget_items is not None:
            selected_target_widgets = self.XMLStructureTreeWidget.selectedItems()
            task_item = None
            if len(selected_target_widgets) == 0:
                """ Create UI Node """
                task_item = self.add_transport_task("VI.Transport.ObjectTransport, VI.Transport")
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

                    self.xml_structure_widgets.append(object_container)

                    if add_without_relations:
                        object_container.set_all_relations_state(0)
                    
                    task_item.setExpanded(True)

        self.xml_structure_changed.emit()

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
